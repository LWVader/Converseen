#pragma once
// Pixel Shroom Phase 6 — optional UI-only preview and linked comparison.
// The existing Converseen converter, print DPI and batch workflow are untouched.
#include <QBuffer>
#include <QCheckBox>
#include <QComboBox>
#include <QDesktopServices>
#include <QDialog>
#include <QDoubleSpinBox>
#include <QFileInfo>
#include <QGraphicsPixmapItem>
#include <QGraphicsScene>
#include <QGraphicsView>
#include <QHBoxLayout>
#include <QImageReader>
#include <QImageWriter>
#include <QLabel>
#include <QPainter>
#include <QImage>
#include <QPixmap>
#include <QSizePolicy>
#include <QMessageBox>
#include <QPushButton>
#include <QScrollBar>
#include <QSlider>
#include <QSpinBox>
#include <QTimer>
#include <QUrl>
#include <QVBoxLayout>
#include <QtMath>
#include <Magick++.h>
#include <algorithm>
#include <cmath>
#include <functional>
#include <stdexcept>

namespace PixelShroomPhase6 {

inline QString fileInfo(const QString &path, const QImage &pixels) {
    const QFileInfo f(path);
    QString dpiText = QObject::tr("Embedded DPI: not specified");
    try {
        Magick::Image meta;
        meta.ping(path.toStdString());
        const auto units = meta.resolutionUnits();
        if (units == Magick::PixelsPerInchResolution ||
            units == Magick::PixelsPerCentimeterResolution) {
            const double factor = units == Magick::PixelsPerCentimeterResolution ? 2.54 : 1.0;
            dpiText = QObject::tr("Embedded DPI: %1 x %2")
                .arg(qRound(meta.xResolution() * factor))
                .arg(qRound(meta.yResolution() * factor));
        }
    } catch (const Magick::Exception &) {
        dpiText = QObject::tr("Embedded DPI: unavailable");
    }
    return QObject::tr("%1\n%2 x %3 pixels | %4 MiB\n%5")
        .arg(f.fileName()).arg(pixels.width()).arg(pixels.height())
        .arg(QString::number(f.size() / 1048576.0, 'f', 2)).arg(dpiText);
}

inline double embeddedDpi(const QString &path) {
    try {
        Magick::Image im;
        im.ping(path.toStdString());
        const auto u = im.resolutionUnits();
        if (u == Magick::PixelsPerInchResolution || u == Magick::PixelsPerCentimeterResolution) {
            const double f = u == Magick::PixelsPerCentimeterResolution ? 2.54 : 1.0;
            const double dx = im.xResolution() * f;
            const double dy = im.yResolution() * f;
            if (dx > 0 && dy > 0 && qAbs(dx-dy) <= 2.0) return (dx+dy)/2;
        }
    } catch (const Magick::Exception &) {}
    return 0;
}

inline void compare(QWidget *owner, const QString &originalPath,
                    const QString &exportPath, int requestedPrintDpi) {
    QImageReader beforeReader(originalPath), afterReader(exportPath);
    beforeReader.setAutoTransform(true);
    afterReader.setAutoTransform(true);
    const QSize aSize = beforeReader.size(), bSize = afterReader.size();
    if (aSize.isValid() && bSize.isValid()) {
        const quint64 pixels = quint64(aSize.width()) * aSize.height()
                             + quint64(bSize.width()) * bSize.height();
        if (pixels > 170000000ULL && QMessageBox::question(owner,
                QObject::tr("Large comparison"),
                QObject::tr("Opening both full-resolution images may use substantial memory. Continue?"))
                != QMessageBox::Yes) return;
    }
    const QImage before = beforeReader.read(), after = afterReader.read();
    if (before.isNull() || after.isNull()) {
        QMessageBox::warning(owner, QObject::tr("Cannot open comparison"),
            QObject::tr("Original: %1\nOutput: %2")
              .arg(beforeReader.errorString()).arg(afterReader.errorString()));
        return;
    }

    QDialog dlg(owner);
    dlg.setWindowTitle(QObject::tr("Pixel Shroom | Synchronized comparison"));
    dlg.setMinimumSize(780, 520);
    dlg.resize(1120, 750);
    dlg.setStyleSheet(R"PS6(QDialog { background:#20252b; color:#eff4f7; }
        QLabel { color:#eff4f7; }
        QPushButton, QComboBox { color:#f4f6f8; background:#364650;
          border:1px solid #62788b; padding:6px 12px; border-radius:4px; }
        QGraphicsView { background:#11171e; border:1px solid #667784; }
    )PS6");
    auto *root = new QVBoxLayout(&dlg);
    auto *header = new QHBoxLayout();
    auto *title = new QLabel(QObject::tr("ORIGINAL   /   EXPORTED OUTPUT"), &dlg);
    header->addWidget(title, 1);
    header->addWidget(new QLabel(QObject::tr("Linked zoom:"), &dlg));
    auto *zoom = new QComboBox(&dlg);
    zoom->addItems({QObject::tr("Fit"), QObject::tr("100%"), QObject::tr("200%"), QObject::tr("400%")});
    zoom->setToolTip(QObject::tr("100% = native exported-image pixels. The original is scaled to match the subject area."));
    header->addWidget(zoom);
    root->addLayout(header);

    auto *columns = new QHBoxLayout();
    root->addLayout(columns, 1);
    auto makePane = [&](const QString &caption, const QString &path, const QImage &im) {
        auto *layout = new QVBoxLayout();
        auto *name = new QLabel(caption, &dlg);
        layout->addWidget(name);
        auto *view = new QGraphicsView(&dlg);
        view->setRenderHint(QPainter::SmoothPixmapTransform, true);
        view->setDragMode(QGraphicsView::ScrollHandDrag);
        view->setResizeAnchor(QGraphicsView::AnchorViewCenter);
        view->setTransformationAnchor(QGraphicsView::AnchorViewCenter);
        auto *scene = new QGraphicsScene(view);
        scene->addPixmap(QPixmap::fromImage(im));
        scene->setSceneRect(0, 0, im.width(), im.height());
        view->setScene(scene);
        layout->addWidget(view, 1);
        auto *details = new QLabel(fileInfo(path, im), &dlg);
        details->setWordWrap(true);
        layout->addWidget(details);
        columns->addLayout(layout, 1);
        return view;
    };
    auto *left = makePane(QObject::tr("BEFORE | ORIGINAL"), originalPath, before);
    auto *right = makePane(QObject::tr("AFTER | EXPORTED"), exportPath, after);
    // Match normalized subject coordinates even when source/output pixel sizes differ.
    bool syncing = false;
    auto syncCenter = [&](QGraphicsView *from, QGraphicsView *to) {
        if (syncing) return;
        syncing = true;
        const QRectF sr = from->sceneRect(), dst = to->sceneRect();
        const QPointF center = from->mapToScene(from->viewport()->rect().center());
        const double x = sr.width() ? (center.x()-sr.left())/sr.width() : 0.5;
        const double y = sr.height() ? (center.y()-sr.top())/sr.height() : 0.5;
        to->centerOn(dst.left()+x*dst.width(), dst.top()+y*dst.height());
        syncing = false;
    };
    for (auto *sb : {left->horizontalScrollBar(), left->verticalScrollBar()})
        QObject::connect(sb, &QScrollBar::valueChanged, &dlg,
                         [&, right, left](int) { syncCenter(left, right); });
    for (auto *sb : {right->horizontalScrollBar(), right->verticalScrollBar()})
        QObject::connect(sb, &QScrollBar::valueChanged, &dlg,
                         [&, right, left](int) { syncCenter(right, left); });
    auto applyZoom = [&]() {
        const int mode = zoom->currentIndex();
        syncing = true;
        if (mode == 0) {
            left->fitInView(left->sceneRect(), Qt::KeepAspectRatio);
            right->fitInView(right->sceneRect(), Qt::KeepAspectRatio);
        } else {
            const double z = mode == 1 ? 1.0 : (mode == 2 ? 2.0 : 4.0);
            const double sourceFactor = double(after.width()) / qMax(1, before.width());
            left->resetTransform(); right->resetTransform();
            left->scale(z*sourceFactor, z*sourceFactor);
            right->scale(z, z);
        }
        left->centerOn(left->sceneRect().center());
        right->centerOn(right->sceneRect().center());
        syncing = false;
    };
    QObject::connect(zoom, QOverload<int>::of(&QComboBox::currentIndexChanged),
                     &dlg, [&](int) { applyZoom(); });

    auto *info = new QLabel(&dlg);
    info->setWordWrap(true);
    const double factor = double(after.width()) / qMax(1, before.width());
    QString message = QObject::tr("Size: %1 x %2 px. Enlargement: %3x. Zoom and drag either image to inspect the same region.")
        .arg(after.width()).arg(after.height()).arg(QString::number(factor, 'f', 2));
    const double actualDpi = embeddedDpi(exportPath);
    if (requestedPrintDpi > 0) {
        if (actualDpi > 0 && qAbs(actualDpi-requestedPrintDpi) <= 2.0)
            message += QObject::tr("\nPrint DPI verified: %1 DPI embedded in export.").arg(qRound(actualDpi));
        else
            message += QObject::tr("\nWARNING: Expected %1 DPI but exported metadata does not match.").arg(requestedPrintDpi);
    }
    info->setText(message);
    root->addWidget(info);
    auto *buttons = new QHBoxLayout();
    buttons->addStretch();
    auto *open = new QPushButton(QObject::tr("Open exported file"), &dlg);
    QObject::connect(open, &QPushButton::clicked, &dlg, [exportPath]() {
        QDesktopServices::openUrl(QUrl::fromLocalFile(exportPath));
    });
    buttons->addWidget(open);
    auto *close = new QPushButton(QObject::tr("Close"), &dlg);
    QObject::connect(close, &QPushButton::clicked, &dlg, &QDialog::accept);
    buttons->addWidget(close);
    root->addLayout(buttons);
    QTimer::singleShot(0, &dlg, applyZoom);
    dlg.exec();
}

inline void livePreview(QWidget *owner, const QString &path, QSize target,
                        bool keepAspect, const QString &format,
                        bool overrideQuality, int quality, double smooth, double sharpen,
                        bool webpLossless, std::function<void(bool,int,double,double)> applySettings) {
    QString codec = format.toUpper();
    if (codec == "JPG") codec = "JPEG";
    if (codec != "JPEG" && codec != "WEBP" && codec != "PNG") {
        QMessageBox::information(owner, QObject::tr("Unsupported preview format"),
            QObject::tr("For the interactive preview, choose JPEG, PNG or WebP as your export format."));
        return;
    }
    QImageReader reader(path);
    reader.setAutoTransform(true);
    const QSize originalSize = reader.size();
    if (!originalSize.isValid()) {
        QMessageBox::warning(owner, QObject::tr("Cannot preview"), reader.errorString());
        return;
    }
    reader.setScaledSize(originalSize.scaled(1100, 1100, Qt::KeepAspectRatio));
    const QImage sample = reader.read();
    if (sample.isNull()) {
        QMessageBox::warning(owner, QObject::tr("Cannot preview"), reader.errorString());
        return;
    }
    QDialog dlg(owner);
    dlg.setWindowTitle(QObject::tr("Pixel Shroom | Live quality preview"));
    dlg.setMinimumSize(730, 550);
    dlg.resize(1000, 700);
    dlg.setStyleSheet(R"PS6(QDialog { background:#20252b; color:#f1f4f7; }
        QLabel, QCheckBox { color:#f1f4f7; }
        QPushButton, QSpinBox, QDoubleSpinBox { background:#364650; color:white;
            border:1px solid #637b8c; padding:5px; border-radius:4px; }
        QSlider::groove:horizontal { height:5px; background:#647783; }
        QSlider::handle:horizontal { background:#68b9e7; width:16px; margin:-6px 0; }
    )PS6");
    auto *layout = new QVBoxLayout(&dlg);
    auto *heading = new QLabel(QObject::tr("SAMPLED PREVIEW  |  %1  |  Original %2 x %3 px")
        .arg(codec).arg(originalSize.width()).arg(originalSize.height()), &dlg);
    layout->addWidget(heading);
    auto *columns = new QHBoxLayout();
    layout->addLayout(columns, 1);
    auto createImage = [&](const QString &title) {
        auto *pane = new QVBoxLayout();
        pane->addWidget(new QLabel(title, &dlg));
        auto *image = new QLabel(&dlg);
        image->setMinimumHeight(320);
        image->setAlignment(Qt::AlignCenter);
        image->setStyleSheet("background:#10161c; border:1px solid #506070;");
        image->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
        pane->addWidget(image, 1);
        columns->addLayout(pane, 1);
        return image;
    };
    auto *beforeLabel = createImage(QObject::tr("ORIGINAL SAMPLE"));
    auto *afterLabel = createImage(QObject::tr("ADJUSTED / COMPRESSED SAMPLE"));
    const QPixmap originalPix = QPixmap::fromImage(sample);
    beforeLabel->setPixmap(originalPix.scaled(430, 390, Qt::KeepAspectRatio, Qt::SmoothTransformation));
    auto *custom = new QCheckBox(QObject::tr("Override JPEG/WebP quality"), &dlg);
    custom->setChecked(overrideQuality && codec != "PNG");
    custom->setEnabled(codec != "PNG");
    layout->addWidget(custom);
    auto *qualityRow = new QHBoxLayout();
    qualityRow->addWidget(new QLabel(QObject::tr("Quality"), &dlg));
    auto *qualitySlider = new QSlider(Qt::Horizontal, &dlg);
    qualitySlider->setRange(1, 100);
    qualitySlider->setValue(quality);
    qualitySlider->setEnabled(custom->isChecked());
    qualityRow->addWidget(qualitySlider, 1);
    auto *qualityNumber = new QSpinBox(&dlg);
    qualityNumber->setRange(1, 100);
    qualityNumber->setValue(quality);
    qualityNumber->setEnabled(custom->isChecked());
    qualityRow->addWidget(qualityNumber);
    layout->addLayout(qualityRow);
    auto *effects = new QHBoxLayout();
    auto addEffect = [&](const QString &name, double value) {
        effects->addWidget(new QLabel(name, &dlg));
        auto *box = new QDoubleSpinBox(&dlg);
        box->setDecimals(1); box->setRange(0, 2); box->setSingleStep(0.1);
        box->setValue(value);
        effects->addWidget(box);
        return box;
    };
    auto *blur = addEffect(QObject::tr("Smoothing"), smooth);
    auto *sharp = addEffect(QObject::tr("Sharpen"), sharpen);
    effects->addStretch();
    layout->addLayout(effects);
    auto *estimate = new QLabel(&dlg);
    estimate->setWordWrap(true);
    layout->addWidget(estimate);
    auto *timer = new QTimer(&dlg);
    timer->setSingleShot(true);
    timer->setInterval(320);
    auto render = [&]() {
        estimate->setText(QObject::tr("Rendering compressed sample..."));
        try {
            // Preview processes a capped sample, never the original or export files.
            QImage scaled = sample;
            if (target.isValid()) {
                QSize sampleTarget = target.scaled(1100, 1100, Qt::KeepAspectRatio);
                if (keepAspect) sampleTarget = sample.size().scaled(sampleTarget, Qt::KeepAspectRatio);
                if (sampleTarget.isValid())
                    scaled = sample.scaled(sampleTarget, Qt::IgnoreAspectRatio, Qt::SmoothTransformation);
            }
            QByteArray sourceBytes;
            QBuffer buffer(&sourceBytes);
            buffer.open(QIODevice::WriteOnly);
            QImageWriter writer(&buffer, "PNG");
            if (!writer.write(scaled)) throw std::runtime_error("Could not encode temporary sample");
            Magick::Blob input(sourceBytes.constData(), size_t(sourceBytes.size()));
            Magick::Image magick;
            magick.read(input);
            if (blur->value() > 0.0) magick.blur(0.0, blur->value());
            if (sharp->value() > 0.0) magick.sharpen(0.0, sharp->value());
            magick.magick(codec.toStdString());
            if (codec == "JPEG" || codec == "WEBP")
                magick.quality(size_t(qualityNumber->value()));
            if (codec == "WEBP")
                magick.defineValue("webp", "lossless",
                                   (!custom->isChecked() && webpLossless) ? "true" : "false");
            Magick::Blob output;
            magick.write(&output);
            QByteArray compressed(static_cast<const char *>(output.data()), qsizetype(output.length()));
            const QImage result = QImage::fromData(compressed);
            if (result.isNull()) throw std::runtime_error("Could not decode compressed preview");
            afterLabel->setPixmap(QPixmap::fromImage(result).scaled(430, 390,
                Qt::KeepAspectRatio, Qt::SmoothTransformation));
            double targetPixels = double(originalSize.width()) * originalSize.height();
            if (target.isValid()) {
                QSize realTarget = keepAspect ? originalSize.scaled(target, Qt::KeepAspectRatio) : target;
                targetPixels = double(realTarget.width()) * realTarget.height();
            }
            const double ratio = targetPixels / qMax(1.0, double(result.width()) * result.height());
            const double mib = double(output.length()) * ratio / 1048576.0;
            estimate->setText(QObject::tr("Compressed sample: %1 KiB  |  Rough full-export estimate: ~%2 MiB\n"
                "Approximation only: full-size detail, metadata and encoder settings change file size. "
                "The preview uses a reduced image; final texture and print DPI must be verified after export.")
                .arg(QString::number(double(output.length())/1024.0, 'f', 1))
                .arg(QString::number(mib, 'f', 1)));
        } catch (const std::exception &e) {
            estimate->setText(QObject::tr("Preview failed: %1").arg(QString::fromLocal8Bit(e.what())));
        }
    };
    QObject::connect(timer, &QTimer::timeout, &dlg, render);
    auto schedule = [&]() { timer->start(); };
    QObject::connect(custom, &QCheckBox::toggled, &dlg, [=](bool enabled) {
        qualitySlider->setEnabled(enabled);
        qualityNumber->setEnabled(enabled);
        schedule();
    });
    QObject::connect(qualitySlider, &QSlider::valueChanged, qualityNumber, &QSpinBox::setValue);
    QObject::connect(qualityNumber, QOverload<int>::of(&QSpinBox::valueChanged), &dlg,
                     [=](int v) { qualitySlider->setValue(v); schedule(); });
    QObject::connect(blur, QOverload<double>::of(&QDoubleSpinBox::valueChanged), &dlg,
                     [=](double) { schedule(); });
    QObject::connect(sharp, QOverload<double>::of(&QDoubleSpinBox::valueChanged), &dlg,
                     [=](double) { schedule(); });
    auto *buttons = new QHBoxLayout();
    buttons->addStretch();
    auto *apply = new QPushButton(QObject::tr("Apply settings to batch"), &dlg);
    QObject::connect(apply, &QPushButton::clicked, &dlg, [&]() {
        applySettings(custom->isChecked(), qualityNumber->value(), blur->value(), sharp->value());
        dlg.accept();
    });
    buttons->addWidget(apply);
    auto *cancel = new QPushButton(QObject::tr("Cancel"), &dlg);
    QObject::connect(cancel, &QPushButton::clicked, &dlg, &QDialog::reject);
    buttons->addWidget(cancel);
    layout->addLayout(buttons);
    QTimer::singleShot(0, &dlg, render);
    dlg.exec();
}
} // namespace PixelShroomPhase6
