#pragma once
// Pixel Shroom Image Studio — upload-ready exports, Phase 11.
// Uses the ImageMagick instance already initialized by main.cpp.
// This is a separate batch command. The native conversion and print engine are unchanged.
#include <Magick++.h>
#include <QByteArray>
#include <QDateTime>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QFutureWatcher>
#include <QMessageBox>
#include <QPointer>
#include <QProgressDialog>
#include <QRegularExpression>
#include <QSaveFile>
#include <QStandardPaths>
#include <QStringList>
#include <QWidget>
#include <QtConcurrent/QtConcurrent>
#include <QtMath>
#include <algorithm>
#include <atomic>
#include <functional>
#include <QMetaObject>
#include <cmath>
#include <cstring>
#include <memory>
#include <limits>
#include <utility>
#include <stdexcept>
#include <vector>

namespace PixelShroomUpload {

constexpr qint64 OriginalLimit = qint64(50) * 1024 * 1024; // STRICT: files must be smaller

struct BlobCandidate {
    QByteArray bytes;
    QString suffix;
    QString description;
    bool valid = false;
};

struct Result {
    QString input;
    QString message;
    QString originalPath;
    qint64 originalBytes = 0;
    bool success = false;
};

struct Summary {
    QList<Result> rows;
    QString reportPath;
    int passed = 0;
    int failed = 0;
    bool cancelled = false;
};

inline QString cleanStem(QString s) {
    s.replace(QRegularExpression(QStringLiteral(R"([\\/:*?"<>|\x00-\x1f])")), "_");
    s = s.trimmed();
    return s.isEmpty() ? QStringLiteral("artwork") : s;
}

inline QByteArray readSource(const QString &path) {
    QFile f(path);
    if (!f.open(QIODevice::ReadOnly)) throw std::runtime_error("Source cannot be opened");
    if (f.size() > 512LL * 1024 * 1024)
        throw std::runtime_error("Source exceeds the 512 MiB safety limit for this optimizer");
    const QByteArray bytes = f.readAll();
    if (bytes.size() != f.size()) throw std::runtime_error("Source file was not completely read");
    return bytes;
}

// Optional website fallback: high-quality lossy copy, same pixel dimensions.
 // Never used unless the user explicitly enables it in the Website tab.
inline BlobCandidate encodeLossy(Magick::Image &source, const QString &format, int quality) {
    BlobCandidate out;
    Magick::Image image(source);
    if (format == "webp") {
        image.magick("WEBP");
        image.defineValue("webp", "lossless", "false");
        image.defineValue("webp", "method", "6");
        out.suffix = ".webp";
        out.description = QStringLiteral("WebP lossy quality %1").arg(quality);
    } else {
        image.magick("JPEG");
        out.suffix = ".jpg";
        out.description = QStringLiteral("JPEG lossy quality %1").arg(quality);
    }
    image.quality(size_t(quality));
    Magick::Blob blob;
    image.write(&blob);
    if (blob.length() > static_cast<size_t>(std::numeric_limits<int>::max()))
        throw std::runtime_error("Lossy output exceeds memory safety limit");
    out.bytes = QByteArray(static_cast<const char*>(blob.data()), static_cast<int>(blob.length()));
    out.valid = !out.bytes.isEmpty();
    return out;
}

inline bool nearDensity(const Magick::Image &a, const Magick::Image &b) {
    if (a.resolutionUnits() == Magick::UndefinedResolution) return true;
    if (b.resolutionUnits() == Magick::UndefinedResolution) return false;
    const auto densityDpi = [](const Magick::Image &img) {
        const double factor = img.resolutionUnits() == Magick::PixelsPerCentimeterResolution ? 2.54 : 1.0;
        return std::pair<double,double>(img.xResolution() * factor, img.yResolution() * factor);
    };
    const auto x = densityDpi(a), y = densityDpi(b);
    return std::abs(x.first-y.first) <= 1.5 && std::abs(x.second-y.second) <= 1.5;
}

inline bool sameProfile(const Magick::Image &a, const Magick::Image &b, const std::string &key) {
    try {
        const auto pa = a.profile(key);
        if (pa.length() == 0) return true;
        const auto pb = b.profile(key);
        return pa.length() == pb.length() &&
               std::memcmp(pa.data(), pb.data(), pa.length()) == 0;
    } catch (...) { return false; }
}

inline bool originalEquivalent(const Magick::Image &input, const BlobCandidate &candidate) {
    if (!candidate.valid) return false;
    try {
        const Magick::Blob bytes(candidate.bytes.constData(), size_t(candidate.bytes.size()));
        Magick::Image decoded(bytes);
        if (decoded.columns() != input.columns() || decoded.rows() != input.rows()) return false;
        if (decoded.depth() != input.depth()) return false;
        if (!input.compare(decoded)) return false;
        if (!nearDensity(input, decoded)) return false;
        for (const std::string name : {"ICC", "EXIF", "XMP", "IPTC"})
            if (!sameProfile(input, decoded, name)) return false;
        return true;
    } catch (...) { return false; }
}

// Lossy output may change color values, but must preserve the original image
// dimensions and important print/color information.
inline bool lossyMetadataOK(const Magick::Image &input, const BlobCandidate &candidate) {
    if (!candidate.valid) return false;
    try {
        Magick::Blob bytes(candidate.bytes.constData(), size_t(candidate.bytes.size()));
        Magick::Image decoded(bytes);
        // PNG images often have an undefined orientation while JPEG writers
        // normalize that field to top-left. This does not rotate the artwork.
        const auto originalOrientation = input.orientation();
        const bool orientationOK =
            originalOrientation == Magick::UndefinedOrientation
                ? (decoded.orientation() == Magick::UndefinedOrientation ||
                   decoded.orientation() == Magick::TopLeftOrientation)
                : decoded.orientation() == originalOrientation;
        return decoded.columns() == input.columns() &&
               decoded.rows() == input.rows() &&
               orientationOK &&
               nearDensity(input, decoded) &&
               sameProfile(input, decoded, "ICC");
    } catch (...) { return false; }
}

inline bool saveBytes(const QString &path, const QByteArray &bytes) {
    // Never silently replace a previous export.
    if (QFileInfo::exists(path)) return false;
    QSaveFile output(path);
    if (!output.open(QIODevice::WriteOnly)) return false;
    if (output.write(bytes) != bytes.size()) { output.cancelWriting(); return false; }
    return output.commit();
}

inline bool hasSafeStem(const QString &stem, const QString &outDir) {
    const QDir dir(outDir);
    const QStringList candidates = dir.entryList(
        QStringList() << stem + "__original.*", QDir::Files | QDir::NoDotAndDotDot);
    return candidates.isEmpty();
}

inline QString uniqueStem(const QString &baseName, const QString &outDir) {
    for (int i=0; i < 10000; ++i) {
        const QString stem = i == 0 ? baseName : baseName + "-" + QString::number(i+1);
        if (hasSafeStem(stem, outDir)) return stem;
    }
    throw std::runtime_error("Too many existing export names");
}

// Export exactly one website-ready image; never resize or overwrite the source.
inline Result process(const QString &sourcePath, const QString &targetDir,
                      bool allowLossyOriginal, int preferredQuality,
                      const std::shared_ptr<std::atomic_bool> &cancel,
                      const std::function<void(int, const QString &)> &stage) {
    Result result;
    result.input = sourcePath;
    try {
        if (stage) stage(0, QObject::tr("Reading source artwork"));
        const QFileInfo source(sourcePath);
        const QString suffix = source.suffix().toLower();
        if (!source.isFile())
            throw std::runtime_error("Source image no longer exists");
        if (!(suffix == "png" || suffix == "jpeg" || suffix == "jpg" || suffix == "webp"))
            throw std::runtime_error("Website export supports PNG, JPEG and WebP");
        const QByteArray bytes = readSource(source.absoluteFilePath());
        if (cancel && cancel->load()) throw std::runtime_error("Cancelled");
        BlobCandidate original{bytes, "." + suffix, "unchanged source", true};

        // An existing file under the size limit is already the best,
        // byte-for-byte-identical original upload copy.
        if (stage) stage(1, QObject::tr("Checking 50 MiB limit"));
        if (original.bytes.size() >= OriginalLimit) {
            const Magick::Blob inputBlob(bytes.constData(), size_t(bytes.size()));
            Magick::Image raw(inputBlob); // keep source EXIF orientation and density
            if (raw.columns() == 0 || raw.rows() == 0 ||
                raw.columns() > 20000 || raw.rows() > 20000 ||
                raw.columns() * raw.rows() > 120000000ULL)
                throw std::runtime_error("Source exceeds the supported image dimensions");

            // Try one moderate-cost lossless PNG encoding when appropriate.
            // For very large images with an opt-in lossy fallback, skip
            // this often-expensive pass and try the 50 MiB fallback directly.
            if (suffix == "png" &&
                (!allowLossyOriginal || raw.columns() * raw.rows() <= 16000000ULL)) {
                if (cancel && cancel->load()) throw std::runtime_error("Cancelled");
                if (stage) stage(1, QObject::tr("Trying lossless PNG compression"));
                try {
                    Magick::Image compressed(raw);
                    compressed.magick("PNG");
                    compressed.defineValue("png", "compression-level", "3");
                    Magick::Blob blob;
                    compressed.write(&blob);
                    if (blob.length() < static_cast<size_t>(OriginalLimit)) {
                        BlobCandidate candidate;
                        candidate.bytes = QByteArray(
                            static_cast<const char *>(blob.data()),
                            static_cast<qsizetype>(blob.length()));
                        candidate.suffix = ".png";
                        candidate.description = "PNG lossless";
                        candidate.valid = !candidate.bytes.isEmpty();
                        if (originalEquivalent(raw, candidate))
                            original = std::move(candidate);
                    }
                } catch (const Magick::Exception &) {
                    // The unmodified original remains available.
                }
            }

            if (original.bytes.size() >= OriginalLimit &&
                allowLossyOriginal && raw.depth() <= 8) {
                const QString codec = raw.isOpaque() ? QStringLiteral("jpeg")
                                                     : QStringLiteral("webp");
                const int ceiling = qBound(82, preferredQuality, 98);
                for (const int quality : {ceiling, 94, 90, 86, 82}) {
                    if (quality > ceiling) continue;
                    if (cancel && cancel->load()) throw std::runtime_error("Cancelled");
                    if (stage)
                        stage(1, QObject::tr("Compressing %1 copy at quality %2")
                              .arg(codec.toUpper()).arg(quality));
                    try {
                        BlobCandidate candidate = encodeLossy(raw, codec, quality);
                        if (candidate.valid && candidate.bytes.size() < OriginalLimit &&
                            lossyMetadataOK(raw, candidate)) {
                            original = std::move(candidate);
                            break;
                        }
                    } catch (const Magick::Exception &) {
                        // Try the next requested quality step.
                    }
                }
            }
        }

        if (original.bytes.size() >= OriginalLimit)
            throw std::runtime_error(
                "The full-resolution image cannot fit strictly below 50 MiB "
                "with the selected compression and metadata safeguards; "
                "nothing was exported or resized.");
        if (cancel && cancel->load()) throw std::runtime_error("Cancelled");
        if (stage) stage(2, QObject::tr("Saving single full-resolution upload image"));
        const QString stem = uniqueStem(cleanStem(source.completeBaseName()), targetDir);
        const QString destination = QDir(targetDir).filePath(
            stem + "__original" + original.suffix);
        if (!saveBytes(destination, original.bytes))
            throw std::runtime_error("Unable to save upload image safely");
        result.success = true;
        result.originalPath = destination;
        result.originalBytes = original.bytes.size();
        result.message = QStringLiteral("OK (%1)").arg(original.description);
        if (stage) stage(3, QObject::tr("Finished image"));
    } catch (const Magick::Exception &e) {
        result.message = QString::fromUtf8(e.what());
    } catch (const std::exception &e) {
        result.message = QString::fromUtf8(e.what());
    }
    return result;
}

inline QString safeTsv(QString s) {
    s.replace('\r',' '); s.replace('\n',' '); s.replace('\t',' ');
    return s;
}

inline Summary batch(const QStringList &files, const QString &outDir,
                     bool allowLossyOriginal, int preferredQuality,
                     const std::shared_ptr<std::atomic_bool> &cancel,
                     const std::function<void(int, const QString &)> &reportStage) {
    Summary summary;
    if (!QDir(outDir).exists() && !QDir().mkpath(outDir)) {
        Result failed; failed.message = "Cannot create output directory";
        summary.rows.append(failed);
        summary.failed = static_cast<int>(files.size());
        return summary;
    }
    for (int index = 0; index < static_cast<int>(files.size()); ++index) {
        if (cancel->load()) { summary.cancelled = true; break; }
        const QString &file = files.at(index);
        auto progress = [index, &file, &files, &reportStage](
                            int step, const QString &detail) {
            if (!reportStage) return;
            reportStage(index * 3 + step,
                QObject::tr("%1 (%2 of %3) — %4")
                    .arg(QFileInfo(file).fileName())
                    .arg(index + 1)
                    .arg(static_cast<int>(files.size()))
                    .arg(detail));
        };
        Result row = process(file, outDir, allowLossyOriginal,
                             preferredQuality, cancel, progress);
        if (row.success) ++summary.passed; else ++summary.failed;
        if (!row.success)
            progress(3, QObject::tr("Finished with an error; see report"));
        summary.rows.append(std::move(row));
        if (cancel->load()) { summary.cancelled = true; break; }
    }
    // Keep diagnostic logs separate from the upload image folder.
    const QString logsRoot = QStandardPaths::writableLocation(
        QStandardPaths::AppDataLocation);
    const QString reportDir = QDir(logsRoot).filePath("upload-reports");
    if (!logsRoot.isEmpty() && QDir().mkpath(reportDir)) {
        const QString timestamp = QDateTime::currentDateTime().toString(
            "yyyyMMdd-hhmmss-zzz");
        summary.reportPath = QDir(reportDir).filePath(
            "PixelShroom-Upload-Report-" + timestamp + ".tsv");
        QSaveFile log(summary.reportPath);
        if (log.open(QIODevice::WriteOnly)) {
            log.write("Source\tStatus\tOutput bytes\tOutput image\n");
            for (const Result &row : summary.rows) {
                const QString line = QStringLiteral("%1\t%2\t%3\t%4\n")
                    .arg(safeTsv(row.input), safeTsv(row.message))
                    .arg(row.originalBytes)
                    .arg(safeTsv(row.originalPath));
                log.write(line.toUtf8());
            }
            if (!log.commit()) summary.reportPath.clear();
        } else {
            summary.reportPath.clear();
        }
    }
    return summary;
}

inline void start(QWidget *parent, const QStringList &files, const QString &targetDir,
                  bool allowLossyOriginal, int preferredQuality) {
    if (files.isEmpty()) {
        QMessageBox::information(parent, QObject::tr("No images"),
                                 QObject::tr("Check one or more imported images."));
        return;
    }
    if (targetDir.trimmed().isEmpty()) {
        QMessageBox::warning(parent, QObject::tr("Output folder missing"),
            QObject::tr("Choose an output directory before website optimization."));
        return;
    }
    const auto cancel = std::make_shared<std::atomic_bool>(false);
    const int steps = qMax(1, static_cast<int>(files.size()) * 3);
    auto *progress = new QProgressDialog(
        QObject::tr("Preparing full-resolution website images..."),
        QObject::tr("Cancel remaining work"), 0, steps, parent);
    progress->setAttribute(Qt::WA_DeleteOnClose, false);
    progress->setWindowModality(Qt::WindowModal);
    progress->setMinimumDuration(0);
    progress->setAutoClose(false);
    progress->setAutoReset(false);
    progress->setMinimumWidth(450);
    progress->setValue(0);
    progress->show();
    QObject::connect(progress, &QProgressDialog::canceled, parent,
        [cancel]() { cancel->store(true); });
    auto *watcher = new QFutureWatcher<Summary>(parent);
    const QPointer<QProgressDialog> guard(progress);
    QObject::connect(watcher, &QFutureWatcher<Summary>::finished, parent,
        [watcher, guard, parent]() {
        const Summary summary = watcher->result();
        if (guard) { guard->close(); guard->deleteLater(); }
        QStringList errors;
        for (const Result &row : summary.rows)
            if (!row.success && errors.size() < 6)
                errors << QFileInfo(row.input).fileName() + ": " + row.message;
        QString msg = QObject::tr("Images prepared: %1    Failed: %2")
            .arg(summary.passed).arg(summary.failed);
        if (summary.cancelled)
            msg += QObject::tr("\nCancelled before the next image.");
        if (!summary.reportPath.isEmpty())
            msg += QObject::tr("\n\nDiagnostic report: %1").arg(summary.reportPath);
        if (!errors.isEmpty()) msg += "\n\n" + errors.join("\n");
        QMessageBox::information(parent, QObject::tr("Website image results"), msg);
        watcher->deleteLater();
    });
    const auto reportStage = [watcher, guard, steps](
                                 int step, const QString &detail) {
        QMetaObject::invokeMethod(watcher, [guard, step, steps, detail]() {
            if (!guard || guard->wasCanceled()) return;
            guard->setLabelText(detail);
            guard->setValue(qBound(0, step, steps));
        }, Qt::QueuedConnection);
    };
    watcher->setFuture(QtConcurrent::run(
        [files, targetDir, allowLossyOriginal, preferredQuality, cancel, reportStage]() {
            return batch(files, targetDir, allowLossyOriginal,
                         preferredQuality, cancel, reportStage);
        }));
}

} // namespace PixelShroomUpload
