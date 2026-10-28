/*
* This file is part of Converseen, an open-source batch image converter
* and resizer.
*
* (C) Francesco Mondello 2009 - 2026
*
* This program is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* This program is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
* Contact e-mail: Francesco Mondello <faster3ck@gmail.com>
*
*/

#include <QColorDialog>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QComboBox>
#include <QCheckBox>
#include <QSpinBox>
#include <QDoubleSpinBox>
#include <QLabel>
#include <QPushButton>
#include <QSize>
#include <QTabWidget>
#include <QTabBar>
#include <QDialog>
#include <QImageReader>
#include <QPixmap>
#include <QFileInfo>
#include <QDesktopServices>
#include <QUrl>
#include <QGridLayout>
#include <QSlider>
#include <QSignalBlocker>
#include <QFrame>
#include <QToolButton>
#include <QHeaderView>
#include <QTimer>
#include <QStyleFactory>
#include <QImageReader>
#include <QtConcurrent>
#include <QFutureWatcher>
#include <QProgressDialog>
#include <string>
#include "mainwindowimpl.h"
#include "dialogoptions.h"
#include "dialoginfo.h"
#include "formats.h"
#include "inisettings.h"
#include "sizeutil.h"
#include "dialogmultipageeditor.h"
#ifndef DISABLE_CHECK_UPDATES
#include "dialogshowupdatemsg.h"
#endif
#include "globals.h"

using namespace Magick;
using namespace std;

MainWindowImpl::MainWindowImpl(QWidget * parent)
    : QMainWindow(parent)
{
    setupUi(this);

    iAList = new QList<ImageAttributes>;
    convertThread = new Converter(this);
    dlgCStatus = new DialogConversionStatus(this);
#ifndef DISABLE_CHECK_UPDATES
    updateChecker = new UpdateChecker();
#endif

    CachingSystem::init();

    connect(treeWidget, SIGNAL(dropped(QStringList, QStringList)), this, SLOT(dropped(QStringList, QStringList)));

    connect(bntSelDir, SIGNAL(clicked()), this, SLOT(openOutDirectory()));
    connect(checkSameDir, SIGNAL(stateChanged(int)), this, SLOT(setCurrentDirectory()));
    connect(btnFormatOptions, SIGNAL(clicked()), this, SLOT(setQuality()));
    connect(treeWidget, SIGNAL(itemSelectionChanged()), this, SLOT(onItemSelection()));

    connect(spin_geoWidth, SIGNAL(editingFinished()), this, SLOT(relativeSizeW()));
    connect(spin_geoHeight, SIGNAL(editingFinished()), this, SLOT(relativeSizeH()));

    connect(comboResizeValues, SIGNAL(currentTextChanged(QString)), this, SLOT(selectGeometryUnit(QString)));

    connect(checkRename, SIGNAL(stateChanged(int)), this, SLOT(enableRenameLine()));
    connect(radioPrefixSuffix, SIGNAL(clicked()), this, SLOT(enableProgressiveSpin()));
    connect(radioProgressive, SIGNAL(clicked()), this, SLOT(enableProgressiveSpin()));
    connect(checkShowPreview, SIGNAL(stateChanged(int)), this, SLOT(enableShowPreview()));

    connect(pushReset, SIGNAL(clicked()), this, SLOT(onPushResetClick()));

    connect(convertThread, SIGNAL(nextConversion(int)), this, SLOT(nextConversion(int)));
    connect(convertThread, SIGNAL(requestOverwrite(QString)), this, SLOT(overwriteDialog(QString)));
    connect(convertThread, SIGNAL(errorMessage(QString)), this, SLOT(errorMessage(QString)));

    connect(dlgCStatus, SIGNAL(stopProcess()), this, SLOT(stopProcess()));

    connect(pushColor, SIGNAL(clicked()), this, SLOT(choseBackgroundColor()));

    connect(labelPreview, SIGNAL(previewReady(int, int, double, double)), this, SLOT(showImageInformations(int, int, double, double)));

    connect(checkRelative, SIGNAL(stateChanged(int)), this, SLOT(setRelativeSizeCheckboxes(int)));
#ifndef DISABLE_CHECK_UPDATES
    connect(updateChecker, SIGNAL(updateAvailable(bool)), this, SLOT(updateAvailable(bool)));
#endif

    createActions();
    setupMenu();

    loadFormats();

    comboResizeValues->addItems((QStringList() << "%" << "px"));

    adjustSize();
    dockWidget->adjustSize();

    treeWidget->header()->setSectionResizeMode(0, QHeaderView::ResizeToContents);

    treeWidget->setContextMenuPolicy(Qt::CustomContextMenu);
    createContextMenu();

    loadOptions();
    setupPixelShroomControls();

    resetDisplays();

    spin_resX->setValue(0);
    spin_resY->setValue(0);

    if (comboResizeValues->currentText() == "%") {
        spin_geoWidth->setValue(100);
        spin_geoHeight->setValue(100);
    }
    if (comboResizeValues->currentText() == "px") {
        spin_geoWidth->setValue(1);
        spin_geoHeight->setValue(1);
    }

#ifndef DISABLE_CHECK_UPDATES
    checkForUpdates();
#endif

    checkVersion();
}

