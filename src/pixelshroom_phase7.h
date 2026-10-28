#pragma once
// Pixel Shroom Phase 7: read-only, modeless, sampled preview.
// All adjustment controls belong to Image Studio — none are duplicated here.
#include <QBuffer>
#include <QByteArray>
#include <QDialog>
#include <QFileInfo>
#include <QHBoxLayout>
#include <QImage>
#include <QImageReader>
#include <QImageWriter>
#include <QLabel>
#include <QMessageBox>
#include <QPixmap>
#include <QPushButton>
#include <QSizePolicy>
#include <QTimer>
#include <QString>
#include <QIODevice>
#include <QVBoxLayout>
#include <QtGlobal>
#include <Magick++.h>
#include <algorithm>
#include <stdexcept>

namespace PixelShroomPhase7 {

class PreviewWindow : public QDialog {
public:
    explicit PreviewWindow(QWidget *parent) : QDialog(parent) {
        setWindowTitle(tr("Pixel Shroom | Live output preview"));
        setMinimumSize(690, 500);
        resize(1000, 690);
        setModal(false);
        setStyleSheet(R"PS7(
            QDialog { background:#20252b; color:#eef4f7; }
            QLabel { color:#eef4f7; }
            QPushButton { background:#344550; color:#f6f8f9; border:1px solid #698093;
                          border-radius:4px; padding:7px 16px; }
        )PS7");
        auto *layout = new QVBoxLayout(this);
        m_heading = new QLabel(tr("Sampled preview — edit the settings in Image Studio"), this);
        m_heading->setWordWrap(true);
        layout->addWidget(m_heading);
        auto *panes = new QHBoxLayout();
        layout->addLayout(panes, 1);
        auto makePane = [this, panes](const QString &name) {
            auto *column = new QVBoxLayout();
            column->addWidget(new QLabel(name, this));
            auto *view = new QLabel(this);
            view->setAlignment(Qt::AlignCenter);
            view->setMinimumHeight(240);
            view->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
            view->setStyleSheet("background:#11171e; border:1px solid #566b78;");
            column->addWidget(view, 1);
            panes->addLayout(column, 1);
            return view;
        };
        m_before = makePane(tr("ORIGINAL SAMPLE"));
        m_after = makePane(tr("ADJUSTED / COMPRESSED SAMPLE"));
        m_summary = new QLabel(tr("Select an image to preview."), this);
        m_summary->setWordWrap(true);
        layout->addWidget(m_summary);
        auto *bottom = new QHBoxLayout();
        bottom->addStretch();
        auto *close = new QPushButton(tr("Close preview"), this);
        connect(close, &QPushButton::clicked, this, &QDialog::close);
        bottom->addWidget(close);
        layout->addLayout(bottom);
        m_timer = new QTimer(this);
        m_timer->setInterval(350);
        m_timer->setSingleShot(true);
        connect(m_timer, &QTimer::timeout, this, [this]() { render(); });
    }

    bool openSource(const QString &filePath) {
        const QFileInfo file(filePath);
        if (!file.isFile()) {
            QMessageBox::warning(this, tr("Missing original"),
                                 tr("File not found:\n%1").arg(filePath));
            return false;
        }
        if (file.absoluteFilePath() == m_path && !m_sample.isNull()) return true;
        QImageReader reader(file.absoluteFilePath());
        reader.setAutoTransform(true);
        const QSize imageSize = reader.size();
        if (imageSize.isValid()) reader.setScaledSize(imageSize.scaled(1000, 1000, Qt::KeepAspectRatio));
        const QImage sample = reader.read();
        if (sample.isNull()) {
            QMessageBox::warning(this, tr("Cannot read preview image"),
                                 tr("Could not open %1\n%2").arg(file.fileName(), reader.errorString()));
            return false;
        }
        m_sample = sample;
        m_originalSize = imageSize.isValid() ? imageSize : sample.size();
        m_path = file.absoluteFilePath();
        m_before->setPixmap(QPixmap::fromImage(m_sample).scaled(
            440, 410, Qt::KeepAspectRatio, Qt::SmoothTransformation));
        m_timer->start();
        return true;
    }

    void setParameters(QSize target, bool keepAspect, QString codec, bool custom,
                       int quality, double smoothing, double sharpen, bool webpLossless,
                       int pngCompression, int webpMethod, bool webpDithering) {
        m_target = target;
        m_keepAspect = keepAspect;
        m_codec = codec.toUpper();
        if (m_codec == "JPG" || m_codec == "JFIF") m_codec = "JPEG";
        m_quality = qBound(1, quality, 100);
        m_customQuality = custom;
        m_smoothing = qMax(0.0, smoothing);
        m_sharpening = qMax(0.0, sharpen);
        m_webpLossless = webpLossless;
        m_pngCompression = qBound(0, pngCompression, 9);
        m_webpMethod = qBound(0, webpMethod, 6);
        m_webpDithering = webpDithering;
        if (!m_sample.isNull()) m_timer->start();
    }

private:
    void render() {
        if (m_sample.isNull()) return;
        const QString codec = m_codec;
        if (codec != "JPEG" && codec != "WEBP" && codec != "PNG") {
            m_summary->setText(tr("Select JPEG, PNG or WebP in the main window to preview compression. "
                                  "Other formats can still be converted normally."));
            m_after->clear();
            return;
        }
        m_heading->setText(tr("Live sample | %1 | Original: %2 × %3 pixels | Editing in main Image Studio")
            .arg(codec).arg(m_originalSize.width()).arg(m_originalSize.height()));
        m_summary->setText(tr("Rendering adjusted sample..."));
        try {
            QImage scaled = m_sample;
            if (m_target.isValid()) {
                QSize previewTarget = m_target.scaled(1000, 1000, Qt::KeepAspectRatio);
                if (m_keepAspect)
                    previewTarget = m_sample.size().scaled(previewTarget, Qt::KeepAspectRatio);
                if (previewTarget.isValid())
                    scaled = m_sample.scaled(previewTarget, Qt::IgnoreAspectRatio,
                                             Qt::SmoothTransformation);
            }
            QByteArray sourceBytes;
            QBuffer buffer(&sourceBytes);
            if (!buffer.open(QIODevice::WriteOnly)) throw std::runtime_error("Sample buffer failed");
            QImageWriter writer(&buffer, "PNG");
            if (!writer.write(scaled)) throw std::runtime_error("Sample encoding failed");
            Magick::Blob input(sourceBytes.constData(), size_t(sourceBytes.size()));
            Magick::Image image;
            image.read(input);
            if (m_smoothing > 0.0) image.blur(0.0, m_smoothing);
            if (m_sharpening > 0.0) image.sharpen(0.0, m_sharpening);
            image.magick(codec.toStdString());
            if (codec == "JPEG" || codec == "WEBP")
                image.quality(size_t(m_quality));
            if (codec == "PNG") image.quality(size_t(m_pngCompression));
            if (codec == "WEBP") {
                image.defineValue("webp", "lossless", (m_webpLossless && !m_customQuality) ? "true" : "false");
                image.defineValue("webp", "method", std::to_string(m_webpMethod));
                image.defineValue("webp", "preprocessing", m_webpDithering ? "1" : "0");
            }
            Magick::Blob output;
            image.write(&output);
            QByteArray out(static_cast<const char *>(output.data()), qsizetype(output.length()));
            const QImage result = QImage::fromData(out);
            if (result.isNull()) throw std::runtime_error("Could not decode sampled output");
            m_after->setPixmap(QPixmap::fromImage(result).scaled(
                440, 410, Qt::KeepAspectRatio, Qt::SmoothTransformation));
            QSize destination = m_originalSize;
            if (m_target.isValid())
                destination = m_keepAspect ? m_originalSize.scaled(m_target, Qt::KeepAspectRatio) : m_target;
            const double pixelRatio = double(destination.width()) * destination.height()
                   / qMax(1.0, double(result.width()) * result.height());
            const double estimate = double(output.length()) * pixelRatio / 1048576.0;
            m_summary->setText(tr("Sample output: %1 KiB | Approx. full-export size: ~%2 MiB\n"
                "Smoothing: %3  •  Sharpen: %4  •  Quality: %5\n"
                "Change settings in Image Studio; this window refreshes automatically. "
                "This is a small sample, not a full-resolution print simulation. Verify final DPI after export.")
                .arg(QString::number(double(output.length()) / 1024.0, 'f', 1))
                .arg(QString::number(estimate, 'f', 1))
                .arg(QString::number(m_smoothing, 'f', 1))
                .arg(QString::number(m_sharpening, 'f', 1))
                .arg(codec == "PNG" ? tr("lossless") :
                    (m_webpLossless && codec == "WEBP" && !m_customQuality ? tr("lossless") :
                     QString::number(m_quality))));
        } catch (const Magick::Exception &e) {
            m_after->clear();
            m_summary->setText(tr("ImageMagick preview error: %1")
                .arg(QString::fromStdString(e.what())));
        } catch (const std::exception &e) {
            m_after->clear();
            m_summary->setText(tr("Preview error: %1").arg(QString::fromLocal8Bit(e.what())));
        }
    }

    QLabel *m_heading = nullptr;
    QLabel *m_before = nullptr;
    QLabel *m_after = nullptr;
    QLabel *m_summary = nullptr;
    QTimer *m_timer = nullptr;
    QString m_path;
    QImage m_sample;
    QSize m_originalSize;
    QSize m_target;
    bool m_keepAspect = true;
    QString m_codec;
    bool m_customQuality = false;
    int m_quality = 95;
    double m_smoothing = 0.0;
    double m_sharpening = 0.0;
    bool m_webpLossless = false;
    int m_pngCompression = 9;
    int m_webpMethod = 4;
    bool m_webpDithering = false;
};

} // namespace PixelShroomPhase7
