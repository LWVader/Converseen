#pragma once
/*
 Pixel Shroom Image Studio - Phase 18 unified accent and dedicated settings.
 Styling is applied only to interface chrome, never to image data or exports.
 These painted surfaces are intentionally stable/opaque to avoid the ghosting
 seen when Qt child widgets overlap DWM translucent backgrounds.
*/
#include <QColor>
#include <QString>
#include "pixelshroom_phase15_theme.h"

namespace PixelShroomPhase18Theme {

inline QColor mix(const QColor &base, const QColor &tint, int percent) {
    const int p = qBound(0, percent, 100);
    return QColor((base.red()*(100-p)+tint.red()*p)/100,
                  (base.green()*(100-p)+tint.green()*p)/100,
                  (base.blue()*(100-p)+tint.blue()*p)/100);
}

struct Palette {
    QColor accent;
    QString text, muted, surface, raised, panel, panelHi, input, canvas;
    QString border, hover, selected, track, handle, handleHover;
    QString outline, labelBg;
};

inline Palette palette(bool dark) {
    Palette p;
    p.accent = PixelShroomPhase15Theme::accent();
    const QColor a = p.accent;
    auto hex = [](const QColor &c) { return c.name(); };
    if (dark) {
        p.text = "#eef6ff";
        p.muted = "#b7ccdf";
        p.surface = hex(mix(QColor("#1c293d"), a, 15));
        p.raised  = hex(mix(QColor("#34475f"), a, 24));
        p.panel   = hex(mix(QColor("#26384e"), a, 18));
        p.panelHi = hex(mix(QColor("#47617a"), a, 29));
        p.input   = hex(mix(QColor("#1e3249"), a, 12));
        p.canvas  = PixelShroomPhase15Theme::canvas(true).name();
        p.border  = hex(mix(QColor("#6c829a"), a, 45));
        p.hover   = hex(mix(QColor("#53677e"), a, 57));
        p.selected= "#102439";
        p.track   = hex(mix(QColor("#15263a"), a, 12));
        p.handle  = hex(mix(QColor("#7e94a9"), a, 54));
        p.handleHover = a.lighter(130).name();
        p.outline = a.name();
        p.labelBg = p.panel;
    } else {
        p.text = "#243d5b";
        p.muted = "#496a87";
        p.surface = hex(mix(QColor("#e4edf6"), a, 15));
        p.raised  = hex(mix(QColor("#f4f8fc"), a, 19));
        p.panel   = hex(mix(QColor("#edf3f9"), a, 20));
        p.panelHi = hex(mix(QColor("#ffffff"), a, 10));
        p.input   = "#ffffff";
        p.canvas  = PixelShroomPhase15Theme::canvas(false).name();
        p.border  = hex(mix(QColor("#aec2d7"), a, 46));
        p.hover   = hex(mix(QColor("#eaf3fc"), a, 35));
        p.selected= "#152a43";
        p.track   = hex(mix(QColor("#dce8f4"), a, 18));
        p.handle  = hex(mix(QColor("#a6bad0"), a, 55));
        p.handleHover = a.darker(112).name();
        p.outline = a.darker(112).name();
        p.labelBg = p.panel;
    }
    return p;
}

inline QString render(QString css, const Palette &p) {
    const struct Pair { const char* token; QString value; } tokens[] = {
        {"@ACCENT@",p.accent.name()}, {"@TEXT@",p.text}, {"@MUTED@",p.muted},
        {"@SURFACE@",p.surface}, {"@RAISED@",p.raised}, {"@PANEL@",p.panel},
        {"@PANELHI@",p.panelHi}, {"@INPUT@",p.input}, {"@CANVAS@",p.canvas},
        {"@BORDER@",p.border}, {"@HOVER@",p.hover}, {"@SELECTED@",p.selected},
        {"@TRACK@",p.track}, {"@HANDLE@",p.handle}, {"@HANDLEHOVER@",p.handleHover},
        {"@OUTLINE@",p.outline}, {"@LABELBG@",p.labelBg}
    };
    for (const auto &t : tokens) css.replace(QLatin1String(t.token), t.value);
    return css;
}

inline QString app(bool dark) {
    return render(QString::fromUtf8(R"QSS(
/* Uniform accented chrome. Source imagery is not altered. */
QWidget#centralwidget { background:@SURFACE@; }
QMenuBar, QMenu { background:@SURFACE@; color:@TEXT@; border-color:@BORDER@; }
QMenuBar::item:selected, QMenu::item:selected { background:@HOVER@; color:@TEXT@; }
QToolBar { background:@PANEL@; border:0; border-bottom:1px solid @BORDER@; spacing:9px; }
QToolBar QToolButton, QToolBar QPushButton {
 background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 @PANELHI@,stop:1 @RAISED@);
 color:@TEXT@; border:1px solid @BORDER@; border-radius:12px; padding:8px 11px;
}
QToolBar QToolButton:hover, QToolBar QPushButton:hover { background:@HOVER@; border-color:@ACCENT@; }
QToolBar QToolButton:pressed { background:@SURFACE@; }
QDockWidget, QWidget#dockWidgetContents, QFrame#frame, QFrame#frame_2 {
 background:@PANEL@; color:@TEXT@; border-color:@BORDER@;
}
QDockWidget::title { background:@RAISED@; border-bottom:1px solid @BORDER@; color:@TEXT@; }
QFrame#psQueueCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 @PANELHI@,stop:1 @PANEL@);
 border:1px solid @BORDER@; border-top:2px solid @OUTLINE@; border-radius:18px; }
QLabel#psQueueHeader { background:transparent; border:0; color:@TEXT@; }
QGroupBox { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 @PANELHI@,stop:1 @PANEL@);
 border:1px solid @BORDER@; border-radius:15px; margin-top:17px; padding:12px 9px 9px; color:@TEXT@; }