void MainWindowImpl::setupPixelShroomControls()
{
    // Phase 2: Squoosh-inspired, accessible tabs; no changes to the batch engine.
    auto *panel = new QFrame(centralwidget);
    panel->setObjectName("psStudioPanel");
    panel->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Maximum);
    panel->setStyleSheet(R"PSCSS(
        QFrame#psStudioPanel { background: #20252b; border: 1px solid #4a5662;
            border-radius: 8px; color: #f4f6f8; }
        QFrame#psStudioPanel QLabel, QFrame#psStudioPanel QCheckBox {
            color: #f4f6f8; border: none; background: transparent; }
        QFrame#psStudioPanel QTabWidget::pane { border: 0; background: #20252b; }
        QWidget#psResizeTab, QWidget#psCompressTab, QWidget#psEnhanceTab {
            background: #20252b; }
        QFrame#psStudioPanel QTabBar::tab { background: #303941; color: #e8eef4;
            min-width: 78px; padding: 9px 15px; border: 0; }
        QFrame#psStudioPanel QTabBar::tab:selected { background: #68b9e7; color: #121c28; }
        QFrame#psStudioPanel QComboBox, QFrame#psStudioPanel QSpinBox,
        QFrame#psStudioPanel QDoubleSpinBox { color: #f5f7f9; background: #323941;
            border: 1px solid #63717e; border-radius: 4px; min-height: 27px;
            padding: 2px 7px; }
        QFrame#psStudioPanel QPushButton, QFrame#psStudioPanel QToolButton {
            color: #f4f6f8; background: #364650; border: 1px solid #667a89;
            border-radius: 4px; padding: 5px 9px; }
        QFrame#psStudioPanel QSlider::groove:horizontal {
            height: 5px; background: #647783; border-radius: 2px; }
        QFrame#psStudioPanel QSlider::handle:horizontal { background: #68b9e7;
            border-radius: 8px; width: 16px; margin: -6px 0; }
    )PSCSS");
    auto *root = new QVBoxLayout(panel);
    root->setContentsMargins(12, 10, 12, 9);
    root->setSpacing(7);
    auto *heading = new QHBoxLayout();
    auto *title = new QLabel(tr("PIXEL SHROOM  |  IMAGE STUDIO"), panel);
    QFont titleFont = title->font();
    titleFont.setBold(true);
    title->setFont(titleFont);
    heading->addWidget(title, 1);

    // Pixel Shroom Phase 4: compare the selected original with an actual exported image.
    // This compares real files AFTER conversion, not a simulated encoder preview.
    auto *compareOutput = new QPushButton(tr("Compare output..."), panel);
    compareOutput->setToolTip(tr("Compare your selected input with an exported JPEG, PNG or WebP file."));
    heading->addWidget(compareOutput);
    connect(compareOutput, &QPushButton::clicked, this, [this]() {
        const int selectedRow = treeWidget->currentIndex().row();
        if (selectedRow < 0 || selectedRow >= iAList->size()) {
            QMessageBox::information(this, tr("Choose an original"),
                                     tr("Select an imported image in the list first."));
            return;
        }
        const QString originalPath = iAList->at(selectedRow).completeFileName;
        if (!QFileInfo::exists(originalPath)) {
            QMessageBox::warning(this, tr("Original unavailable"),
                                 tr("The selected source file could not be found."));
            return;
        }
        const QString suggestedFolder = checkSameDir->isChecked()
            ? QFileInfo(originalPath).absolutePath() : lineDirectory->text();
        const QString exportedPath = QFileDialog::getOpenFileName(
            this, tr("Select your converted image"), suggestedFolder,
            tr("Artwork (*.png *.jpg *.jpeg *.webp *.tif *.tiff);;All files (*.*)"));
        if (exportedPath.isEmpty())
            return;

        QDialog dlg(this);
        dlg.setWindowTitle(tr("Pixel Shroom | Compare original and output"));
        dlg.resize(1010, 620);
        dlg.setMinimumSize(720, 480);
        dlg.setStyleSheet(R"PSCMP(
            QDialog { background: #20252b; }
            QLabel { color: #eff4f7; }
            QLabel#psComparisonImage { background: #12171d; border: 1px solid #607381;
                border-radius: 5px; padding: 6px; }
            QPushButton { color: #f6f8fa; background: #364650;
                border: 1px solid #63798b; padding: 6px 12px; border-radius: 4px; }
        )PSCMP");
        auto *layout = new QVBoxLayout(&dlg);
        layout->setContentsMargins(14, 12, 14, 12);
        auto *headingLabel = new QLabel(tr("ORIGINAL  /  CONVERTED OUTPUT"), &dlg);
        QFont comparisonTitleFont = headingLabel->font();
        comparisonTitleFont.setBold(true);
        headingLabel->setFont(comparisonTitleFont);
        layout->addWidget(headingLabel);
        auto *columns = new QHBoxLayout();
        columns->setSpacing(14);
        layout->addLayout(columns, 1);

        QLabel *originalImage = nullptr;
        QLabel *exportedImage = nullptr;
        QLabel *originalDetails = nullptr;
        QLabel *exportedDetails = nullptr;
        auto addPane = [&dlg, columns](const QString &name,
                                       QLabel *&imageLabel, QLabel *&detailsLabel) {
            auto *pane = new QVBoxLayout();
            auto *paneTitle = new QLabel(name, &dlg);
            pane->addWidget(paneTitle);
            imageLabel = new QLabel(&dlg);
            imageLabel->setObjectName("psComparisonImage");
            imageLabel->setMinimumSize(240, 280);
            imageLabel->setAlignment(Qt::AlignCenter);
            imageLabel->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
            pane->addWidget(imageLabel, 1);
            detailsLabel = new QLabel(&dlg);
            detailsLabel->setWordWrap(true);
            pane->addWidget(detailsLabel);
            columns->addLayout(pane, 1);
        };
        addPane(tr("BEFORE | ORIGINAL"), originalImage, originalDetails);
        addPane(tr("AFTER | EXPORTED FILE"), exportedImage, exportedDetails);

        auto loadPane = [](const QString &path, QLabel *imageLabel, QLabel *detailsLabel,
                           double *readDpiX, double *readDpiY) -> QSize {
            if (readDpiX) *readDpiX = 0.0;
            if (readDpiY) *readDpiY = 0.0;
            QImageReader reader(path);
            reader.setAutoTransform(true);
            const QSize actualPixels = reader.size();
            if (actualPixels.isValid())
                reader.setScaledSize(actualPixels.scaled(420, 380, Qt::KeepAspectRatio));
            const QImage preview = reader.read();
            const QFileInfo file(path);
            if (preview.isNull()) {
                imageLabel->setText(QObject::tr("No Qt preview available for this format"));
                detailsLabel->setText(file.fileName() + "\n" + reader.errorString());
                return actualPixels;
            }
            imageLabel->setPixmap(QPixmap::fromImage(preview));
            // Read physical resolution from the ACTUAL file, not from a downscaled
            // Qt preview (which can report a misleading default of 96 DPI).
            double embeddedX = 0.0;
            double embeddedY = 0.0;
            QString dpiLabel = QObject::tr("Embedded DPI: not specified");
            try {
                Magick::Image fileMetadata;
                fileMetadata.ping(path.toStdString());
                const auto units = fileMetadata.resolutionUnits();
                const double toDpi = (units == Magick::PixelsPerCentimeterResolution)
                    ? 2.54 : 1.0;
                if (units == Magick::PixelsPerCentimeterResolution ||
                    units == Magick::PixelsPerInchResolution) {
                    embeddedX = fileMetadata.xResolution() * toDpi;
                    embeddedY = fileMetadata.yResolution() * toDpi;
                    if (embeddedX > 0.0 && embeddedY > 0.0) {
                        dpiLabel = QObject::tr("Embedded print DPI: %1 × %2")
                            .arg(qRound(embeddedX)).arg(qRound(embeddedY));
                    }
                }
            } catch (const Magick::Exception &e) {
                dpiLabel = QObject::tr("Embedded DPI unavailable: %1")
                    .arg(QString::fromStdString(e.what()));
            }
            if (readDpiX) *readDpiX = embeddedX;
            if (readDpiY) *readDpiY = embeddedY;
            detailsLabel->setText(QObject::tr("%1\n%2 × %3 pixels  |  %4 MiB\n%5")
                .arg(file.fileName())
                .arg(actualPixels.width()).arg(actualPixels.height())
                .arg(QString::number(file.size() / 1048576.0, 'f', 2))
                .arg(dpiLabel));
            return actualPixels;
        };
        const QSize originalSize = loadPane(originalPath, originalImage, originalDetails, nullptr, nullptr);
        double psOutputDpiX = 0.0;
        double psOutputDpiY = 0.0;
        const QSize exportedSize = loadPane(exportedPath, exportedImage, exportedDetails,
                                            &psOutputDpiX, &psOutputDpiY);

        auto *summary = new QLabel(&dlg);
        summary->setWordWrap(true);
        if (originalSize.isValid() && exportedSize.isValid()) {
            const double scaleX = static_cast<double>(exportedSize.width()) / originalSize.width();
            const double scaleY = static_cast<double>(exportedSize.height()) / originalSize.height();
            if (scaleX > 2.0 || scaleY > 2.0) {
                summary->setText(QObject::tr("Upscaling: %1× width and %2× height. More pixels do not automatically create more fine detail.")
                    .arg(QString::number(scaleX, 'f', 2))
                    .arg(QString::number(scaleY, 'f', 2)));
                summary->setStyleSheet("color: #ffd49c; font-weight: bold;");
            } else {
                summary->setText(QObject::tr("Viewing the actual converted image. Open the full-size export to inspect fine details at 100%."));
            }
        } else {
            summary->setText(QObject::tr("Dimensions could not be read for one of the files."));
        }
        // Print verification uses the actual saved file's embedded units.
        if (auto *studioPrintDpi = findChild<QCheckBox*>("psPrintDpi")) {
            if (studioPrintDpi->isChecked()) {
                if (auto *studioDpiValue = findChild<QSpinBox*>("psDpiValue")) {
                    const int wanted = studioDpiValue->value();
                    if (psOutputDpiX <= 0.0 || psOutputDpiY <= 0.0 ||
                        qAbs(psOutputDpiX - wanted) > 2.0 ||
                        qAbs(psOutputDpiY - wanted) > 2.0) {
                        summary->setText(summary->text() +
                            QObject::tr("\nWARNING: Export does not contain the expected %1 DPI metadata.")
                                .arg(wanted));
                        summary->setStyleSheet("color: #ffd49c; font-weight: bold;");
                    } else {
                        summary->setText(summary->text() +
                            QObject::tr("\nPrint DPI verified: %1 × %2 DPI embedded in exported file.")
                                .arg(qRound(psOutputDpiX)).arg(qRound(psOutputDpiY)));
                    }
                }
            }
        }
        layout->addWidget(summary);
        auto *buttons = new QHBoxLayout();
        buttons->addStretch();
        auto *openExport = new QPushButton(tr("Open exported file"), &dlg);
        connect(openExport, &QPushButton::clicked, &dlg, [exportedPath]() {
            QDesktopServices::openUrl(QUrl::fromLocalFile(exportedPath));
        });
        buttons->addWidget(openExport);
        auto *closeButton = new QPushButton(tr("Close"), &dlg);
        connect(closeButton, &QPushButton::clicked, &dlg, &QDialog::accept);
        buttons->addWidget(closeButton);
        layout->addLayout(buttons);
        dlg.exec();
    });
    auto *collapse = new QToolButton(panel);
    collapse->setText(tr("Hide controls"));
    collapse->setCheckable(true);
    collapse->setChecked(true);
    heading->addWidget(collapse);
    root->addLayout(heading);

    auto *tabs = new QTabWidget(panel);
    tabs->setDocumentMode(true);
    // Fill the full tab header width rather than leaving a white empty strip.
    tabs->tabBar()->setExpanding(true);
    root->addWidget(tabs);
    connect(collapse, &QToolButton::toggled, this, [tabs, collapse](bool expanded) {
        tabs->setVisible(expanded);
        collapse->setText(expanded ? QObject::tr("Hide controls") : QObject::tr("Show controls"));
    });

    // Resize tab: exact pixel boxes, existing aspect-fit behavior, print DPI and filters.
    auto *resizeTab = new QWidget(tabs);
    resizeTab->setObjectName("psResizeTab");
    auto *sizeGrid = new QGridLayout(resizeTab);
    sizeGrid->setContentsMargins(8, 12, 8, 10);
    sizeGrid->setHorizontalSpacing(14);
    sizeGrid->setVerticalSpacing(10);
    auto *preset = new QComboBox(resizeTab);
    preset->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Fixed);
    preset->addItem(tr("Custom (use size below)"), QSize());
    preset->addItem(tr("16 x 16 in  |  4800 x 4800"), QSize(4800, 4800));
    preset->addItem(tr("16 x 20 in  |  4800 x 6000"), QSize(4800, 6000));
    preset->addItem(tr("24 x 24 in  |  7200 x 7200"), QSize(7200, 7200));
    preset->addItem(tr("24 x 30 in  |  7200 x 9000"), QSize(7200, 9000));
    preset->addItem(tr("Web  |  600 x 600"), QSize(600, 600));
    preset->addItem(tr("Web  |  2048 x 2048"), QSize(2048, 2048));
    sizeGrid->addWidget(new QLabel(tr("Preset"), resizeTab), 0, 0);
    sizeGrid->addWidget(preset, 0, 1, 1, 3);
    auto *width = new QSpinBox(resizeTab);
    auto *height = new QSpinBox(resizeTab);
    for (auto *spin : {width, height}) {
        spin->setRange(1, 100000);
        spin->setSingleStep(100);
        spin->setSuffix(tr(" px"));
        spin->setMinimumWidth(120);
    }
    width->setValue(comboResizeValues->currentText() == "px" && spin_geoWidth->value() > 1
                    ? qRound(spin_geoWidth->value()) : 2048);
    height->setValue(comboResizeValues->currentText() == "px" && spin_geoHeight->value() > 1
                     ? qRound(spin_geoHeight->value()) : 2048);
    sizeGrid->addWidget(new QLabel(tr("Width"), resizeTab), 1, 0);
    sizeGrid->addWidget(width, 1, 1);
    sizeGrid->addWidget(new QLabel(tr("Height"), resizeTab), 1, 2);
    sizeGrid->addWidget(height, 1, 3);
    auto *keepAspect = new QCheckBox(tr("Keep aspect ratio (fit inside, no crop)"), resizeTab);
    keepAspect->setChecked(checkRelative->isChecked());
    sizeGrid->addWidget(keepAspect, 2, 0, 1, 4);

    auto *filter = new QComboBox(resizeTab);
    filter->addItem(tr("Automatic"), static_cast<int>(UndefinedFilter));
    filter->addItem(tr("Lanczos - crisp detail"), static_cast<int>(LanczosFilter));
    filter->addItem(tr("Mitchell - smooth edges"), static_cast<int>(MitchellFilter));
    filter->addItem(tr("Catrom - sharp edges"), static_cast<int>(CatromFilter));
    filter->addItem(tr("Triangle - soft"), static_cast<int>(TriangleFilter));
    int currentFilter = filter->findData(static_cast<int>(m_resamplingFilter));
    filter->setCurrentIndex(currentFilter >= 0 ? currentFilter : 0);
    sizeGrid->addWidget(new QLabel(tr("Resize method"), resizeTab), 3, 0);
    sizeGrid->addWidget(filter, 3, 1, 1, 3);
    connect(filter, QOverload<int>::of(&QComboBox::currentIndexChanged), this,
            [this, filter](int index) {
        if (index >= 0)
            m_resamplingFilter = static_cast<IMFilterType>(filter->itemData(index).toInt());
    });

    auto *printDpi = new QCheckBox(tr("Print resolution"), resizeTab);
    printDpi->setObjectName("psPrintDpi");
    printDpi->setChecked(groupResolution->isChecked());
    auto *dpi = new QSpinBox(resizeTab);
    dpi->setObjectName("psDpiValue");
    dpi->setRange(72, 1200);
    dpi->setValue(spin_resX->value() >= 72 ? qRound(spin_resX->value()) : 300);
    dpi->setSuffix(tr(" DPI"));
    dpi->setEnabled(printDpi->isChecked());
    sizeGrid->addWidget(printDpi, 4, 0);
    sizeGrid->addWidget(dpi, 4, 1);
    auto *note = new QLabel(tr("Print presets use 300 DPI. Aspect-fit prevents stretching; output may not fill a different-shaped canvas."), resizeTab);
    note->setWordWrap(true);
    sizeGrid->addWidget(note, 5, 0, 1, 4);
    sizeGrid->setColumnStretch(1, 1);
    sizeGrid->setColumnStretch(3, 1);
    tabs->addTab(resizeTab, tr("Resize"));

    auto applySize = [this, width, height, keepAspect]() {
        groupDimensions->setChecked(true);
        comboResizeValues->setCurrentText("px"); // Native control resets size when units change.
        checkRelative->setChecked(keepAspect->isChecked());
        spin_geoWidth->setValue(width->value());
        spin_geoHeight->setValue(height->value());
        showNewSizePreview();
    };
    connect(width, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [applySize](int) { applySize(); });
    connect(height, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [applySize](int) { applySize(); });
    connect(keepAspect, &QCheckBox::toggled, this,
            [applySize](bool) { applySize(); });
    connect(preset, QOverload<int>::of(&QComboBox::currentIndexChanged), this,
            [this, preset, width, height, keepAspect, dpi, printDpi, applySize](int index) {
        if (index < 1)
            return;
        const QSize target = preset->itemData(index).toSize();
        if (!target.isValid())
            return;
        {
            const QSignalBlocker blockWidth(width);
            const QSignalBlocker blockHeight(height);
            width->setValue(target.width());
            height->setValue(target.height());
        }
        {
            const QSignalBlocker blockAspect(keepAspect);
            keepAspect->setChecked(true); // Presets fit the art without cropping/stretching.
        }
        const bool isPrint = index <= 4;
        if (isPrint)
            dpi->setValue(300);
        printDpi->setChecked(isPrint);
        applySize();
        statusBar()->showMessage(tr("Preset applied. Choose a matching aspect ratio for exact canvas dimensions."), 7000);
    });
    connect(printDpi, &QCheckBox::toggled, this, [this, dpi](bool enabled) {
        dpi->setEnabled(enabled);
        groupResolution->setChecked(enabled);
        if (enabled) {
            spin_resX->setValue(dpi->value());
            spin_resY->setValue(dpi->value());
        }
    });
    connect(dpi, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [this, printDpi](int value) {
        if (printDpi->isChecked()) {
            spin_resX->setValue(value);
            spin_resY->setValue(value);
        }
    });

    // Compress tab: Squoosh-style quality slider + exact value, opt-in.
    auto *compressTab = new QWidget(tabs);
    compressTab->setObjectName("psCompressTab");
    auto *compressGrid = new QGridLayout(compressTab);
    compressGrid->setContentsMargins(8, 12, 8, 10);
    compressGrid->setHorizontalSpacing(14);
    compressGrid->setVerticalSpacing(12);
    auto *overrideQuality = new QCheckBox(tr("Use custom quality for JPEG / WebP"), compressTab);
    auto *qualitySlider = new QSlider(Qt::Horizontal, compressTab);
    auto *qualityNumber = new QSpinBox(compressTab);
    qualitySlider->setRange(1, 100);
    qualitySlider->setValue(m_psQuality);
    qualityNumber->setRange(1, 100);
    qualityNumber->setValue(m_psQuality);
    qualityNumber->setMinimumWidth(75);
    qualitySlider->setEnabled(false);
    qualityNumber->setEnabled(false);
    compressGrid->addWidget(overrideQuality, 0, 0, 1, 3);
    compressGrid->addWidget(new QLabel(tr("Quality"), compressTab), 1, 0);
    compressGrid->addWidget(qualitySlider, 1, 1);
    compressGrid->addWidget(qualityNumber, 1, 2);
    auto *compressHint = new QLabel(tr("Higher quality = more detail and larger files. PNG stays lossless. WebP switches to lossy when this override is on."), compressTab);
    compressHint->setWordWrap(true);
    compressGrid->addWidget(compressHint, 2, 0, 1, 3);
    auto *advanced = new QPushButton(tr("Advanced compression / format settings..."), compressTab);
    compressGrid->addWidget(advanced, 3, 0, 1, 3);
    compressGrid->setColumnStretch(1, 1);
    connect(overrideQuality, &QCheckBox::toggled, this, [this, qualitySlider, qualityNumber](bool on) {
        m_psOverrideQuality = on;
        qualitySlider->setEnabled(on);
        qualityNumber->setEnabled(on);
    });
    connect(qualitySlider, &QSlider::valueChanged, qualityNumber, &QSpinBox::setValue);
    connect(qualityNumber, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [this, qualitySlider](int val) {
        qualitySlider->setValue(val);
        m_psQuality = val;
    });
    connect(advanced, &QPushButton::clicked, this, [this, filter]() {
        setQuality();
        const int idx = filter->findData(static_cast<int>(m_resamplingFilter));
        if (idx >= 0) {
            const QSignalBlocker b(filter);
            filter->setCurrentIndex(idx);
        }
    });
    tabs->addTab(compressTab, tr("Compress"));

    // Enhance tab: independent subtle blur / detail sharpening, both off by default.
    auto *enhanceTab = new QWidget(tabs);
    enhanceTab->setObjectName("psEnhanceTab");
    auto *enhanceGrid = new QGridLayout(enhanceTab);
    enhanceGrid->setContentsMargins(8, 12, 8, 10);
    enhanceGrid->setHorizontalSpacing(14);
    enhanceGrid->setVerticalSpacing(12);
    auto makeEnhancement = [this, enhanceTab, enhanceGrid](int row, const QString &label,
                                                            const QString &help, bool smoothing) {
        auto *caption = new QLabel(label, enhanceTab);
        auto *slider = new QSlider(Qt::Horizontal, enhanceTab);
        auto *number = new QDoubleSpinBox(enhanceTab);
        slider->setRange(0, 20);
        slider->setValue(0);
        slider->setSingleStep(1);
        number->setDecimals(1);
        number->setRange(0.0, 2.0);
        number->setSingleStep(0.1);
        number->setValue(0.0);
        number->setMinimumWidth(78);
        slider->setToolTip(help);
        number->setToolTip(help);
        enhanceGrid->addWidget(caption, row, 0);
        enhanceGrid->addWidget(slider, row, 1);
        enhanceGrid->addWidget(number, row, 2);
        connect(slider, &QSlider::valueChanged, this, [this, number, smoothing](int val) {
            const double sigma = val / 10.0;
            number->setValue(sigma);
            if (smoothing) m_psSmoothSigma = sigma;
            else m_psSharpenSigma = sigma;
        });
        connect(number, QOverload<double>::of(&QDoubleSpinBox::valueChanged), this,
                [slider](double val) { slider->setValue(qRound(val * 10.0)); });
    };
    makeEnhancement(0, tr("Smoothing"), tr("Gaussian smoothing, 0 = off; try 0.2-0.4"), true);
    makeEnhancement(1, tr("Sharpen"), tr("Sharpen after resizing, 0 = off; try 0.3-0.7"), false);
    auto *enhanceHint = new QLabel(tr("Both are off at 0. Start gently: strong smoothing removes texture; strong sharpening adds halos."), enhanceTab);
    enhanceHint->setWordWrap(true);
    enhanceGrid->addWidget(enhanceHint, 2, 0, 1, 3);
    enhanceGrid->setColumnStretch(1, 1);
    tabs->addTab(enhanceTab, tr("Enhance"));

    // Honor native advanced editing (e.g., if user changes existing resize fields).
    connect(spin_geoWidth, QOverload<double>::of(&QDoubleSpinBox::valueChanged), this,
            [this, width](double value) {
        if (comboResizeValues->currentText() != "px") return;
        const QSignalBlocker b(width);
        width->setValue(qMax(1, qRound(value)));
    });
    connect(spin_geoHeight, QOverload<double>::of(&QDoubleSpinBox::valueChanged), this,
            [this, height](double value) {
        if (comboResizeValues->currentText() != "px") return;
        const QSignalBlocker b(height);
        height->setValue(qMax(1, qRound(value)));
    });
    connect(checkRelative, &QCheckBox::toggled, this, [keepAspect](bool on) {
        const QSignalBlocker b(keepAspect);
        keepAspect->setChecked(on);
    });

    // Avoid the compressed single-row toolbar seen in Phase 1.
    verticalLayout_20->insertWidget(0, panel);

    // Pixel Shroom Phase 3: hide the native Dimensions tab, not its widgets.
    // Phase 2 deliberately updates groupDimensions, spin_geoWidth/Height,
    // checkRelative, and groupResolution behind the scenes. Removing or
    // disabling them could break the already-working conversion logic.
    // Keep the Rotate and Flip page available in the Actions Panel.
    const int nativeDimensionsTab = tabWidget->indexOf(tab);
    const int rotateFlipTab = tabWidget->indexOf(tab_2);
    if (nativeDimensionsTab >= 0 && rotateFlipTab >= 0) {
        tabWidget->setCurrentIndex(rotateFlipTab);
        tabWidget->setTabVisible(nativeDimensionsTab, false);
        tabWidget->setTabText(rotateFlipTab, tr("Rotate / Flip"));
    }
}

