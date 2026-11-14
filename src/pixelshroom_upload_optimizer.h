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

constexpr qint64 PreviewLimit = qint64(10) * 1024 * 1024;
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
    QString previewPath;
    qint64 originalBytes = 0;
    qint64 previewBytes = 0;
    int previewWidth = 0;
    int previewHeight = 0;
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

inline BlobCandidate encode(Magick::Image &source, const QString &format) {
    BlobCandidate out;
    Magick::Image image(source); // copy-on-write; do not mutate the source
    if (format == "webp") {
        image.magick("WEBP");
        image.defineValue("webp", "lossless", "true");
        image.defineValue("webp", "method", "6");
        image.quality(100);
        out.suffix = ".webp";
        out.description = "WebP lossless";
    } else {
        image.magick("PNG");
        image.defineValue("png", "compression-level", "9");
        image.defineValue("png", "compression-filter", "5");
        out.suffix = ".png";
        out.description = "PNG lossless";
    }
    Magick::Blob blob;
    image.write(&blob);
    if (blob.length() > static_cast<size_t>(std::numeric_limits<int>::max()))
        throw std::runtime_error("Encoded file is too large for memory");
    out.bytes = QByteArray(static_cast<const char*>(blob.data()), static_cast<int>(blob.length()));
    out.valid = !out.bytes.isEmpty();
    return out;
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
    const QStringList candidates = dir.entryList(QStringList() << stem + "__original.*"
                                                             << stem + "__preview.*",
                                                  QDir::Files | QDir::NoDotAndDotDot);
    return candidates.isEmpty();
}

inline QString uniqueStem(const QString &baseName, const QString &outDir) {
    for (int i=0; i < 10000; ++i) {
        const QString stem = i == 0 ? baseName : baseName + "-" + QString::number(i+1);
        if (hasSafeStem(stem, outDir)) return stem;
    }
    throw std::runtime_error("Too many existing export names");
}

    // Pixel Shroom Phase 19: shared Resize bounds
inline BlobCandidate choosePreview(Magick::Image &input, const QByteArray &original,
                                   const QString &suffix, int maxWidth, int maxHeight,
                                   bool downscale, int &width, int &height,
                                   const std::shared_ptr<std::atomic_bool> &cancel,
                                   const std::function<void(const QString &)> &stage) {
    const int iw = int(input.columns()), ih = int(input.rows());
    const int targetW = std::max(1, std::min(20000, maxWidth));
    const int targetH = std::max(1, std::min(20000, maxHeight));
    if (original.size() < PreviewLimit && iw <= targetW && ih <= targetH) {
        // An already-valid original is also a valid, pixel-identical preview.
        width = iw;
        height = ih;
        return {original, "." + suffix, "unchanged source", true};
    }
    Magick::Image preview(input);
    double scale = std::min({1.0, double(targetW) / iw, double(targetH) / ih});
    // Prevent large input artwork from causing minutes of pointless
    // full-resolution preview encoding when automatic shrinking is enabled.
    if (downscale && original.size() >= PreviewLimit) {
        const double fastPreviewEdge = 2560.0;
        scale = std::min(scale, fastPreviewEdge / std::max(iw, ih));
    }
    if (scale < 1.0) {
        if (stage) stage(QObject::tr("Resizing website preview"));
        preview.filterType(Magick::LanczosFilter);
        preview.resize(Magick::Geometry(size_t(std::max(1, qRound(iw * scale))),
                                        size_t(std::max(1, qRound(ih * scale)))));
    }

    // One fast lossless codec at each size, instead of two maximum-effort
    // encodes at up to 16 sizes. Honor 16-bit sources with PNG.
    const QString codec = preview.depth() > 8 ? QStringLiteral("png")
                                              : QStringLiteral("webp");
    for (int attempt = 0; attempt < 10; ++attempt) {
        if (cancel && cancel->load())
            throw std::runtime_error("Cancelled during preview optimization");
        if (stage)
            stage(QObject::tr("Encoding preview (%1 x %2, attempt %3)")
                    .arg(preview.columns()).arg(preview.rows()).arg(attempt + 1));
        try {
            Magick::Image image(preview);
            if (codec == "webp") {
                image.magick("WEBP");
                image.defineValue("webp", "lossless", "true");
                image.defineValue("webp", "method", "2");
                image.quality(100);
            } else {
                image.magick("PNG");
                image.defineValue("png", "compression-level", "3");
            }
            Magick::Blob blob;
            image.write(&blob);
            if (blob.length() < static_cast<size_t>(PreviewLimit)) {
                BlobCandidate result;
                result.bytes = QByteArray(static_cast<const char *>(blob.data()),
                                           static_cast<qsizetype>(blob.length()));
                result.suffix = codec == "webp" ? ".webp" : ".png";
                result.description = codec == "webp" ? "WebP lossless" : "PNG lossless";
                result.valid = !result.bytes.isEmpty();
                width = int(preview.columns());
                height = int(preview.rows());
                return result;
            }
        } catch (const Magick::Exception &) {
            // Try a smaller resolution if the codec fails.
        }
        if (!downscale || std::max(preview.columns(), preview.rows()) <= 256) break;
        const size_t w = std::max<size_t>(1, size_t(std::floor(preview.columns() * 0.70)));
        const size_t h = std::max<size_t>(1, size_t(std::floor(preview.rows() * 0.70)));
        preview.filterType(Magick::LanczosFilter);
        preview.resize(Magick::Geometry(w, h));
    }
    throw std::runtime_error("Preview cannot reach 10 MiB. Reduce Resize dimensions or allow automatic preview shrinking.");
}