QGroupBox::title { subcontrol-origin:margin; subcontrol-position:top left; left:12px;
 color:@TEXT@; background:@LABELBG@; padding:2px 6px; }
QTreeWidget#treeWidget, QTreeView, QTableView, QListView {
 background:@INPUT@; color:@TEXT@; alternate-background-color:@RAISED@;
 border:1px solid @BORDER@; border-radius:12px; selection-background-color:@HOVER@;
 selection-color:@TEXT@;
}
QHeaderView::section { background:@RAISED@; color:@TEXT@; border:0; border-bottom:1px solid @BORDER@; padding:7px; }
QTreeWidget::item:selected, QTableView::item:selected { background:@HOVER@; color:@TEXT@; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
 background:@INPUT@; color:@TEXT@; border:1px solid @BORDER@; border-radius:10px;
 selection-background-color:@HOVER@;
}
QComboBox QAbstractItemView { background:@INPUT@; color:@TEXT@; selection-background-color:@HOVER@; }
QPushButton, QToolButton {
 background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 @PANELHI@,stop:1 @RAISED@);
 color:@TEXT@; border:1px solid @BORDER@; border-radius:11px;
}
QPushButton:hover, QToolButton:hover { border-color:@ACCENT@; background:@HOVER@; }
QPushButton:pressed, QToolButton:pressed { background:@SURFACE@; }
QPushButton:focus, QToolButton:focus, QLineEdit:focus, QComboBox:focus {
 border:2px solid @OUTLINE@;
}
QCheckBox, QRadioButton, QLabel { color:@TEXT@; }
QCheckBox::indicator, QRadioButton::indicator { border:1px solid @BORDER@; }
QCheckBox::indicator:checked { background:@ACCENT@; border:1px solid @OUTLINE@; }
QTabWidget#psStudioTabs::pane { background:@PANEL@; border:1px solid @BORDER@; }
QTabBar#psStudioTabBar { background:@PANEL@; border:0; }
QTabBar#psStudioTabBar::tab { background:@RAISED@; color:@TEXT@; border:1px solid @BORDER@;
 border-radius:10px; padding:9px 12px; margin-right:5px; }
QTabBar#psStudioTabBar::tab:selected { background:@ACCENT@; color:@SELECTED@; border-color:@OUTLINE@; }
QTabBar#psStudioTabBar::tab:hover { background:@HOVER@; }
QWidget#labelPreview, QLabel#psGlassImageCanvas, QGraphicsView#psGlassImageCanvas {
 background:@CANVAS@; border:1px solid @BORDER@; border-radius:13px;
}
QDialog#psAppearanceDialog { background:@SURFACE@; color:@TEXT@; }
QDialog#psAppearanceDialog QLabel#psAppearanceDialogTitle { font-size:18pt; font-weight:700; color:@TEXT@; }
QDialog#psAppearanceDialog QLabel#psAppearanceDialogHint { color:@MUTED@; }
QDialog#psAppearanceDialog QFrame#psThemePreviewCard {
 background:@PANEL@; border:1px solid @BORDER@; border-radius:18px; }