MainWindowImpl::~MainWindowImpl()
{
    saveSettings();
}

void MainWindowImpl::importListFromArgv(QString fileName)
{
    QFile file(fileName);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
        return;

    QString text = file.readAll();
    QStringList rawlist = text.split("\n");

    QStringList list;

    for (int i = 0; i < rawlist.count(); i++) {
        QFileInfo fi(rawlist.at(i));
        if (Formats::readableFilters().contains(fi.suffix(), Qt::CaseInsensitive))
            list << rawlist.at(i);
    }

    loadFiles(list);
}

void MainWindowImpl::printSupportedFormats()
{
    Formats::printSupportedFormats();
}

void MainWindowImpl::createActions()
{
    // "File" actions
    connect(actionOpenFiles, SIGNAL(triggered()), this, SLOT(openFiles()));
    connect(actionAddDirectory, SIGNAL(triggered()), this, SLOT(openImportDirectoryDialog()));
    connect(actionAddFiles, SIGNAL(triggered()), this, SLOT(addFiles()));
    connect(actionImportWindowsIconIco, SIGNAL(triggered()), this, SLOT(importIcoFile()));
    connect(actionImportPDFFile, SIGNAL(triggered()), this, SLOT(importPdfFile()));

    connect(actionShowOptions, SIGNAL(triggered()), this, SLOT(editSettings()));
    connect(actionClose, SIGNAL(triggered()), this, SLOT(close()));

    // "Edit" actions
    connect(actionCheckItems, SIGNAL(triggered()), treeWidget, SLOT(checkItems()));
    connect(actionCheckAllItems, SIGNAL(triggered()), treeWidget, SLOT(checkAllItems()));

    connect(actionUncheckItems, SIGNAL(triggered()), treeWidget, SLOT(uncheckItems()));
    connect(actionUncheckAllItems, SIGNAL(triggered()), treeWidget, SLOT(uncheckAllItems()));
    connect(actionInvertCheckedItems, SIGNAL(triggered()), treeWidget, SLOT(invertCheckAllItems()));

    connect(actionRemoveItems, SIGNAL(triggered()), this, SLOT(removeItems()));
    connect(actionRemoveAllItems, SIGNAL(triggered()), this, SLOT(removeAllItems()));

    // "Actions" actions
    connect(actionConvert, SIGNAL(triggered()), this, SLOT(elabora()));

    connect(actionInfo, SIGNAL(triggered()), this, SLOT(about()));
    connect(actionDonatePaypal, SIGNAL(triggered()), this, SLOT(openPaypalLink()));
    connect(actionReportBug, SIGNAL(triggered()), this, SLOT(bugReport()));
#ifndef DISABLE_CHECK_UPDATES
    connect(actionCheckForUpdates, SIGNAL(triggered()), this, SLOT(manualCheckForUpdate()));
#else
    actionCheckForUpdates->setVisible(false);
#endif
    connect(actionHelp, SIGNAL(triggered()), this, SLOT(onlineHelp()));

    // Create first toolbar button

    QToolButton *openFileButton = new QToolButton(this);

    openFileButton->setPopupMode(QToolButton::InstantPopup);
    openFileButton->setToolButtonStyle(Qt::ToolButtonTextBesideIcon);

    QMenu *openMenu = new QMenu(openFileButton);
    openMenu->addAction(actionOpenFiles);
    openMenu->addAction(actionAddDirectory);
    openFileButton->setMenu(openMenu);

    //toolBar->addWidget(openFileButton);
    toolBar->insertWidget(toolBar->actions().first(), openFileButton);
    openFileButton->setDefaultAction(actionOpenFiles);
}

