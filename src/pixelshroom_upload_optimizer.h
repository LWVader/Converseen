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
        return decoded.columns() == input.columns() &&
               decoded.rows() == input.rows() &&
               decoded.orientation() == input.orientation() &&
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
                                   bool downscale, int &width, int &height) {
    Magick::Image preview(input);
    const int iw = int(input.columns()), ih = int(input.rows());
    // Website uses the same bounding dimensions as the Resize tab. Do not
    // upscale a source that is already smaller; keep original aspect ratio.
    const int targetW = std::max(1, std::min(20000, maxWidth));
    const int targetH = std::max(1, std::min(20000, maxHeight));
    const double scale = std::min({1.0, double(targetW) / iw, double(targetH) / ih});
    if (scale < 1.0) {
        preview.filterType(Magick::LanczosFilter);
        preview.resize(Magick::Geometry(size_t(std::max(1, qRound(iw*scale))),
                                        size_t(std::max(1, qRound(ih*scale)))));
    }
    // Prefer highest resolution that meets the preview cap. At that resolution,
    // choose the smallest available lossless encoder output.
    for (int attempt=0; attempt<16; ++attempt) {
        BlobCandidate best;
        const bool sameSize = preview.columns() == input.columns() && preview.rows() == input.rows();
        if (sameSize && original.size() < PreviewLimit &&
            (suffix == "png" || suffix == "jpg" || suffix == "jpeg" || suffix == "webp")) {
            best = {original, "." + suffix, "unchanged source", true};
        }
        for (const QString codec : {QStringLiteral("webp"), QStringLiteral("png")}) {
            // WebP lossless has 8-bit RGBA semantics; PNG is the precision fallback.
            if (codec == "webp" && preview.depth() > 8) continue;
            try {
                BlobCandidate candidate = encode(preview, codec);
                if (candidate.valid && candidate.bytes.size() < PreviewLimit &&
                    (!best.valid || candidate.bytes.size() < best.bytes.size()))
                    best = std::move(candidate);
            } catch (const Magick::Exception &) { /* try alternate lossless format */ }
        }
        if (best.valid && best.bytes.size() < PreviewLimit) {
            width = int(preview.columns()); height = int(preview.rows());
            return best;
        }
        if (!downscale) break;
        if (std::max(preview.columns(), preview.rows()) <= 256) break;
        const size_t w = std::max<size_t>(1, size_t(std::floor(preview.columns()*0.80)));
        const size_t h = std::max<size_t>(1, size_t(std::floor(preview.rows()*0.80)));
        preview.filterType(Magick::LanczosFilter);
        preview.resize(Magick::Geometry(w,h));
    }
    throw std::runtime_error("Preview cannot reach 10 MiB within selected resolution rules");
}

inline Result process(const QString &sourcePath, const QString &targetDir,
                      int maxWidth, int maxHeight, bool downscale,
                      bool allowLossyOriginal, int preferredQuality) {
    Result result;
    result.input = sourcePath;
    try {
        const QFileInfo source(sourcePath);
        const QString suffix = source.suffix().toLower();
        if (!source.isFile()) throw std::runtime_error("Source file no longer exists");
        if (!(suffix == "png" || suffix == "jpeg" || suffix == "jpg" || suffix == "webp"))
            throw std::runtime_error("Only PNG, JPEG and WebP still images are supported for upload export");
        const QByteArray bytes = readSource(source.absoluteFilePath());
        const Magick::Blob inputBlob(bytes.constData(), size_t(bytes.size()));
        Magick::Image input(inputBlob);
        input.autoOrient(); // source is not mutated; preview follows its orientation
        if (input.columns() == 0 || input.rows() == 0)
            throw std::runtime_error("Image has invalid dimensions");
        if (input.columns() > 20000 || input.rows() > 20000 ||
            input.columns() * input.rows() > 120000000ULL)
            throw std::runtime_error("Image exceeds the 120-megapixel batch safety limit");
        // Preserve the exact input file when possible; compare other lossless
        // encodings only if re-reading proves pixel/profile/DPI equivalence.
        BlobCandidate original {bytes, "." + suffix, "unchanged source", true};
        // For EXIF-oriented images, avoid substituting auto-oriented decoded pixels
        // in the ORIGINAL: original remains a byte-for-byte copy.
        Magick::Image raw(inputBlob);
        for (const QString codec : {QStringLiteral("png"), QStringLiteral("webp")}) {
            if (codec == "webp" && raw.depth() > 8) continue;
            try {
                BlobCandidate candidate = encode(raw, codec);
                if (candidate.valid && candidate.bytes.size() < original.bytes.size() &&
                    originalEquivalent(raw, candidate))
                    original = std::move(candidate);
            } catch (const Magick::Exception &) { /* the original source remains safe */ }
        }
        if (original.bytes.size() >= OriginalLimit && allowLossyOriginal) {
            // A photograph or opaque 8-bit artwork can often reach 50 MiB
            // at high quality without changing its pixel dimensions.
            // 16-bit originals are not silently reduced to 8-bit.
            if (raw.depth() <= 8) {
#if MagickLibVersion < 0x700
                const bool hasAlpha = raw.matte();
#else
                const bool hasAlpha = raw.alpha();
#endif
                const QString codec = hasAlpha ? QStringLiteral("webp") : QStringLiteral("jpeg");
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
        int pw=0, ph=0;
        BlobCandidate preview = choosePreview(input, bytes, suffix, maxWidth, maxHeight, downscale, pw, ph);
        if (preview.bytes.size() >= PreviewLimit)
            throw std::runtime_error("Preview exceeds the 10 MiB limit");
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
                     const std::shared_ptr<std::atomic_bool> &cancel) {
    Summary result;
    if (!QDir(outDir).exists() && !QDir().mkpath(outDir)) {
        Result failed; failed.message = "Cannot create output directory";
        result.rows.append(failed); result.failed = files.size(); return result;
    }
    for (const QString &file : files) {
        if (cancel->load()) { result.cancelled = true; break; }
        Result row = process(file, outDir, maxWidth, maxHeight, downscale,
                             allowLossyOriginal, preferredQuality);
        if (row.success) ++result.passed; else ++result.failed;
        result.rows.append(std::move(row));
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
    auto *progress = new QProgressDialog(QObject::tr("Optimizing %1 images for upload...").arg(files.size()),
                                         QObject::tr("Cancel after current image"), 0, 0, parent);
    progress->setAttribute(Qt::WA_DeleteOnClose, false);
    progress->setWindowModality(Qt::WindowModal);
    progress->setMinimumDuration(0);
    progress->setAutoClose(false);
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
    watcher->setFuture(QtConcurrent::run([files, targetDir, maxWidth, maxHeight, downscale,
                                          allowLossyOriginal, preferredQuality, cancel]() {
        return batch(files, targetDir, maxWidth, maxHeight, downscale,
                     allowLossyOriginal, preferredQuality, cancel);
    }));
}

} // namespace PixelShroomUpload
