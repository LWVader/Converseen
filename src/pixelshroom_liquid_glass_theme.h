#pragma once
// Pixel Shroom Image Studio — Phase 12, Apple-inspired Liquid Glass styling.
// Qt Widgets visual design. Native background-blur is intentionally NOT claimed.
// Keep light/dark appearance in one source of truth. No changes to converter.
#include <QString>

namespace PixelShroomLiquidGlass {

inline QString window(bool dark = false) {
    if (!dark) return QString::fromUtf8(R"LIGHT(
/* O P A L   G L A S S — Light appearance */
QWidget { color: #26344b; font-family: 'Segoe UI Variable', 'Segoe UI', sans-serif; font-size: 10pt; }
QMainWindow, QWidget#centralwidget {
  background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
     stop:0 #e2eaf5, stop:0.30 #f3f6fc, stop:0.73 #e8f0fb, stop:1 #dbe6f4);
}
QDialog { background: #edf3fb; }
QMenuBar { background: rgba(246,249,254,235); color:#33445e; border:0; border-bottom:1px solid rgba(153,168,192,70); padding:4px 8px; }
QMenuBar::item { background:transparent; padding:7px 14px; border-radius:9px; }
QMenuBar::item:selected { background:rgba(111,158,235,65); color:#174a9e; }
QMenu { background:#f7faff; color:#293950; border:1px solid #d4e0f0; border-radius:12px; padding:7px; }
QMenu::item { padding:8px 26px; border-radius:8px; }
QMenu::item:selected { background:#dbe9ff; color:#1654a4; }
QToolBar { background:rgba(245,248,254,195); border:0; border-bottom:1px solid rgba(148,166,196,70); padding:8px 12px; spacing:9px; }
QDockWidget { background:transparent; color:#384d68; font-weight:600; }
QDockWidget::title { background:rgba(250,252,255,190); border:0; border-bottom:1px solid #dbe5f2; padding:10px 15px; }
QStatusBar { background:rgba(248,250,254,220); color:#687a92; border-top:1px solid #dae4f0; }
QGroupBox { background:rgba(255,255,255,168); border:1px solid rgba(255,255,255,237); border-radius:17px; margin-top:18px; padding:18px 13px 12px; }
QGroupBox::title { subcontrol-origin:margin; subcontrol-position:top left; left:13px; padding:1px 8px; color:#405976; font-weight:600; }
QLabel, QCheckBox, QRadioButton { color:#33435b; background:transparent; }
QCheckBox, QRadioButton { spacing:9px; }
QPushButton, QToolButton { background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 rgba(255,255,255,239),stop:1 rgba(230,239,251,218)); color:#29425e; border:1px solid #c5d5e9; border-radius:12px; padding:8px 15px; min-height:25px; font-weight:600; }
QPushButton:hover, QToolButton:hover { background:#e2eeff; border-color:#8aafe4; }
QPushButton:pressed, QToolButton:pressed { background:#d2e5ff; }
QPushButton:checked, QToolButton:checked { color:#1652a3; background:#dbeaff; border:1px solid #81b1f4; }
QPushButton:disabled, QToolButton:disabled { color:#9aabbd; background:#eef2f8; border-color:#d9e3ef; }
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
 background:rgba(255,255,255,226); color:#203852; selection-background-color:#bad7fd; border:1px solid #cddbed; border-radius:11px; min-height:30px; padding:5px 10px; }
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus { border:2px solid #5e9bf5; }
QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled { color:#9babbc; background:#edf1f8; }
QComboBox::drop-down { border:none; width:27px; }
QComboBox QAbstractItemView { background:#f7fbff; color:#283a51; selection-background-color:#cfe3ff; border:1px solid #d7e2f0; }
QTabWidget::pane { background:rgba(255,255,255,153); border:1px solid rgba(255,255,255,224); border-radius:17px; padding:8px; }
QTabBar { background:transparent; }
QTabBar::tab { background:rgba(218,229,244,132); color:#62748e; border:1px solid rgba(197,212,233,170); border-radius:11px; margin:3px 4px 7px 0; padding:9px 17px; min-width:68px; font-weight:600; }
QTabBar::tab:hover { background:#edf5ff; color:#28599e; }
QTabBar::tab:selected { background:#fff; color:#1d5bab; border:1px solid #b8d1f0; }
QTreeView, QTreeWidget, QTableView, QListView { background:rgba(255,255,255,217); color:#24364f; alternate-background-color:#f0f5fc; border:1px solid #d4e1f1; border-radius:14px; gridline-color:#e1e9f4; selection-background-color:#d2e4fd; selection-color:#19395e; }
QHeaderView::section { background:#edf4fd; color:#546985; padding:10px; border:0; border-bottom:1px solid #d4e1f1; }
QScrollBar:vertical { background:transparent; width:12px; margin:2px; }
QScrollBar::handle:vertical { background:#b9c9dc; border-radius:5px; min-height:30px; }
QScrollBar:horizontal { background:transparent; height:12px; margin:2px; }
QScrollBar::handle:horizontal { background:#b9c9dc; border-radius:5px; min-width:30px; }
QSlider::groove:horizontal { height:5px; background:#d1dfef; border-radius:3px; }
QSlider::handle:horizontal { background:#fff; border:2px solid #5c9dec; border-radius:10px; width:18px; margin:-8px 0; }
QProgressBar { background:#e4ecf7; color:#28476a; border:1px solid #ceddf0; border-radius:8px; text-align:center; min-height:16px; }
QProgressBar::chunk { background:#619cf2; border-radius:7px; }
QToolTip { background:#fafdff; color:#2c4360; border:1px solid #bdcfe7; padding:8px; }
)LIGHT");
    return QString::fromUtf8(R"DARK(
/* S M O K E   G L A S S — Dark appearance */
QWidget { color:#eaf1fa; font-family:'Segoe UI Variable','Segoe UI',sans-serif; font-size:10pt; }
QMainWindow, QWidget#centralwidget { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #101626,stop:0.32 #1c2940,stop:0.78 #161f32,stop:1 #111a2b); }
QDialog { background:#1a263a; }
QMenuBar { background:rgba(23,33,52,238); color:#e9f2fe; border:0; border-bottom:1px solid #38475d; padding:4px 8px; }
QMenuBar::item { padding:7px 14px; border-radius:9px; }
QMenuBar::item:selected { background:#2b4467; }
QMenu { background:#23334a; color:#eef5fe; border:1px solid #506784; border-radius:12px; padding:7px; }
QMenu::item { padding:8px 26px; border-radius:8px; }
QMenu::item:selected { background:#35547a; }
QToolBar { background:rgba(27,39,59,213); border:0; border-bottom:1px solid #3a4b63; spacing:9px; padding:8px 12px; }
QDockWidget { color:#dfebfa; font-weight:600; background:transparent; }
QDockWidget::title { background:rgba(35,50,72,232); border:0; border-bottom:1px solid #455977; padding:10px 15px; }
QStatusBar { background:#172236; color:#abc0dc; border-top:1px solid #3d4f6a; }
QGroupBox { background:rgba(56,70,92,168); border:1px solid rgba(154,175,205,90); border-radius:17px; margin-top:18px; padding:18px 13px 12px; }
QGroupBox::title { subcontrol-origin:margin; subcontrol-position:top left; left:13px; padding:1px 8px; color:#b7d2f4; font-weight:600; }
QLabel, QCheckBox, QRadioButton { color:#e7effb; background:transparent; }
QCheckBox, QRadioButton { spacing:9px; }
QPushButton, QToolButton { background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #40526a,stop:1 #2c3d55); color:#eff7ff; border:1px solid #617693; border-radius:12px; padding:8px 15px; min-height:25px; font-weight:600; }
QPushButton:hover, QToolButton:hover { background:#435d7e; border-color:#8eafdc; }
QPushButton:checked, QToolButton:checked { background:#36577e; border-color:#91beff; }
QPushButton:disabled, QToolButton:disabled { color:#8195ae; background:#2b3a4f; border-color:#40536d; }
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox { background:rgba(32,47,70,238); color:#f2f8ff; selection-background-color:#4775af; border:1px solid #60738e; border-radius:11px; min-height:30px; padding:5px 10px; }
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus { border:2px solid #83baff; }
QLineEdit:disabled, QSpinBox:disabled, QComboBox:disabled { color:#8294ab; background:#253448; }
QComboBox::drop-down { border:none; width:27px; }
QComboBox QAbstractItemView { background:#273a54; color:#eef6ff; selection-background-color:#476e9c; border:1px solid #5a7291; }
QTabWidget::pane { background:rgba(30,43,63,202); border:1px solid rgba(145,171,208,99); border-radius:17px; padding:8px; }
QTabBar::tab { background:rgba(55,72,97,199); color:#bfd0e5; border:1px solid #526985; border-radius:11px; margin:3px 4px 7px 0; padding:9px 17px; min-width:68px; font-weight:600; }
QTabBar::tab:hover { background:#425d80; }
QTabBar::tab:selected { background:#708eaf; color:#0e1e32; border:1px solid #aecdf2; }
QTreeView, QTreeWidget, QTableView, QListView { background:rgba(31,45,66,230); color:#eaf2fb; alternate-background-color:#283952; border:1px solid #4c6280; border-radius:14px; gridline-color:#3b4f6b; selection-background-color:#43678f; }
QHeaderView::section { background:#2a3d59; color:#d4e4f6; padding:10px; border:0; border-bottom:1px solid #4a6180; }
QScrollBar:vertical { background:transparent; width:12px; margin:2px; }
QScrollBar::handle:vertical { background:#6d84a1; border-radius:5px; min-height:30px; }
QScrollBar:horizontal { background:transparent; height:12px; margin:2px; }
QScrollBar::handle:horizontal { background:#6d84a1; border-radius:5px; min-width:30px; }
QSlider::groove:horizontal { height:5px; background:#506684; border-radius:3px; }
QSlider::handle:horizontal { background:#edf6ff; border:2px solid #91bdff; border-radius:10px; width:18px; margin:-8px 0; }
QProgressBar { background:#263750; color:#e8f5ff; border:1px solid #57708d; border-radius:8px; min-height:16px; text-align:center; }
QProgressBar::chunk { background:#76aaff; border-radius:7px; }
QToolTip { background:#263c56; color:#f3f9ff; border:1px solid #7899bd; padding:8px; }
)DARK");
}

inline QString panel(bool dark = false) {
    if (!dark) return QString::fromUtf8(R"LIGHT(
QFrame#psStudioPanel { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
  stop:0 rgba(255,255,255,232), stop:0.48 rgba(248,251,255,217), stop:1 rgba(229,240,254,224));
  border:1px solid rgba(255,255,255,251); border-radius:24px; }
QFrame#psStudioPanel QLabel, QFrame#psStudioPanel QCheckBox { background:transparent; color:#344865; border:0; }
QFrame#psStudioPanel QLabel#psStudioTitle { color:#1b304a; font-size:15pt; font-weight:700; }
QFrame#psStudioPanel QLabel#psStudioSubtitle { color:#778da8; font-size:9pt; font-weight:600; }
QFrame#psStudioPanel QTabWidget::pane { background:rgba(255,255,255,124); border:1px solid rgba(255,255,255,212); border-radius:17px; padding:12px; }
QWidget#psResizeTab, QWidget#psCompressTab, QWidget#psEnhanceTab, QWidget#psUploadTab { background:transparent; }
QFrame#psStudioPanel QTabBar::tab { background:rgba(223,233,246,154); color:#667b99; border:1px solid #d5e1ee; border-radius:12px; margin:3px 5px 8px 0; padding:10px 17px; min-width:76px; }
QFrame#psStudioPanel QTabBar::tab:selected { background:#ffffff; color:#1e62b9; border:1px solid #a8c8ef; font-weight:700; }
QFrame#psStudioPanel QTabBar::tab:hover { background:#f3f8ff; color:#2a5f9b; }
QFrame#psStudioPanel QComboBox, QFrame#psStudioPanel QSpinBox, QFrame#psStudioPanel QDoubleSpinBox { background:rgba(255,255,255,221); color:#223c59; border:1px solid #cbdcef; border-radius:10px; min-height:30px; padding:5px 9px; }
QFrame#psStudioPanel QComboBox:focus, QFrame#psStudioPanel QSpinBox:focus, QFrame#psStudioPanel QDoubleSpinBox:focus { border:2px solid #649af0; }
QFrame#psStudioPanel QPushButton, QFrame#psStudioPanel QToolButton { background:rgba(255,255,255,221); color:#294d77; border:1px solid #c8d9ed; border-radius:12px; padding:8px 14px; }
QFrame#psStudioPanel QPushButton:hover, QFrame#psStudioPanel QToolButton:hover { background:#e4efff; border-color:#8caee0; }
QFrame#psStudioPanel QToolButton#psGlassModeToggle { background:rgba(234,240,249,195); color:#4d6583; }
QFrame#psStudioPanel QPushButton#psUploadAction { color:#ffffff; font-weight:700; background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #508eeb,stop:1 #256ad2); border:1px solid #4779c3; min-height:35px; }
QFrame#psStudioPanel QPushButton#psUploadAction:hover { background:#317be9; }
QFrame#psStudioPanel QSlider::groove:horizontal { height:5px; background:#cfdef2; border-radius:3px; }
QFrame#psStudioPanel QSlider::handle:horizontal { background:#ffffff; border:2px solid #468aeb; border-radius:10px; width:18px; margin:-8px 0; }
)LIGHT");
    return QString::fromUtf8(R"DARK(
QFrame#psStudioPanel { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(64,82,109,235),stop:0.48 rgba(39,55,77,233),stop:1 rgba(29,43,65,231)); border:1px solid #768fac; border-radius:24px; }
QFrame#psStudioPanel QLabel, QFrame#psStudioPanel QCheckBox { background:transparent; color:#e8f1fb; border:0; }
QFrame#psStudioPanel QLabel#psStudioTitle { color:#f5faff; font-size:15pt; font-weight:700; }
QFrame#psStudioPanel QLabel#psStudioSubtitle { color:#a2bddb; font-size:9pt; font-weight:600; }
QFrame#psStudioPanel QTabWidget::pane { background:rgba(28,41,60,190); border:1px solid rgba(153,180,215,95); border-radius:17px; padding:12px; }
QWidget#psResizeTab, QWidget#psCompressTab, QWidget#psEnhanceTab, QWidget#psUploadTab { background:transparent; }
QFrame#psStudioPanel QTabBar::tab { background:rgba(61,81,110,171); color:#ccdbed; border:1px solid #657d9e; border-radius:12px; margin:3px 5px 8px 0; padding:10px 17px; min-width:76px; }
QFrame#psStudioPanel QTabBar::tab:selected { background:#93b7e7; color:#122e4e; border:1px solid #b4d3ff; font-weight:700; }
QFrame#psStudioPanel QTabBar::tab:hover { background:#536f92; }
QFrame#psStudioPanel QComboBox, QFrame#psStudioPanel QSpinBox, QFrame#psStudioPanel QDoubleSpinBox { background:rgba(37,54,77,228); color:#f1f8ff; border:1px solid #708bad; border-radius:10px; min-height:30px; padding:5px 9px; }
QFrame#psStudioPanel QComboBox:focus, QFrame#psStudioPanel QSpinBox:focus, QFrame#psStudioPanel QDoubleSpinBox:focus { border:2px solid #92bfff; }
QFrame#psStudioPanel QPushButton, QFrame#psStudioPanel QToolButton { background:rgba(59,82,112,233); color:#f0f7ff; border:1px solid #7391b5; border-radius:12px; padding:8px 14px; }
QFrame#psStudioPanel QPushButton:hover, QFrame#psStudioPanel QToolButton:hover { background:#526e94; }
QFrame#psStudioPanel QToolButton#psGlassModeToggle { background:rgba(63,83,112,227); color:#dbe9fc; }
QFrame#psStudioPanel QPushButton#psUploadAction { background:qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #78aafa,stop:1 #4679ca); color:#0b1b2f; font-weight:700; border:1px solid #9ec7ff; min-height:35px; }
QFrame#psStudioPanel QPushButton#psUploadAction:hover { background:#98c0ff; }
QFrame#psStudioPanel QSlider::groove:horizontal { height:5px; background:#596f8f; border-radius:3px; }
QFrame#psStudioPanel QSlider::handle:horizontal { background:#edf7ff; border:2px solid #8bbbff; border-radius:10px; width:18px; margin:-8px 0; }
)DARK");
}

} // namespace PixelShroomLiquidGlass