void MainWindowImpl::setupMenu()
{
    menu_File->addAction(actionOpenFiles);
    menu_File->addAction(actionAddFiles);
    menu_File->addSeparator();
    menu_File->addAction(actionImportWindowsIconIco);
    menu_File->addAction(actionImportPDFFile);
    menu_File->addSeparator();
    menu_File->addAction(actionShowOptions);
    menu_File->addSeparator();
    menu_File->addAction(actionClose);

    menu_Edit->addAction(actionRemoveItems);
    menu_Edit->addAction(actionRemoveAllItems);
    menu_Edit->addSeparator();
    menu_Edit->addAction(actionCheckItems);
    menu_Edit->addAction(actionCheckAllItems);
    menu_Edit->addAction(actionUncheckItems);
    menu_Edit->addAction(actionUncheckAllItems);
    menu_Edit->addSeparator();
    menu_Edit->addAction(actionInvertCheckedItems);
    menu_Edit->addSeparator();

    menu_Actions->addAction(actionConvert);

    //menu_About->addAction(actionInfo);
}

void MainWindowImpl::createContextMenu()
{
    treeWidget->setContextMenuPolicy(Qt::ActionsContextMenu);
    treeWidget->addAction(actionCheckItems);
    treeWidget->addAction(actionCheckAllItems);
    treeWidget->addAction(actionUncheckItems);
    treeWidget->addAction(actionUncheckAllItems);
    addContextMenuSeparator();
    treeWidget->addAction(actionInvertCheckedItems);
    addContextMenuSeparator();
    treeWidget->addAction(actionRemoveItems);
    treeWidget->addAction(actionRemoveAllItems);
}

void MainWindowImpl::addContextMenuSeparator()
{
    QAction* separator = new QAction(this);
    separator->setSeparator(true);
    treeWidget->addAction(separator);
}

void MainWindowImpl::openFiles()
{
    iAList->clear();
    addFiles();
}

void MainWindowImpl::addFiles()
{
    CachingSystem::clear();

    QString path = IniSettings::latestOpenedDir();

    QString readableFiltersString = Formats::readableFiltersString();
    QStringList fileNames = QFileDialog::getOpenFileNames(this,
                                                          tr("Open Image"), path,
                                                          readableFiltersString);

    if (!fileNames.isEmpty())
        loadFiles(fileNames);
}

