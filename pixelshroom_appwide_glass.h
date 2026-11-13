#pragma once
// Pixel Shroom Image Studio — Phase 14 universal glass Qt Widgets treatment.
// The OS-level compositor material remains managed by pixelshroom_native_glass.h.
// This sheet styles application surfaces and controls, not the artwork pixels.
// All controls remain native Qt Widgets and retain keyboard/accessibility behavior.
#include <QString>

namespace PixelShroomAppGlass {

inline QString widgets(bool dark) {
    if (!dark) return QString::fromUtf8(R"OPAL(
/* Phase 14 — opal glass, application-wide */
QWidget { font-family: 'Segoe UI Variable', 'Segoe UI'; }
QMenuBar { background:rgba(250,253,255,205); border-bottom:1px solid rgba(161,184,208,115); padding:5px 8px; }
QMenuBar::item { padding:8px 13px; border-radius:10px; }
QMenuBar::item:selected { background:rgba(111,163,231,74); }
QMenu { background:#f8fbff; color:#254261; border:1px solid #cddbea; border-radius:12px; padding:7px; }
QMenu::item { padding:9px 26px; border-radius:8px; }
QMenu::item:selected { background:#d7e8fa; color:#1d5398; }
QToolBar { background:rgba(244,250,255,192); border:0; border-bottom:1px solid rgba(158,180,205,116); padding:9px; spacing:8px; }
QToolBar QToolButton { background:rgba(255,255,255,125); border:1px solid transparent; border-radius:12px; color:#2c4a6c; padding:7px 11px; min-height:26px; }
QToolBar QToolButton:hover { background:rgba(231,243,255,238); border-color:#bdd4ed; }
QToolBar QToolButton:pressed { background:#d2e6fc; }
QPushButton, QToolButton, QDialogButtonBox QPushButton {
    background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 rgba(255,255,255,249), stop:1 rgba(228,238,250,225));
    color:#284767; border:1px solid #c9d9e9; border-radius:12px;
    padding:8px 14px; min-height:25px; font-weight:600;
}
QPushButton:hover, QToolButton:hover { background:#e2f1ff; color:#1d4f8c; border-color:#83b9e9; }
QPushButton:pressed, QToolButton:pressed { background:#cfe3fb; }
QPushButton:disabled, QToolButton:disabled { background:#e5eaf0; color:#99a7b8; border-color:#d6e0e9; }
QPushButton:focus, QToolButton:focus { border:2px solid #5d9bea; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
    background:rgba(255,255,255,222); color:#243d5b; border:1px solid #c4d5e8;
    border-radius:11px; padding:6px 10px; min-height:28px; selection-background-color:#8cbbf4;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus { border:2px solid #67a3ed; }
QComboBox::drop-down { border:none; width:27px; }
QComboBox QAbstractItemView { background:#f7fbff; color:#263e59; selection-background-color:#d2e8ff; border:1px solid #bed0e8; }
QTabWidget::pane { background:rgba(249,252,255,158); border:1px solid rgba(255,255,255,215); border-radius:18px; padding:10px; }
QTabBar::tab { background:rgba(232,241,251,176); color:#5e7793; border:1px solid #d4e0ed; border-radius:11px; margin:3px 4px 7px 0; padding:10px 14px; }
QTabBar::tab:hover { background:#e5f2ff; }
QTabBar::tab:selected { background:rgba(255,255,255,245); color:#2365ad; border-color:#9dbfe6; font-weight:700; }
QGroupBox { background:rgba(255,255,255,165); border:1px solid rgba(255,255,255,225); border-radius:17px; margin-top:18px; padding:15px 12px 10px; }
QGroupBox::title { subcontrol-origin:margin; subcontrol-position:top left; left:12px; padding:1px 9px; color:#456888; font-weight:600; }
QDockWidget { background:transparent; color:#496986; }
QDockWidget::title { background:rgba(249,252,255,188); border-bottom:1px solid #d7e4f0; padding:10px 14px; }
QWidget#dockWidgetContents, QWidget#scrollAreaWidgetContents { background:transparent; }
QScrollArea#scrollArea { background:rgba(250,253,255,80); border:0; border-radius:17px; }
QScrollArea#scrollArea > QWidget { background:transparent; }
QFrame#frame, QFrame#frame_2 { background:rgba(247,250,255,187); border:1px solid rgba(203,220,240,185); border-radius:18px; }
QWidget#labelPreview { background:transparent; border:0; }
QTreeWidget#treeWidget, QTreeView, QTableView, QListView {
    background:rgba(255,255,255,190); color:#283f5b; alternate-background-color:rgba(232,242,254,177);
    border:1px solid rgba(187,207,228,180); border-radius:17px;
    selection-background-color:#cce4ff; selection-color:#163c67; gridline-color:#d2e0ef;
}
QTreeWidget::item, QTreeView::item { padding:5px 7px; min-height:24px; }
QTreeWidget::item:hover, QTreeView::item:hover { background:#e8f3ff; border-radius:7px; }
QHeaderView::section { background:rgba(231,241,251,232); color:#375a7a; border:0; border-bottom:1px solid #c8dced; padding:9px 11px; font-weight:600; }
QDialog { background:#eaf1fa; color:#28415e; }
QDialog QLabel, QDialog QCheckBox, QDialog QRadioButton { background:transparent; }
QGraphicsView#psGlassImageCanvas, QLabel#psGlassImageCanvas {
    background:rgba(244,249,255,164); border:1px solid rgba(167,193,221,175); border-radius:16px;
}
QDialog#psGlassCompareDialog, QDialog#psGlassLivePreview, QDialog#psGlassLegacyPreviewDialog { background:#ecf3fc; }
QStatusBar { background:rgba(246,250,255,200); border-top:1px solid #d6e3f1; color:#526e87; }
QProgressBar { background:rgba(219,233,249,200); border:1px solid #c6d8eb; border-radius:8px; color:#24486c; text-align:center; min-height:15px; }
QProgressBar::chunk { background:#73a9eb; border-radius:7px; }
QSlider::groove:horizontal { background:#c8d9ee; height:5px; border-radius:3px; }
QSlider::handle:horizontal { background:#ffffff; border:2px solid #5c9be9; border-radius:11px; width:18px; margin:-8px 0; }
QScrollBar:vertical { background:transparent; width:12px; margin:2px; }
QScrollBar:horizontal { background:transparent; height:12px; margin:2px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal { background:rgba(125,159,194,180); border-radius:6px; min-height:27px; min-width:27px; }
QToolTip { background:#f7fbff; color:#284a6d; border:1px solid #bfd2e8; padding:7px; }
)OPAL");
    return QString::fromUtf8(R"SMOKE(
/* Phase 14 — smoke glass, application-wide */
QWidget { font-family:'Segoe UI Variable','Segoe UI'; }
QMenuBar { background:rgba(25,36,54,205); border-bottom:1px solid rgba(118,149,182,95); padding:5px 8px; }
QMenuBar::item { padding:8px 13px; border-radius:10px; }
QMenuBar::item:selected { background:rgba(95,130,172,88); }
QMenu { background:#26374e; color:#eaf4ff; border:1px solid #526983; border-radius:12px; padding:7px; }
QMenu::item { padding:9px 26px; border-radius:8px; }
QMenu::item:selected { background:#3a5678; color:#f4f9ff; }
QToolBar { background:rgba(27,40,60,210); border:0; border-bottom:1px solid rgba(120,151,190,95); padding:9px; spacing:8px; }
QToolBar QToolButton { background:rgba(66,86,112,85); color:#e7f3ff; border:1px solid transparent; border-radius:12px; padding:7px 11px; min-height:26px; }
QToolBar QToolButton:hover { background:#405d7f; border-color:#789ac0; }
QToolBar QToolButton:pressed { background:#354d70; }
QPushButton, QToolButton, QDialogButtonBox QPushButton {
    background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 rgba(91,113,143,234),stop:1 rgba(48,69,94,231));
    color:#f1f7ff; border:1px solid #6984a6; border-radius:12px;
    padding:8px 14px; min-height:25px; font-weight:600;
}
QPushButton:hover, QToolButton:hover { background:#496a92; border-color:#a5c5ee; }
QPushButton:pressed, QToolButton:pressed { background:#37577c; }
QPushButton:disabled, QToolButton:disabled { background:#293a50; color:#8297ae; border-color:#485b75; }
QPushButton:focus, QToolButton:focus { border:2px solid #a1c9fc; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QPlainTextEdit {
    background:rgba(38,57,83,229); color:#f2f8ff; border:1px solid #607d9c;
    border-radius:11px; padding:6px 10px; min-height:28px; selection-background-color:#446c9f;
}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus { border:2px solid #9dc8ff; }
QComboBox::drop-down { border:none; width:27px; }
QComboBox QAbstractItemView { background:#253b56; color:#f0f6ff; selection-background-color:#3c6591; border:1px solid #5b789a; }
QTabWidget::pane { background:rgba(35,53,76,190); border:1px solid rgba(139,171,210,115); border-radius:18px; padding:10px; }
QTabBar::tab { background:rgba(57,79,107,182); color:#c6daef; border:1px solid #526d8a; border-radius:11px; margin:3px 4px 7px 0; padding:10px 14px; }
QTabBar::tab:hover { background:#4b688d; }
QTabBar::tab:selected { background:#8db6e7; color:#132d4b; border-color:#b1d4ff; font-weight:700; }
QGroupBox { background:rgba(50,67,92,179); border:1px solid rgba(148,176,209,108); border-radius:17px; margin-top:18px; padding:15px 12px 10px; }
QGroupBox::title { subcontrol-origin:margin; subcontrol-position:top left; left:12px; padding:1px 9px; color:#c6ddf5; font-weight:600; }
QDockWidget { background:transparent; color:#d2e4f8; }
QDockWidget::title { background:rgba(37,53,76,222); border-bottom:1px solid #516a87; padding:10px 14px; }
QWidget#dockWidgetContents, QWidget#scrollAreaWidgetContents { background:transparent; }
QScrollArea#scrollArea { background:rgba(29,45,64,76); border:0; border-radius:17px; }
QScrollArea#scrollArea > QWidget { background:transparent; }
QFrame#frame, QFrame#frame_2 { background:rgba(44,62,84,206); border:1px solid rgba(128,159,190,135); border-radius:18px; }
QWidget#labelPreview { background:transparent; border:0; }
QTreeWidget#treeWidget, QTreeView, QTableView, QListView {
    background:rgba(28,43,63,226); color:#e9f2ff; alternate-background-color:rgba(40,60,84,213);
    border:1px solid rgba(106,139,174,153); border-radius:17px;
    selection-background-color:#496f9a; selection-color:#ffffff; gridline-color:#435a75;
}
QTreeWidget::item, QTreeView::item { padding:5px 7px; min-height:24px; }
QTreeWidget::item:hover, QTreeView::item:hover { background:#3b597a; border-radius:7px; }
QHeaderView::section { background:rgba(43,64,89,243); color:#d6e7fa; border:0; border-bottom:1px solid #56708d; padding:9px 11px; font-weight:600; }
QDialog { background:#1b293e; color:#eaf4ff; }
QDialog QLabel, QDialog QCheckBox, QDialog QRadioButton { background:transparent; }
QGraphicsView#psGlassImageCanvas, QLabel#psGlassImageCanvas {
    background:rgba(22,37,55,195); border:1px solid rgba(116,148,181,151); border-radius:16px;
}
QDialog#psGlassCompareDialog, QDialog#psGlassLivePreview, QDialog#psGlassLegacyPreviewDialog { background:#202e45; }
QStatusBar { background:rgba(24,38,57,223); border-top:1px solid #48617c; color:#acc4df; }
QProgressBar { background:#263a55; border:1px solid #516e8f; border-radius:8px; color:#f0f7ff; text-align:center; min-height:15px; }
QProgressBar::chunk { background:#7aa9e6; border-radius:7px; }
QSlider::groove:horizontal { background:#577395; height:5px; border-radius:3px; }
QSlider::handle:horizontal { background:#eaf5ff; border:2px solid #8dbaff; border-radius:11px; width:18px; margin:-8px 0; }
QScrollBar:vertical { background:transparent; width:12px; margin:2px; }
QScrollBar:horizontal { background:transparent; height:12px; margin:2px; }
QScrollBar::handle:vertical, QScrollBar::handle:horizontal { background:rgba(125,156,194,171); border-radius:6px; min-height:27px; min-width:27px; }
QToolTip { background:#273d58; color:#f0f8ff; border:1px solid #7899bd; padding:7px; }
)SMOKE");
}

inline QString settingsPanel(bool dark) {
    if (!dark) return QString::fromUtf8(R"OPAL(
QWidget#psSettingsTab { background:transparent; }
QFrame#psAppearanceCard { background:rgba(255,255,255,190); border:1px solid #d2e2f0; border-radius:17px; }
QFrame#psAppearanceCard QLabel { background:transparent; border:none; color:#345371; }
QFrame#psAppearanceCard QLabel#psAppearanceTitle { color:#214a75; font-size:13pt; font-weight:700; }
QFrame#psAppearanceCard QToolButton#psGlassModeToggle { background:#e1f0ff; color:#1e5c9c; border:1px solid #9cc5ef; border-radius:12px; }
QLabel#psNativeGlassStatus { color:#536d87; }
)OPAL");
    return QString::fromUtf8(R"SMOKE(
QWidget#psSettingsTab { background:transparent; }
QFrame#psAppearanceCard { background:rgba(40,57,79,218); border:1px solid #6a88a7; border-radius:17px; }
QFrame#psAppearanceCard QLabel { background:transparent; border:none; color:#c2daf2; }
QFrame#psAppearanceCard QLabel#psAppearanceTitle { color:#eef6ff; font-size:13pt; font-weight:700; }
QFrame#psAppearanceCard QToolButton#psGlassModeToggle { background:#436487; color:#eff8ff; border:1px solid #8cadcf; border-radius:12px; }
QLabel#psNativeGlassStatus { color:#b5cbe4; }
)SMOKE");
}
} // namespace PixelShroomAppGlass
