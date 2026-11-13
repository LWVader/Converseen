#pragma once
/*
 * Pixel Shroom Image Studio — Phase 17 stable glass rendering.
 * A DWM backdrop can remain behind the native titlebar, but Qt child widgets
 * paint stable backgrounds so old controls do not bleed through on resize.
 * Visual styles only; does not change artwork or conversion data.
 */
#include <QString>
#include "pixelshroom_phase15_theme.h"

namespace PixelShroomPhase17Theme {
inline QString app(bool dark) {
    // Opaque backing surface inside the content area is intentional. The
    // layered gradients and subtle highlights emulate glass without allowing
    // previous widget frames or child text to show through.
    QString sheet;
    if (dark) sheet = QString::fromUtf8(R"DARK(
QWidget#centralwidget { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #152238,stop:0.46 #24354b,stop:1 #182a40); }
QToolBar { background:#23354b; border:0; border-bottom:1px solid #6b83a0; padding:8px 11px; spacing:10px; }
QToolBar QToolButton, QToolBar QPushButton {
 background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #55708e,stop:0.5 #3c5572,stop:1 #30475f);
 color:#f3f8ff; border:1px solid #7f9ab7; border-top:1px solid #a5bdd5;
 border-radius:13px; padding:8px 12px; min-height:27px; }
QToolBar QToolButton:hover { background:#54779a; border-color:#bad5f1; }
QToolBar QToolButton:pressed { background:#264462; }
QFrame#psQueueCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #435b74,stop:0.34 #283f59,stop:1 #1e314a);
 border:1px solid #819db9; border-top:2px solid #a2c1df; border-radius:18px; }
QLabel#psQueueHeader { color:#d7e9fa; font-size:10pt; font-weight:700; padding:0 3px; background:transparent; border:0; }
QTreeWidget#treeWidget { background:#1d2d44; color:#e9f4ff; border:1px solid #647f9d; border-radius:12px; }
QTreeWidget::item { background:#1d2d44; }
QTreeWidget::item:selected { background:#527da8; color:#ffffff; }
QHeaderView::section { background:#314862; border-bottom:1px solid #7594b3; color:#e7f5ff; padding:7px 8px; }
QGroupBox { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #405872,stop:1 #293f58);
 border:1px solid #7e98b3; border-radius:16px; margin-top:17px; padding:14px 9px 9px; }
QGroupBox::title { subcontrol-origin:margin; subcontrol-position:top left; left:14px; padding:2px 5px; background:#2a415a; color:#e0eefb; }
QSplitter#psWorkspaceSplitter::handle:vertical { background:#192b41; border-top:2px solid #7595b5; border-bottom:2px solid #8ab5d4; height:14px; }
QWidget#psResizeTab, QWidget#psCompressTab, QWidget#psEnhanceTab, QWidget#psUploadTab { background:#273d56; }
QScrollArea#psEditorScroll_psResizeTab, QScrollArea#psEditorScroll_psCompressTab,
QScrollArea#psEditorScroll_psEnhanceTab, QScrollArea#psEditorScroll_psUploadTab { background:#273d56; border:0; }
QFrame#psStudioPanel QTabWidget#psStudioTabs::pane { background:#263c55; border:1px solid #91acc7; border-radius:13px; padding:8px; }
QTabBar#psStudioTabBar { background:#293e56; border:0; }
QTabBar#psStudioTabBar::tab { background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #617a99,stop:1 #485e79);
 color:#eaf3ff; border:1px solid #7993b1; border-radius:11px; margin:0 3px 5px 0; padding:9px 12px; }
QTabBar#psStudioTabBar::tab:selected { background:@ACCENT@; color:#132a44; border-color:@ACCENT@; }
QTabBar#psStudioTabBar::tab:hover { background:#5d81a5; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background:#243951; border:1px solid #748fab; color:#f0f7ff; }
)DARK");
    else sheet = QString::fromUtf8(R"LIGHT(
QWidget#centralwidget { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #e7eff9,stop:0.45 #d7e4f4,stop:1 #dce9f6); }
QToolBar { background:#e3edf8; border:0; border-bottom:1px solid #a9bfd6; padding:8px 11px; spacing:10px; }
QToolBar QToolButton, QToolBar QPushButton { background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ffffff,stop:0.5 #f2f8ff,stop:1 #d6e6f6);
 color:#2b4e72; border:1px solid #b2c9e0; border-top:1px solid #ffffff;
 border-radius:13px; padding:8px 12px; min-height:27px; }
QToolBar QToolButton:hover { background:#dceeff; border-color:#82b4df; }
QToolBar QToolButton:pressed { background:#c7e0f8; }
QFrame#psQueueCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ffffff,stop:0.4 #edf5fd,stop:1 #d8e7f5);
 border:1px solid #aec6de; border-top:2px solid #ffffff; border-radius:18px; }
QLabel#psQueueHeader { color:#3a6284; font-size:10pt; font-weight:700; padding:0 3px; background:transparent; border:0; }
QTreeWidget#treeWidget { background:#ffffff; color:#2c4968; border:1px solid #b7cfe4; border-radius:12px; }
QTreeWidget::item { background:#ffffff; }
QTreeWidget::item:selected { background:#c4e4ff; color:#194f84; }
QHeaderView::section { background:#e2effa; border-bottom:1px solid #b5cde3; color:#335776; padding:7px 8px; }
QGroupBox { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ffffff,stop:1 #e6f1fb);
 border:1px solid #b9cede; border-radius:16px; margin-top:17px; padding:14px 9px 9px; }
QGroupBox::title { subcontrol-origin:margin; subcontrol-position:top left; left:14px; padding:2px 5px; background:#e7f2fc; color:#446987; }
QSplitter#psWorkspaceSplitter::handle:vertical { background:#d2e4f3; border-top:2px solid #ffffff; border-bottom:2px solid #95b4d4; height:14px; }
QWidget#psResizeTab, QWidget#psCompressTab, QWidget#psEnhanceTab, QWidget#psUploadTab { background:#ecf4fd; }
QScrollArea#psEditorScroll_psResizeTab, QScrollArea#psEditorScroll_psCompressTab,
QScrollArea#psEditorScroll_psEnhanceTab, QScrollArea#psEditorScroll_psUploadTab { background:#ecf4fd; border:0; }
QFrame#psStudioPanel QTabWidget#psStudioTabs::pane { background:#f1f8ff; border:1px solid #b9d6eb; border-radius:13px; padding:8px; }
QTabBar#psStudioTabBar { background:#e8f3fc; border:0; }
QTabBar#psStudioTabBar::tab { background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #ffffff,stop:1 #d6e5f3);
 color:#4b6f91; border:1px solid #bed2e4; border-radius:11px; margin:0 3px 5px 0; padding:9px 12px; }
QTabBar#psStudioTabBar::tab:selected { background:@ACCENT@; color:#1c426d; border-color:@ACCENT@; }
QTabBar#psStudioTabBar::tab:hover { background:#d9ecfc; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background:#ffffff; border:1px solid #bed2e5; color:#2b4865; }
)LIGHT");
    sheet.replace(QStringLiteral("@ACCENT@"), PixelShroomPhase15Theme::accent().name());
    return sheet;
}

inline QString panel(bool dark) {
    QString sheet;
    if (dark) sheet = QString::fromUtf8(R"DARK(
QFrame#psStudioPanel { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #5b7390,stop:0.15 #435d7a,stop:1 #243b54);
 border:1px solid #a0bbd5; border-top:2px solid #c3dcef; border-radius:22px; }
QFrame#psStudioPanel QTabWidget#psStudioTabs::pane { background:#273e56; border:1px solid #7696b4; border-radius:13px; }
QFrame#psStudioPanel QTabBar#psStudioTabBar { background:#273e56; }
QFrame#psStudioPanel QTabBar#psStudioTabBar::tab { background:#4c6480; color:#e9f4ff; border:1px solid #809ab6; border-radius:11px; margin:0 3px 5px 0; padding:9px 12px; }
QFrame#psStudioPanel QTabBar#psStudioTabBar::tab:selected { background:@ACCENT@; color:#102842; border-color:@ACCENT@; }
QFrame#psStudioPanel QWidget#psResizeTab, QFrame#psStudioPanel QWidget#psCompressTab,
QFrame#psStudioPanel QWidget#psEnhanceTab, QFrame#psStudioPanel QWidget#psUploadTab { background:#273e56; }
QFrame#psStudioPanel QScrollArea#psEditorScroll_psResizeTab,
QFrame#psStudioPanel QScrollArea#psEditorScroll_psCompressTab,
QFrame#psStudioPanel QScrollArea#psEditorScroll_psEnhanceTab,
QFrame#psStudioPanel QScrollArea#psEditorScroll_psUploadTab { background:#273e56; border:0; }
)DARK");
    else sheet = QString::fromUtf8(R"LIGHT(
QFrame#psStudioPanel { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ffffff,stop:0.2 #f1f8ff,stop:1 #d5e5f6);
 border:1px solid #afcbe2; border-top:2px solid #ffffff; border-radius:22px; }
QFrame#psStudioPanel QTabWidget#psStudioTabs::pane { background:#f3f8fd; border:1px solid #bfd8ea; border-radius:13px; }
QFrame#psStudioPanel QTabBar#psStudioTabBar { background:#e8f3fc; }
QFrame#psStudioPanel QTabBar#psStudioTabBar::tab { background:#dceaf8; color:#456784; border:1px solid #b5cadf; border-radius:11px; margin:0 3px 5px 0; padding:9px 12px; }
QFrame#psStudioPanel QTabBar#psStudioTabBar::tab:selected { background:@ACCENT@; color:#173c61; border-color:@ACCENT@; }
QFrame#psStudioPanel QWidget#psResizeTab, QFrame#psStudioPanel QWidget#psCompressTab,
QFrame#psStudioPanel QWidget#psEnhanceTab, QFrame#psStudioPanel QWidget#psUploadTab { background:#f1f7fe; }
QFrame#psStudioPanel QScrollArea#psEditorScroll_psResizeTab,
QFrame#psStudioPanel QScrollArea#psEditorScroll_psCompressTab,
QFrame#psStudioPanel QScrollArea#psEditorScroll_psEnhanceTab,
QFrame#psStudioPanel QScrollArea#psEditorScroll_psUploadTab { background:#f1f7fe; border:0; }
)LIGHT");
    sheet.replace(QStringLiteral("@ACCENT@"), PixelShroomPhase15Theme::accent().name());
    return sheet;
}
} // namespace PixelShroomPhase17Theme