void MainWindowImpl::openImportDirectoryDialog()
{
    QStringList fileNames;
    QDirIterator::IteratorFlag flag;

    QStringList readableFiltersList = Formats::readableFormattedFilters();

    QString dir = QFileDialog::getExistingDirectory(this, tr("Open Directory"),
                                                    QDir::homePath(),
                                                    QFileDialog::ShowDirsOnly
                                                        | QFileDialog::DontResolveSymlinks);

    if (!dir.isNull()) {
        int ret = QMessageBox::question(this, QApplication::applicationName(),
                                        tr("Do you want to import subfolders as well?"),
                                        QMessageBox::Yes | QMessageBox::No
                                            | QMessageBox::Cancel);

        switch (ret) {
        case QMessageBox::Yes:
            flag = QDirIterator::Subdirectories;
            break;
        case QMessageBox::No:
            flag = QDirIterator::NoIteratorFlags;
            break;
        case QMessageBox::Cancel:
            return;
        default:
            return;
        }

        loadDirectoryFiles(dir, readableFiltersList, flag);

        /*fileNames = loadDirectoryFiles(dir, readableFiltersList, flag);

        if (!fileNames.isEmpty())
            loadFiles(fileNames);*/
    }
}

void MainWindowImpl::importIcoFile()
{
    QString path = IniSettings::latestOpenedDir();

    QString fileName = QFileDialog::getOpenFileName(this,
        tr("Open Icon file"), path, tr("Microsoft icon (*.ico *.icon)"));

    if (!fileName.isEmpty())
        openMultipageFile(fileName);
}

void MainWindowImpl::importPdfFile()
{
    QString path = IniSettings::latestOpenedDir();

    QString fileName = QFileDialog::getOpenFileName(this,
        tr("Open Pdf file"), path, tr("Portable Document Format (*.pdf)"));

    if (!fileName.isEmpty())
        openMultipageFile(fileName);
}

void MainWindowImpl::openMultipageFile(QString fileName)
{
    DialogMultipageEditor *dlg = new DialogMultipageEditor(this);

    statusBar()->showMessage(tr("Analyzing the file. It may take a while, please wait..."));
    QApplication::setOverrideCursor(QCursor(Qt::WaitCursor));
    dlg->readFile(fileName);
    QApplication::restoreOverrideCursor();
    statusBar()->clearMessage();

    dlg->exec();

    if (dlg->result() == 1) {
        QStringList fileNames = dlg->fileNames();
        loadFiles(fileNames);
    }
}

void MainWindowImpl::dropped(QStringList fileNames, QStringList directories)
{
    if (!fileNames.isEmpty())
        loadFiles(fileNames);


    if (!directories.isEmpty()) {
        QDirIterator::IteratorFlag flag;
        QStringList readableFiltersList = Formats::readableFormattedFilters();

        QString msg = QString(tr("You are going to import %1 directories. Do you want to import subfolders as well?")
                                  .arg(QString::number(directories.count())));

        int ret = QMessageBox::question(this, QApplication::applicationName(),
                                        msg,
                                        QMessageBox::Yes | QMessageBox::No
                                            | QMessageBox::Cancel);

        switch (ret) {
        case QMessageBox::Yes:
            flag = QDirIterator::Subdirectories;
            break;
        case QMessageBox::No:
            flag = QDirIterator::NoIteratorFlags;
            break;
        case QMessageBox::Cancel:
            return;
        default:
            return;
        }

        for (int i = 0; i < directories.count(); i++) {
            loadDirectoryFiles(directories.at(i), readableFiltersList, flag);
        }
    }
}

void MainWindowImpl::loadDirectoryFiles(
    const QString &directory,
    const QStringList &readableFiltersList,
    const QDirIterator::IteratorFlag &flag)
{
    auto *progress = new QProgressDialog(
        tr("Scanning folders for images..."),
        QString(),
        0,
        0,
        this);

    progress->setWindowTitle(QApplication::applicationName());
    progress->setSizeGripEnabled(false);
    progress->setFixedSize(progress->sizeHint());
    progress->setWindowModality(Qt::ApplicationModal);
    progress->setCancelButton(nullptr);
    progress->setMinimumDuration(0);

    QApplication::setOverrideCursor(Qt::WaitCursor);
    progress->show();

    auto *watcher = new QFutureWatcher<QStringList>(this);

    connect(watcher, &QFutureWatcher<QStringList>::finished,
            this, [this, watcher, progress]()
            {
                const QStringList fileNames = watcher->result();

                if (!fileNames.isEmpty())
                    loadFiles(fileNames);

                progress->close();
                progress->deleteLater();

                QApplication::restoreOverrideCursor();

                watcher->deleteLater();
            });

    watcher->setFuture(QtConcurrent::run(
        [directory, readableFiltersList, flag]()
        {
            QStringList fileNames;

            QDirIterator it(directory,
                            readableFiltersList,
                            QDir::Files,
                            flag);

            while (it.hasNext())
                fileNames << it.next();

            return fileNames;
        }));
}

void MainWindowImpl::loadFiles(QStringList fileNames)
{
    treeWidget->clear();

    QFileInfo fi(fileNames.at(0));
    IniSettings::setLatestOpenedDir(fi.path());

    for (int i = 0; i < fileNames.count(); i++) {
        QFileInfo fi(fileNames.at(i));
        ImageAttributes iA;

        int w_data = 0;
        int h_data = 0;
        int x_dpi_data = 0;
        int y_dpi_data = 0;

        /* Controlla i doppioni! */
        if (!checkDuplicates(fileNames, i)) {
            Image my_image;
            //my_image.quiet(true);

            try {
                my_image.ping(fileNames.at(i).toStdString());

                w_data = my_image.columns();
                h_data = my_image.rows();
                x_dpi_data = my_image.xResolution();
                y_dpi_data = my_image.yResolution();
            }
            catch (Error &error) {
                QString err_read_status = QString("Error in reading image metadata: %1").arg(QString::fromStdString(error.what()));
                qWarning() << "Read Error: " << err_read_status;
                if (Formats::isNativeReadable(fileNames.at(i).toUtf8())) {
                    QImageReader reader(fileNames.at(i));
                    QSize size = reader.size();
                    QImage qimg = reader.read();

                    w_data = size.width();
                    h_data = size.height();

                    int dpiX = qimg.dotsPerMeterX();
                    int dpiY = qimg.dotsPerMeterY();

                    x_dpi_data = dpiX * 0.0254;
                    y_dpi_data = dpiY * 0.0254;
                }
            }
            catch( Magick::WarningCoder &warning )
            {
                qWarning() << "Read Warning: " << QString("Warning : %1").arg(QString::fromStdString(warning.what()));;
            }
            catch( Magick::Warning &warning )
            {
                qWarning() << "Read Warning: " << QString("Warning : %1").arg(QString::fromStdString(warning.what()));;
            }

            iA.completeFileName = fileNames.at(i).toUtf8();
            iA.fileName = fi.fileName();
            iA.suffix = fi.suffix();
            iA.imgSize = QString("%1×%2 px").arg(QString::number(w_data), QString::number(h_data));
            if (x_dpi_data == 0 || y_dpi_data == 0) {
                iA.imgRes = tr("n/a");
            } else {
                iA.imgRes = QString("%1×%2 dpi")
                                .arg(QString::number(x_dpi_data),
                                     QString::number(y_dpi_data));
            }
            iA.size = fi.size();
            iA.path = fi.path();
            iAList->append(iA);   // aggiunge
        }
    }
    fillTreeView();
}

bool MainWindowImpl::checkDuplicates(QStringList fileNames, int e)
{
    int cnt = iAList->count();

    for (int i = 0; i < cnt; i++)
        if (iAList->at(i).completeFileName == fileNames.at(e).toUtf8())
            return true;

    return false;
}

void MainWindowImpl::fillTreeView()
{
    treeWidget->addItems(iAList);
}

void MainWindowImpl::elabora()
{
    if (!iAList->isEmpty()) {
        if (treeWidget->thereAreItemsChecked()) {
            if (!lineDirectory->text().isEmpty()) {
                QDir dir(lineDirectory->text());
                if((dir.exists()) || (checkSameDir->isChecked())) {
                    startConversion();
                }
                else {
                    int ret = QMessageBox::warning(0, tr("Warning"),
                                                   tr("The output directory does not exist! Would you like to create it?"),
                                                   QMessageBox::Ok | QMessageBox::Cancel);

                    if (ret == QMessageBox::Ok) {
                        if (!dir.mkpath(lineDirectory->text()))
                            QMessageBox::warning(0, tr("Warning"),
                                                 tr("The directory cannot be created!"));
                        else {
                            startConversion();
                        }
                    }
                }
            }
            else
                QMessageBox::warning(0, tr("Warning"),
                                     tr("Set an output directory!"));
        }
        else
            QMessageBox::warning(0, tr("Warning"),
                                 tr("No image checked!"));
    }
    else
        QMessageBox::warning(0, tr("Warning"),
                             tr("No images to convert!"));
}