inline Result process(const QString &sourcePath, const QString &targetDir,
                      int maxWidth, int maxHeight, bool downscale,
                      bool allowLossyOriginal, int preferredQuality,
                      const std::shared_ptr<std::atomic_bool> &cancel,
                      const std::function<void(int, const QString &)> &stage) {
    Result result;
    result.input = sourcePath;
    try {
        if (stage) stage(0, QObject::tr("Reading source image"));
        const QFileInfo source(sourcePath);
        const QString suffix = source.suffix().toLower();
        if (!source.isFile()) throw std::runtime_error("Source file no longer exists");
        if (!(suffix == "png" || suffix == "jpeg" || suffix == "jpg" || suffix == "webp"))
            throw std::runtime_error("Only PNG, JPEG and WebP still images are supported for upload export");
        const QByteArray bytes = readSource(source.absoluteFilePath());
        if (cancel && cancel->load()) throw std::runtime_error("Cancelled");
        if (stage) stage(1, QObject::tr("Decoding image and checking dimensions"));
        const Magick::Blob inputBlob(bytes.constData(), size_t(bytes.size()));
        Magick::Image input(inputBlob);
        input.autoOrient(); // source is not mutated; preview follows its orientation
        if (input.columns() == 0 || input.rows() == 0)
            throw std::runtime_error("Image has invalid dimensions");
        if (input.columns() > 20000 || input.rows() > 20000 ||
            input.columns() * input.rows() > 120000000ULL)
            throw std::runtime_error("Image exceeds the 120-megapixel batch safety limit");
        // Do not recompress an original that ALREADY meets the upload cap.
        // It is the exact source file, preserving every byte and profile.
        BlobCandidate original {bytes, "." + suffix, "unchanged source", true};
        if (stage) stage(2, QObject::tr("Preparing original (50 MiB limit)"));
        if (original.bytes.size() >= OriginalLimit) {
            Magick::Image raw(inputBlob);
            // Lossless attempts are limited and fast; avoid 100%-effort
            // PNG/WebP work on multi-megapixel sources without a size need.
            if (suffix == "png") {
                try {
                    if (cancel && cancel->load()) throw std::runtime_error("Cancelled");
                    if (stage) stage(2, QObject::tr("Trying fast lossless PNG"));
                    Magick::Image compressed(raw);
                    compressed.magick("PNG");
                    compressed.defineValue("png", "compression-level", "3");
                    Magick::Blob blob;
                    compressed.write(&blob);
                    if (blob.length() < static_cast<size_t>(OriginalLimit)) {
                        BlobCandidate candidate;
                        candidate.bytes = QByteArray(static_cast<const char *>(blob.data()),
                                                     static_cast<qsizetype>(blob.length()));
                        candidate.suffix = ".png";
                        candidate.description = "PNG lossless";
                        candidate.valid = !candidate.bytes.isEmpty();
                        if (originalEquivalent(raw, candidate)) original = std::move(candidate);
                    }
                } catch (const Magick::Exception &) { /* try selected fallback */ }
            }
            if (original.bytes.size() >= OriginalLimit && allowLossyOriginal && raw.depth() <= 8) {
#if MagickLibVersion < 0x700
                const bool opaque = !raw.matte();
#else
                const bool opaque = raw.isOpaque();
#endif
                const QString codec = opaque ? QStringLiteral("jpeg")
                                             : QStringLiteral("webp");
                const int ceiling = qBound(82, preferredQuality, 98);
                for (const int quality : {ceiling, 94, 90, 86, 82}) {
                    if (cancel && cancel->load()) throw std::runtime_error("Cancelled");
                    if (quality > ceiling) continue;
                    if (stage) stage(2, QObject::tr("Compressing original as %1 at quality %2")
                                               .arg(codec.toUpper()).arg(quality));
                    try {
                        BlobCandidate candidate = encodeLossy(raw, codec, quality);
                        if (candidate.valid && candidate.bytes.size() < OriginalLimit &&
                            lossyMetadataOK(raw, candidate)) {
                            original = std::move(candidate);
                            break;
                        }
                    } catch (const Magick::Exception &) { /* try next quality */ }
                }
            }
        }
        if (original.bytes.size() >= OriginalLimit && allowLossyOriginal) {
            // A photograph or opaque 8-bit artwork can often reach 50 MiB
            // at high quality without changing its pixel dimensions.
            // 16-bit originals are not silently reduced to 8-bit.
            if (raw.depth() <= 8) {
                // An alpha channel can exist even when all pixels are opaque.
                // Encode fully opaque artwork as JPEG; preserve actual
                // transparency via WebP when needed.
                const QString codec = raw.isOpaque() ? QStringLiteral("jpeg")
                                                      : QStringLiteral("webp");
                // Highest acceptable quality wins; never drop below 82.
                const int ceiling = qBound(82, preferredQuality, 98);
                for (const int quality : {ceiling, 94, 90, 86, 82}) {
                    if (quality > ceiling) continue;
                    try {
                        BlobCandidate candidate = encodeLossy(raw, codec, quality);
                        if (candidate.valid && candidate.bytes.size() < OriginalLimit &&
                            lossyMetadataOK(raw, candidate)) {
                            original = std::move(candidate);
                            break;
                        }
                    } catch (const Magick::Exception &) { /* test next quality */ }
                }
            }
        }
        if (original.bytes.size() >= OriginalLimit)
            throw std::runtime_error(
                "Original cannot fit under 50 MiB with the selected fidelity settings. "
                "Enable the optional high-quality original compression under Website, "
                "or use a smaller source. No source pixels were changed.");
        if (cancel && cancel->load()) throw std::runtime_error("Cancelled");
        if (stage) stage(3, QObject::tr("Preparing website preview (10 MiB limit)"));
        int pw = 0, ph = 0;
        BlobCandidate preview = choosePreview(input, bytes, suffix, maxWidth, maxHeight,
             downscale, pw, ph, cancel,
             [stage](const QString &detail) { if (stage) stage(3, detail); });
        if (preview.bytes.size() >= PreviewLimit)
            throw std::runtime_error("Preview exceeds the 10 MiB limit");
        if (cancel && cancel->load()) throw std::runtime_error("Cancelled");
        if (stage) stage(4, QObject::tr("Saving original and preview"));
        const QString stem = uniqueStem(cleanStem(source.completeBaseName()), targetDir);
        const QDir dir(targetDir);
        const QString origPath = dir.filePath(stem + "__original" + original.suffix);
        const QString prevPath = dir.filePath(stem + "__preview" + preview.suffix);
        if (!saveBytes(origPath, original.bytes))
            throw std::runtime_error("Could not safely save the original file");
        if (!saveBytes(prevPath, preview.bytes)) {
            QFile::remove(origPath); // rollback only the file created in this invocation
            throw std::runtime_error("Could not safely save the preview file");
        }
        result.success = true;
        result.originalPath = origPath; result.previewPath = prevPath;
        result.originalBytes = original.bytes.size(); result.previewBytes = preview.bytes.size();
        result.previewWidth = pw; result.previewHeight = ph;
        result.message = QStringLiteral("OK (%1 original, %2 preview)")
                             .arg(original.description, preview.description);
        if (stage) stage(5, QObject::tr("Completed image"));
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
                     int maxWidth, int maxHeight, bool downscale,
                     bool allowLossyOriginal, int preferredQuality,
                     const std::shared_ptr<std::atomic_bool> &cancel,
                     const std::function<void(int, const QString &)> &reportStage) {
    Summary result;
    if (!QDir(outDir).exists() && !QDir().mkpath(outDir)) {
        Result failed; failed.message = "Cannot create output directory";
        result.rows.append(failed); result.failed = files.size(); return result;
    }
    for (int index = 0; index < static_cast<int>(files.size()); ++index) {
        if (cancel->load()) { result.cancelled = true; break; }
        const QString &file = files.at(index);
        auto progress = [index, &file, &files, &reportStage](int step, const QString &detail) {
            if (!reportStage) return;
            reportStage(index * 5 + step,
                QObject::tr("%1 (%2 of %3) — %4")
                    .arg(QFileInfo(file).fileName())
                    .arg(index + 1)
                    .arg(static_cast<int>(files.size()))
                    .arg(detail));
        };
        Result row = process(file, outDir, maxWidth, maxHeight, downscale,
                             allowLossyOriginal, preferredQuality, cancel, progress);
        if (row.success) ++result.passed; else ++result.failed;
        if (!row.success)
            progress(5, QObject::tr("Finished with an error; see export report"));
        result.rows.append(std::move(row));
        if (cancel->load()) { result.cancelled = true; break; }
    }
    const QString timestamp = QDateTime::currentDateTime().toString("yyyyMMdd-hhmmss-zzz");
    result.reportPath = QDir(outDir).filePath("PixelShroom-Upload-Report-" + timestamp + ".tsv");
    QSaveFile log(result.reportPath);
    if (log.open(QIODevice::WriteOnly)) {
        log.write("Source\tStatus\tOriginal bytes\tPreview bytes\tPreview dimensions\tOriginal file\tPreview file\n");
        for (const auto &row : result.rows) {
            const QString line = QStringLiteral("%1\t%2\t%3\t%4\t%5x%6\t%7\t%8\n")
                .arg(safeTsv(row.input),safeTsv(row.message))
                .arg(row.originalBytes).arg(row.previewBytes).arg(row.previewWidth).arg(row.previewHeight)
                .arg(safeTsv(row.originalPath),safeTsv(row.previewPath));
            log.write(line.toUtf8());
        }
        if (!log.commit()) result.reportPath.clear();
    } else result.reportPath.clear();
    return result;
}

inline void start(QWidget *parent, const QStringList &files, const QString &targetDir,
                  int maxWidth, int maxHeight, bool downscale,
                  bool allowLossyOriginal, int preferredQuality) {
    if (files.isEmpty()) {
        QMessageBox::information(parent, QObject::tr("No images"),
                                 QObject::tr("Import images first, then open Upload-ready."));
        return;
    }
    if (targetDir.trimmed().isEmpty()) {
        QMessageBox::warning(parent, QObject::tr("Output folder missing"),
                             QObject::tr("Choose an output folder in the main application first."));
        return;
    }
    const auto cancel = std::make_shared<std::atomic_bool>(false);
    const int totalSteps = qMax(1, static_cast<int>(files.size()) * 5);
    auto *progress = new QProgressDialog(
        QObject::tr("Preparing website upload..."),
        QObject::tr("Cancel remaining work"), 0, totalSteps, parent);
    progress->setAttribute(Qt::WA_DeleteOnClose, false);
    progress->setWindowModality(Qt::WindowModal);
    progress->setMinimumDuration(0);
    progress->setAutoClose(false);
    progress->setAutoReset(false);
    progress->setValue(0);
    progress->setMinimumWidth(450);
    progress->show();
    QObject::connect(progress, &QProgressDialog::canceled, parent, [cancel]() { cancel->store(true); });
    auto *watcher = new QFutureWatcher<Summary>(parent);
    const QPointer<QProgressDialog> guard(progress);
    QObject::connect(watcher, &QFutureWatcher<Summary>::finished, parent,
                     [watcher, guard, parent]() {
        const Summary report = watcher->result();
        if (guard) { guard->close(); guard->deleteLater(); }
        QStringList problems;
        for (const auto &row : report.rows)
            if (!row.success && problems.size() < 6)
                problems << QFileInfo(row.input).fileName() + ": " + row.message;
        QString msg = QObject::tr("Optimized: %1    Could not fit/convert: %2")
                          .arg(report.passed).arg(report.failed);
        if (report.cancelled) msg += QObject::tr("\nCancelled after the current image.");
        if (!report.reportPath.isEmpty()) msg += QObject::tr("\n\nDetailed report: %1").arg(report.reportPath);
        if (!problems.isEmpty()) msg += "\n\n" + problems.join("\n");
        QMessageBox::information(parent, QObject::tr("Upload-ready results"), msg);
        watcher->deleteLater();
    });
    const auto reportStage = [watcher, guard, totalSteps](int step, const QString &detail) {
        // Never touch Qt UI objects directly from the worker thread.
        QMetaObject::invokeMethod(watcher, [guard, step, totalSteps, detail]() {
            if (!guard || guard->wasCanceled()) return;
            guard->setLabelText(detail);
            guard->setValue(qBound(0, step, totalSteps));
        }, Qt::QueuedConnection);
    };
    watcher->setFuture(QtConcurrent::run([files, targetDir, maxWidth, maxHeight, downscale,
                                          allowLossyOriginal, preferredQuality, cancel, reportStage]() {
        return batch(files, targetDir, maxWidth, maxHeight, downscale,
                     allowLossyOriginal, preferredQuality, cancel, reportStage);
    }));
}

} // namespace PixelShroomUpload