QDialog#psAppearanceDialog QFrame#psThemePreviewHeader {
 background:@RAISED@; border:1px solid @BORDER@; border-radius:12px; }
QDialog#psAppearanceDialog QFrame#psThemePreviewCanvas {
 background:@CANVAS@; border:1px solid @BORDER@; border-radius:12px; }
QDialog#psAppearanceDialog QLabel#psThemePreviewPrimary {
 background:@ACCENT@; color:@SELECTED@; border:1px solid @OUTLINE@;
 border-radius:10px; padding:10px 16px; font-weight:700; }
QDialog#psAppearanceDialog QLabel#psThemePreviewSecondary {
 background:@RAISED@; color:@TEXT@; border:1px solid @BORDER@;
 border-radius:10px; padding:10px 16px; }
QDialog#psAppearanceDialog QLabel#psThemePreviewCaption { color:@MUTED@; }
QProgressBar { color:@TEXT@; background:@TRACK@; border:1px solid @BORDER@; border-radius:7px; }
QProgressBar::chunk { background:@ACCENT@; border-radius:6px; }
/* Entire application's scrollbars, including file list and editor previews. */
QScrollBar:vertical { background:@TRACK@; width:13px; margin:2px 1px; border:0; border-radius:6px; }
QScrollBar::handle:vertical { background:@HANDLE@; min-height:32px; border:1px solid @BORDER@; border-radius:5px; }
QScrollBar::handle:vertical:hover { background:@HANDLEHOVER@; border-color:@ACCENT@; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0px; border:none; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background:transparent; }
QScrollBar:horizontal { background:@TRACK@; height:13px; margin:1px 2px; border:0; border-radius:6px; }
QScrollBar::handle:horizontal { background:@HANDLE@; min-width:32px; border:1px solid @BORDER@; border-radius:5px; }
QScrollBar::handle:horizontal:hover { background:@HANDLEHOVER@; border-color:@ACCENT@; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width:0px; border:none; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background:transparent; }
QScrollBar::corner { background:@TRACK@; }
)QSS"), palette(dark));
}

inline QString panel(bool dark) {
    return render(QString::fromUtf8(R"QSS(
QFrame#psStudioPanel { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 @PANELHI@,stop:1 @PANEL@);
 border:1px solid @BORDER@; border-top:2px solid @ACCENT@; border-radius:19px; }
QFrame#psStudioPanel QTabWidget#psStudioTabs::pane { background:@PANEL@; border:1px solid @BORDER@; }
QFrame#psStudioPanel QTabBar#psStudioTabBar { background:@PANEL@; }
QFrame#psStudioPanel QTabBar#psStudioTabBar::tab { background:@RAISED@; color:@TEXT@;
 border:1px solid @BORDER@; border-radius:10px; margin-right:5px; padding:9px 12px; }
QFrame#psStudioPanel QTabBar#psStudioTabBar::tab:selected { background:@ACCENT@;
 color:@SELECTED@; border-color:@OUTLINE@; }
QFrame#psStudioPanel QTabBar#psStudioTabBar::tab:hover { background:@HOVER@; }
QFrame#psStudioPanel QWidget#psResizeTab, QFrame#psStudioPanel QWidget#psCompressTab,
QFrame#psStudioPanel QWidget#psEnhanceTab, QFrame#psStudioPanel QWidget#psUploadTab {
 background:@PANEL@;
}
QFrame#psStudioPanel QScrollArea#psEditorScroll_psResizeTab,
QFrame#psStudioPanel QScrollArea#psEditorScroll_psCompressTab,
QFrame#psStudioPanel QScrollArea#psEditorScroll_psEnhanceTab,
QFrame#psStudioPanel QScrollArea#psEditorScroll_psUploadTab { background:@PANEL@; border:0; }
)QSS"), palette(dark));
}
} // namespace PixelShroomPhase18Theme