void MainWindowImpl::startConversion()
{
    double width;
    double height;
    bool percent = false;
    bool maintainAspectRatio = false;
    bool noTransparency;


    IniSettings::setOutputDir(lineDirectory->text());

    abort_all = false;


    statusBar()->showMessage(tr("Processing..."));
    curr_index = 0;

    m_progressiveNren = spinProgressiveRen->value();    // Used when the progressive number renaming is checked

    convertThread->reset();

    // Colore
    noTransparency = this->checkNoTransp->isChecked();
    convertThread->setBackgroundColor(m_bgColor, noTransparency);

    // setResize(const double &width, const double &height, const bool &percent, const bool &maintainAspectRatio)

    /* Change image size */
    if (groupDimensions->isChecked()) {
        width = spin_geoWidth->value();
        height = spin_geoHeight->value();

        if (checkRelative->isChecked())
            maintainAspectRatio = true;

        if (comboResizeValues->currentText() == "px")
            percent = false;

        if (comboResizeValues->currentText() == "%")
            percent = true;

        //if (!(((percent) && ((int)width == 100)) && ((int)height == 100)))
        convertThread->setResize(width, height, percent, maintainAspectRatio);
    }

    // Pixel Shroom Phase 5: use the visible DPI controls for EVERY batch.
    // The native hidden spinboxes are reset to zero after the studio is built
    // during MainWindowImpl construction. A checked DPI box does not emit a
    // toggled signal again; sync it explicitly at the conversion boundary.
    if (auto *studioPrintDpi = findChild<QCheckBox*>("psPrintDpi")) {
        const bool printEnabled = studioPrintDpi->isChecked();
        groupResolution->setChecked(printEnabled);
        if (printEnabled) {
            auto *studioDpiValue = findChild<QSpinBox*>("psDpiValue");
            if (!studioDpiValue || studioDpiValue->value() < 72) {
                QMessageBox::warning(this, tr("Invalid print DPI"),
                                     tr("Choose a print resolution of at least 72 DPI."));
                return;
            }
            spin_resX->setValue(studioDpiValue->value());
            spin_resY->setValue(studioDpiValue->value());
        }
    }
    /* Change image density */
    if (groupResolution->isChecked()) {
        QString densStr = QString("%1x%2")
                              .arg(spin_resX->value())
                              .arg(spin_resY->value());

        convertThread->setDensity(densStr);
    }

    if (!radioRotNo->isChecked()) {
        double rotation = 0;

        if (radioRotPos90->isChecked())
            rotation = 90.0;
        if (radioRotNeg90->isChecked())
            rotation = -90.0;
        if (radioRot180->isChecked())
            rotation = 180.0;

        convertThread->setRotation(rotation);
    }

    if (!radioFlipNo->isChecked()) {
        FlipOrientation fo;

        if (radioFlipV->isChecked())
            fo = VERTICAL;
        if (radioFlipH->isChecked())
            fo = HORIZONTAL;

        convertThread->setFlip(fo);
    }

    convertThread->setResamplingFilter(m_resamplingFilter);
    convertThread->setEnhancements(m_psSmoothSigma, m_psSharpenSigma);

    convert();

    dlgCStatus->setup(treeWidget->countChecked());
    dlgCStatus->exec();
}

void MainWindowImpl::convert()
{
    if ((treeWidget->topLevelItem(curr_index))->checkState(0)) {
        IniSettings::setLatestWrittenFormatIndex(comboWFormats->currentIndex());
        statusBar()->showMessage(iAList->at(curr_index).fileName, 5000);

        QString out_format;

        QString inputFilename = iAList->at(curr_index).completeFileName;

        QFileInfo fi(inputFilename);

        QList<MagickDefine> magickDefines;

        if (comboWFormats->currentIndex() != 0) {
            out_format = comboWFormats->currentText().split(" - ").at(0);
        }
        else {
            QString suffix = fi.suffix();

            out_format = suffix;
        }

        out_format = out_format.toLower();

        QString outFileName = QString("%1/%2.%3").arg(destinationPath()).arg(fi.completeBaseName()).arg(out_format);

        int quality = -1;

        /*
            For further details:
            http://www.imagemagick.org/script/command-line-options.php#quality
        */

        // Compression level 1-100
        if ((out_format == "jpg") || (out_format == "jpeg") || (out_format == "mpeg") || (out_format == "mpg")) {
            quality = m_jpgQuality;
        }

        // Compression level 0-9. For compression level 0 (quality value less than 10), the Huffman-only strategy is used
        if ((out_format == "png") || (out_format == "mng")) {
            quality = m_pngQuality * 10;
        }

        if (out_format == "webp") {
            quality = m_webPQuality;

            // magick, key, value
            magickDefines << MagickDefine("webp", "lossless", (m_psOverrideQuality ? "false" : (m_isWebPLosslessCompression ? "true" : "false")));
            magickDefines << MagickDefine("webp", "method", QString::number(m_webPCompression));
            magickDefines << MagickDefine("webp", "preprocessing", (m_iskWebPDithering) ? "1" : "0");
        }

        if (out_format == "avif") {
            // ImageMagick maybe maps quality=100 to lossless (?) AVIF.
            // Recent libaom versions reject the default chroma delta-q
            // configuration in this mode.

            quality = 99;
            magickDefines << MagickDefine("avif", "speed", "6");
            magickDefines << MagickDefine("heic", "chroma", "420");
        }

        if (m_psOverrideQuality && (out_format == "jpg" || out_format == "jpeg" || out_format == "webp"))
            quality = m_psQuality;

        convertThread->setInputPicture(inputFilename);
        convertThread->setFormat(out_format);
        convertThread->setQuality(quality);
        convertThread->setMagickDefines(magickDefines);
        convertThread->setRemoveMetadata(m_removeMetadata);
        convertThread->setOutputDir(destinationPath());

        if (checkRename->isChecked()) {
            // Special renaming settings for the output file enabled
            QString renamedOutFileName;

            if (radioPrefixSuffix->isChecked())
                renamedOutFileName = renameFileNameOnPrefixSuffix(outFileName);
            else
                renamedOutFileName = renameFileNameOnProgressiveN(outFileName);

            convertThread->setOutputPictureName(renamedOutFileName);
        }
        else {
            // No special renaming settings for the output file. Set it with tho original name + new extension
            convertThread->setOutputPictureName(outFileName);
        }

        OverwriteMode manageOverwrite = ASK;

        if (radioOverwriteExisting->isChecked())
            manageOverwrite = OVERWRITE;
        if (radioSkipExisting->isChecked())
            manageOverwrite = SKIP;

        convertThread->setOverwrite(manageOverwrite);

        convertThread->start();
    }
    else {
        nextConversion(2);
    }
}

void MainWindowImpl::nextConversion(int conv_status)
{
    if (!abort_all) {
        if ((treeWidget->topLevelItem(curr_index))->checkState(0)) {
            dlgCStatus->step(conv_status, iAList->at(curr_index).fileName);
        }

        QString msg = "";
        if (conv_status == 1) {
            msg = tr("Converted");
            // Add the destination dirs to DialogConversionStatus so them can be opened at the end of the image processing
            dlgCStatus->addOutputDirectory(QDir::toNativeSeparators(destinationPath()));
        }
        else if (conv_status == 2)
            msg = tr("Skipped");
        else if (conv_status == -1)
            msg = tr("Error");

        (treeWidget->topLevelItem(curr_index))->setText(1, msg);

        curr_index++;
        if (curr_index < iAList->count()) {
            convert();
        }
        else {
            statusBar()->showMessage(tr("Processing finished!"), 5000);
        }
    }
}

QString MainWindowImpl::renameFileNameOnPrefixSuffix(QString oldFileName)
{
    QString t_renamingString = lineRename->text();

    QFileInfo fi(oldFileName);
    QString newFileName = QString("%1.%2")
            .arg(t_renamingString.replace("#", fi.completeBaseName()))
            .arg(fi.suffix());

    return QString("%1/%2").arg(fi.path()).arg(newFileName);
}

QString MainWindowImpl::renameFileNameOnProgressiveN(QString oldFileName)
{
    QString t_renamingString = lineRename->text();

    QFileInfo fi(oldFileName);  // For the output directory
    QString newFileName = QString("%1.%2")
            .arg(t_renamingString.replace("#", QString::number(m_progressiveNren)))
            .arg(fi.suffix());

    m_progressiveNren++;    // the key of progressive number renaming (set to start when the conversion in starded)

    return QString("%1/%2").arg(fi.path()).arg(newFileName);
}

void MainWindowImpl::loadFormats()
{
    Formats::loadFormats();

    comboWFormats->addItems(Formats::writableFilters());
    comboWFormats->setCurrentIndex(0);
}

void MainWindowImpl::setCurrentDirectory()
{
    bool enabled;

    if (checkSameDir->isChecked())
        enabled = false;
    else
        enabled = true;

    lineDirectory->setEnabled(enabled);
    bntSelDir->setEnabled(enabled);
}

void MainWindowImpl::openOutDirectory()
{
    QString dir = QFileDialog::getExistingDirectory(this, tr("Open Directory"),
                                                    QDir::homePath(),
                                                    QFileDialog::ShowDirsOnly
                                                    | QFileDialog::DontResolveSymlinks);

    if (!dir.isNull())
        lineDirectory->setText(QDir::toNativeSeparators(dir));
    // La cartella viene salvata quando viene avviata la procedura di conversione

}

void MainWindowImpl::loadOptions()
{
    //IniSettings::init();

    this->restoreGeometry(IniSettings::windowGeometry());

    lineDirectory->setText(QDir::toNativeSeparators(IniSettings::outputDir()));
    comboWFormats->setCurrentIndex(IniSettings::latestWrittenFormatIndex());

    int overwriteMode = IniSettings::overwriteMode();

    switch (overwriteMode) {
    case 0:
        radioOverwriteAsk->setChecked(true);
        break;
    case 1:
        radioSkipExisting->setChecked(true);
        break;
    case 2:
        radioOverwriteExisting->setChecked(true);
        break;
    default:
        radioOverwriteAsk->setChecked(true);
        break;
    }

    loadQuality();

    m_bgColor = IniSettings::backgroundColor();

    QColor c;
    c.setNamedColor(m_bgColor);
    pushColor->setColor(c);

    checkShowPreview->setChecked(IniSettings::previewChecked());
    groupDimensions->setChecked(IniSettings::scaleChecked());
    comboResizeValues->setCurrentIndex(IniSettings::measure());
    checkRelative->setChecked(IniSettings::aspectRatioChecked());
    groupResolution->setChecked(IniSettings::resolutionChecked());
    checkSameDir->setChecked(IniSettings::imageDirChecked());
    checkRename->setChecked(IniSettings::renameChecked());
    checkNoTransp->setChecked(IniSettings::bgColorChecked());

    enableRenameLine();
    enableProgressiveSpin();
}

void MainWindowImpl::setQuality()
{
    loadQuality();

    DialogQuality *dlg = new DialogQuality(this);
    dlg->setInitValues(m_jpgQuality, m_pngQuality, m_resamplingFilter);

    dlg->setIsWebPLosslessCompression(m_isWebPLosslessCompression);
    dlg->setWebPCompression(m_webPCompression);
    dlg->setWebPQuality(m_webPQuality);
    dlg->setIskWebPDithering(m_iskWebPDithering);

    dlg->setIsRemoveMetadata(m_removeMetadata);

    if (dlg->exec()) {
        m_jpgQuality = dlg->getJpegQuality();
        m_pngQuality = dlg->getPngQuality();

        m_isWebPLosslessCompression = dlg->isWebPLosslessCompression();
        m_webPCompression = dlg->getWebPCompression();
        m_webPQuality = dlg->getWebPQuality();
        m_iskWebPDithering = dlg->iskWebPDithering();

        m_resamplingFilter = dlg->getResamplingFilter();

        m_removeMetadata = dlg->isRemoveMetadata();

        IniSettings::setJpgQuality(m_jpgQuality);
        IniSettings::setPngQuality(m_pngQuality);
        IniSettings::setLatestInterpFiltIdx((int)m_resamplingFilter);

        IniSettings::setIsWebPLosslessCompression(m_isWebPLosslessCompression);
        IniSettings::setWebPCompression(m_webPCompression);
        IniSettings::setWebPQuality(m_webPQuality);
        IniSettings::setIskWebPDithering(m_iskWebPDithering);

        IniSettings::setIsRemoveMetadata(m_removeMetadata);
    }

    delete dlg;
}

void MainWindowImpl::loadQuality()
{
    m_jpgQuality = IniSettings::jpgQuality();
    m_pngQuality = IniSettings::pngQuality();
    m_resamplingFilter = (IMFilterType)IniSettings::latestInterpFiltIdx();

    m_isWebPLosslessCompression = IniSettings::isWebPLosslessCompression();
    m_webPCompression = IniSettings::webPCompression();
    m_webPQuality = IniSettings::webPQuality();
    m_iskWebPDithering = IniSettings::iskWebPDithering();

    m_removeMetadata = IniSettings::isRemoveMetadata();
}

void MainWindowImpl::removeItems()
{
    if (!iAList->isEmpty()) {
        treeWidget->removeItems(iAList);

        labelPreview->setText(tr("Preview"));

        labelType->setText(" - ");
        label_ImageSize->setText(" - ");
        labelFileSize->setText(" - ");
        label_ImageResolution->setText(" - ");

        labelPixelGeometry->setText("");
    }
}

void MainWindowImpl::removeAllItems()
{
    if (!iAList->isEmpty()) {
        iAList->clear();
        CachingSystem::clear();
        treeWidget->clear();

        labelPreview->setText(tr("Preview"));

        labelType->setText(" - ");
        label_ImageSize->setText(" - ");
        labelFileSize->setText(" - ");
        label_ImageResolution->setText(" - ");

        labelPixelGeometry->setText("");

        //resetDisplays();
    }
}

void MainWindowImpl::relativeSizeW()
{
    double value = spin_geoWidth->value();

    if (pushLinkAspect->isChecked()) {
        if (checkRelative->isChecked()) {
            if (comboResizeValues->currentText() == "px") {
                double relative_H = ( ((double)img_height * value) / (double)img_width);
                spin_geoHeight->setValue((double)qRound(relative_H));
            }
        }
    }

    if (comboResizeValues->currentText() == "%") {
        if (checkRelative->isChecked())
            spin_geoHeight->setValue(spin_geoWidth->value());
    }

    showNewSizePreview();
}

void MainWindowImpl::relativeSizeH()
{
    double value = spin_geoHeight->value();

    if (pushLinkAspect->isChecked()) {
        if (checkRelative->isChecked()) {
            if (comboResizeValues->currentText() == "px") {
                double relative_V = ( ((double)img_width * value) / (double)img_height);
                spin_geoWidth->setValue((double)qRound(relative_V));
            }
        }
    }

    if (comboResizeValues->currentText() == "%") {
        if (checkRelative->isChecked())
            spin_geoWidth->setValue(spin_geoHeight->value());
    }

    showNewSizePreview();
}

void MainWindowImpl::loadPreview(QString fileName)
{
    labelPreview->loadPreview(fileName, checkShowPreview->isChecked());
}

void MainWindowImpl::showImageInformations(int orig_w, int orig_h, double orig_dens_x, double orig_dens_y)
{
    /*
        Method executed by the signal myLabelPreviewer::previewReady(orig_w, orig_h, orig_dens_x, orig_dens_y);
    */

    img_width = orig_w;
    img_height = orig_h;

    m_xResolution = orig_dens_x;
    m_yResolution = orig_dens_y;

    int index = treeWidget->currentIndex().row();

    if (index < 0) {
        resetDisplays();

        return;
    }

    labelType->setText(QString("<span style=\" font-size:8pt;\">%1</span>")
                           .arg(iAList->at(index).suffix));

        QString sSize = SizeUtil::simplifyFileSize(iAList->at(index).size);
        labelFileSize->setText(QString("<span style=\" font-size:8pt;\">%1</span>")
                               .arg(sSize));

        label_ImageSize->setText(QString("<span style=\" font-size:8pt;\">%1 x %2 px</span>")
                                 .arg(img_width)
                                 .arg(img_height));

        label_ImageResolution->setText(QString("<span style=\" font-size:8pt;\">X = %1 Y = %2</span>")
                                       .arg(m_xResolution)
                                       .arg(m_yResolution));
}

void MainWindowImpl::onItemSelection()
{
    int index = treeWidget->currentIndex().row();

    if ((index > -1) && (!iAList->isEmpty())) {
        showPreviewAndInfos();
        showNewSizePreview();
    }
}

void MainWindowImpl::onPushResetClick()
{
    selectGeometryUnit(comboResizeValues->currentText());
    showNewSizePreview();
}

void MainWindowImpl::showPreviewAndInfos()
{
    int index = treeWidget->currentIndex().row();

    loadPreview(iAList->at(index).completeFileName);
}

void MainWindowImpl::editSettings()
{
    DialogOptions dlg(this);
    dlg.exec();

    if (dlg.result() == 1) {
        radioOverwriteExisting->setChecked(IniSettings::overwriteMode());
    }
}

void MainWindowImpl::about()
{
    DialogInfo dlg(this);
    dlg.exec();
}

void MainWindowImpl::enableRenameLine()
{
    if (checkRename->isChecked()) {
        lineRename->setEnabled(true);
        radioPrefixSuffix->setEnabled(true);
        radioProgressive->setEnabled(true);
        spinProgressiveRen->setEnabled(true);
        labeStartWith->setEnabled(true);
    }
    else
    {
        lineRename->setEnabled(false);
        radioPrefixSuffix->setEnabled(false);
        radioProgressive->setEnabled(false);
        spinProgressiveRen->setEnabled(false);
        labeStartWith->setEnabled(false);
    }

    enableProgressiveSpin();
}

void MainWindowImpl::enableProgressiveSpin()
{
    if (radioProgressive->isChecked()) {
        spinProgressiveRen->setEnabled(true);
        labeStartWith->setEnabled(true);
    }
    else {
        spinProgressiveRen->setEnabled(false);
        labeStartWith->setEnabled(false);
    }
}

void MainWindowImpl::enableShowPreview()
{
    if (treeWidget->selectedItems().count() > 0)
        onItemSelection();
    else
        labelPreview->setText(tr("Preview"));
}

void MainWindowImpl::selectGeometryUnit(QString unit)
{
    if (unit == "px") {
        spin_geoWidth->setDecimals(0);
        spin_geoWidth->setSuffix(" px");
        spin_geoWidth->setValue((double)img_width);

        spin_geoHeight->setDecimals(0);
        spin_geoHeight->setSuffix(" px");
        spin_geoHeight->setValue((double)img_height);
    }
    if (unit == "%") {
        spin_geoWidth->setDecimals(2);
        spin_geoWidth->setSuffix(" %");
        spin_geoWidth->setValue(100.00);

        spin_geoHeight->setDecimals(2);
        spin_geoHeight->setSuffix(" %");
        spin_geoHeight->setValue(100.00);
    }
}

void MainWindowImpl::showNewSizePreview()
{
    if (comboResizeValues->currentText() == "%") {
        double new_width, new_height, round_new_width, round_new_height;

        new_width = (((double)img_width / 100) * (spin_geoWidth->value()));
        new_height = (((double)img_height / 100) * (spin_geoHeight->value()));

        round_new_width = qRound(new_width);
        round_new_height = qRound(new_height);

        if (treeWidget->selectedItems().count() > 0)
            labelPixelGeometry->setText(QString("<span style=\" font-size:8pt;\"><center>%1 x %2 pixels</center></span>")
                                        .arg(round_new_width)
                                        .arg(round_new_height));

        new_img_width = round_new_width;
        new_img_height = round_new_height;
    }
    if (comboResizeValues->currentText() == "px") {
        if (treeWidget->selectedItems().count() > 0)
            labelPixelGeometry->setText(QString("<span style=\" font-size:8pt;\"><center>%1 x %2 pixels</center></span>")
                                        .arg(spin_geoWidth->value())
                                        .arg(spin_geoHeight->value()));

        new_img_width = spin_geoWidth->value();
        new_img_height = spin_geoHeight->value();
    }
}

void MainWindowImpl::resetDisplays()
{
    labelPreview->setText(tr("Preview"));

    img_width = 0;
    img_height = 0;

    new_img_width = 0;
    new_img_height = 0;

    m_xResolution = 0;
    m_yResolution = 0;

    /*spin_resX->setValue(0);
    spin_resY->setValue(0);

    if (comboResizeValues->currentText() == "%") {
        spin_geoWidth->setValue(100);
        spin_geoHeight->setValue(100);
    }
    if (comboResizeValues->currentText() == "px") {
        spin_geoWidth->setValue(1);
        spin_geoHeight->setValue(1);
    }*/

    labelType->setText(" - ");
    label_ImageSize->setText(" - ");
    labelFileSize->setText(" - ");
    label_ImageResolution->setText(" - ");

    labelPixelGeometry->setText("");
}

void MainWindowImpl::checkVersion()
{
    int savedVersion = IniSettings::currentVersion();
    int currentVersion = globals::CURRENT_INTERNAL_VERSION;

    if (savedVersion < currentVersion) {
#if (defined(Q_OS_WIN) || defined(Q_OS_MACOS))
        // Open thank you page
        QString welcomePage = QString("https://converseen.fasterland.net/thank/");
		QDesktopServices::openUrl(QUrl(welcomePage, QUrl::TolerantMode));
#endif
		IniSettings::setCurrentVersion(currentVersion);
    }
}

void MainWindowImpl::saveSettings()
{
    IniSettings::setWindowGeometry(saveGeometry());
    IniSettings::setPreviewChecked(checkShowPreview->isChecked());
    IniSettings::setScaleChecked(groupDimensions->isChecked());
    IniSettings::setMeasure(comboResizeValues->currentIndex());
    IniSettings::setAspectRatioChecked(checkRelative->isChecked());
    IniSettings::setResolutionChecked(groupResolution->isChecked());
    IniSettings::setImageDirChecked(checkSameDir->isChecked());
    IniSettings::setRenameChecked(checkRename->isChecked());
    IniSettings::setBgColorChecked(checkNoTransp->isChecked());
    //IniSettings::setOverwriteMode(radioOverwriteExisting->isChecked());
    setOverwriteStatus();

    IniSettings::settings->sync();
}

void MainWindowImpl::loadTheme()
{
    QString theme = IniSettings::theme();

    if (theme != "none") {
        QApplication::setStyle(QStyleFactory::create(theme));
    }
}

void MainWindowImpl::overwriteDialog(QString baseName)
{
    bool ok;
    QString newBaseName;

    while (newBaseName.isEmpty()) {
        newBaseName = QInputDialog::getText(0, tr("Suggest a new name!"),
                                            tr("New name:"), QLineEdit::Normal,
                                            baseName, &ok);

        if (!ok) {
            QMessageBox::StandardButton msg;
            msg = QMessageBox::question(this, tr("Please, specify a name!"),
                                        tr("You should specify a name.\nClick Retry to specify a new name.\nClick Ignore to cancel this operation.\nClick Abort to cancel all operations."),
                                        QMessageBox::Retry | QMessageBox::Ignore | QMessageBox::Abort);



            if (msg == QMessageBox::Ignore) {
                convertThread->stopProcess();
                break;
            }

            if (msg == QMessageBox::Abort) {
                stopProcess();
                break;
            }
        }
        else {
            if (newBaseName.isEmpty())
                QMessageBox::warning(0, tr("Warning!"),
                                     tr("The filename should not be empty!"));

            if (newBaseName == baseName) {
                QMessageBox::StandardButton msg;
                msg = QMessageBox::question(this, tr("Warning!"),
                                            tr("The name chosen is identical to the initial one. Do you want to overwrite the original file?"),
                                            QMessageBox::Yes | QMessageBox::No); // TODO: mettere si per tutte!

                if (msg == QMessageBox::No)
                    newBaseName.clear();
            }
        }
    }
    //convertThread->mutex.unlock();
    convertThread->setNewBasename(newBaseName, ok);
}

void MainWindowImpl::stopProcess()
{
    convertThread->stopProcess();
    abort_all = true;
    statusBar()->showMessage(tr("Aborted!"), 5000);
}

void MainWindowImpl::errorMessage(QString err_status)   // Manda stringa di errore al dialog di conversione
{
    dlgCStatus->setErrorMsg(err_status);
}

void MainWindowImpl::choseBackgroundColor()
{
    QColor color;
    color = QColorDialog::getColor(Qt::green, this);

    m_bgColor = color.name();

    pushColor->setColor(color);

    IniSettings::setBackgroundColor(m_bgColor);
}

QString MainWindowImpl::destinationPath()
{
    QString dest = lineDirectory->text();

    if (checkSameDir->isChecked())
        dest = iAList->at(curr_index).path;

    return dest;
}

void MainWindowImpl::openPaypalLink()
{
    QDesktopServices::openUrl(QUrl("https://converseen.fasterland.net/donate/", QUrl::TolerantMode));
}

#ifndef DISABLE_CHECK_UPDATES
void MainWindowImpl::checkForUpdates()
{
    // Checks for updates at program startup
    updateChecker->checkForUpdates();
}

void MainWindowImpl::manualCheckForUpdate()
{
    // Checks for updates when manually requested
    bool update_available = updateChecker->isUpdateAvailable();

    if (update_available) {
        showUpdateDialog();
    } else {
        QString title = QString(tr("No updates available!"));
        QString text = QString(tr("%1 is already updated to the most recent version."))
                              .arg(globals::PROGRAM_NAME);

        QMessageBox::information(this, title, text, QMessageBox::Ok, QMessageBox::Ok);
    }
}

void MainWindowImpl::updateAvailable(const bool &isAvailable)
{
    // Signal received when updates are checked
    if (isAvailable && IniSettings::isAutoChechUpdates()) {
        showUpdateDialog();
    }
}

void MainWindowImpl::showUpdateDialog()
{
    QString caption = QString(tr("New version is available!"));
    QString message = QString(tr("A new version of %1 is available!\nWould you download it?"))
                          .arg(globals::PROGRAM_NAME);

    DialogShowUpdateMsg dlg(this, caption, message, IniSettings::isAutoChechUpdates());

    if (dlg.exec()) {
        QDesktopServices::openUrl(QUrl(DESTINATION_URL, QUrl::TolerantMode));
    }
}
#endif

void MainWindowImpl::bugReport()
{
    QDesktopServices::openUrl(QUrl("https://github.com/Faster3ck/Converseen/issues", QUrl::TolerantMode));
}

void MainWindowImpl::onlineHelp()
{
    QDesktopServices::openUrl(QUrl("https://converseen.fasterland.net/help/", QUrl::TolerantMode));
}

void MainWindowImpl::setRelativeSizeCheckboxes(int state)
{
    if (state == 0)
        pushLinkAspect->setEnabled(false);
    else
        pushLinkAspect->setEnabled(true);
}

void MainWindowImpl::setOverwriteStatus()
{
    OverwriteMode manageOverwrite = ASK;

    if (radioOverwriteAsk->isChecked())
        manageOverwrite = ASK;
    else if (radioOverwriteExisting->isChecked())
        manageOverwrite = OVERWRITE;
    else if (radioSkipExisting->isChecked())
        manageOverwrite = SKIP;

    IniSettings::setOverwriteMode(manageOverwrite);
    IniSettings::settings->sync();
}
