#pragma once
// Pixel Shroom Image Studio – Phase 11 glass-inspired Qt Widgets palette.
// Visual-only; avoids native DWM calls and keeps Windows 10 support.
#include <QString>

namespace PixelShroomGlass {
inline QString window() {
    return QString::fromUtf8(R"QSS(
QMainWindow, QWidget#centralwidget {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                 stop:0 #0a1020, stop:0.44 #121b2b, stop:1 #090e19);
    color: #e9f2ff;
    font-family: 'Segoe UI'; font-size: 10pt;
}
QMenuBar { background: #101b2b; color: #e8f3ff; border-bottom: 1px solid #34475f; }
QMenuBar::item { padding: 6px 12px; border-radius: 6px; }
QMenuBar::item:selected { background: #304c6c; }
QMenu { background: #172638; color: #e8f3ff; border: 1px solid #55708e;
        border-radius: 9px; padding: 5px; }
QMenu::item { padding: 7px 26px; }
QMenu::item:selected { background: #355b7c; }
QToolBar { background: #132237; border: none; border-bottom: 1px solid #32455f;
           spacing: 8px; padding: 5px; }
QDockWidget { color: #e8f2ff; font-weight: 600; }
QDockWidget::title { background: #1b2c42; padding: 8px 10px; border: 1px solid #334b63; }
QStatusBar { background: #101a2b; color: #a9c7df; border-top: 1px solid #33475d; }
QGroupBox { background: rgba(26,43,64,200); border: 1px solid #465c75;
            border-radius: 12px; margin-top: 18px; padding: 13px 10px 10px; color:#e7f1fb; }
QGroupBox::title { subcontrol-origin: margin; left: 11px; padding: 1px 6px;
                   color: #b9eaff; font-weight: 600; }
QLabel, QCheckBox, QRadioButton { color: #e8f2fc; background: transparent; }
QPushButton, QToolButton { color: #eaf6ff; font-weight: 600;
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #334e6b,stop:1 #25394f);
    border: 1px solid #6987a4; border-radius: 9px; padding: 7px 12px; min-height: 24px; }
QPushButton:hover, QToolButton:hover { border-color: #77d9f6; background: #355775; }
QPushButton:pressed, QToolButton:pressed { background: #1e354c; }
QPushButton:disabled, QToolButton:disabled { color: #8498ae; background: #233145; border-color: #354657; }
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #172a40; color: #f1f8ff; selection-background-color: #327ca0;
    border: 1px solid #55728e; border-radius: 8px; min-height: 27px; padding: 3px 8px; }
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus {
    border-color: #75ddfc; }
QComboBox::drop-down { border: 0; width: 24px; }
QComboBox QAbstractItemView { background: #15283f; color: #e8f3ff;
                               selection-background-color: #356081; border: 1px solid #55728e; }
QTabWidget::pane { border: 1px solid #455e78; background: #142439;
                   border-radius: 11px; padding: 6px; }
QTabBar::tab { color: #c2d7ea; background: #263a52; border: 1px solid #425b78;
               padding: 9px 14px; min-width: 66px; }
QTabBar::tab:hover { background: #355471; }
QTabBar::tab:selected { color: #061627; background: #8bdffa; border-color: #b9f2ff; font-weight:700; }
QTreeView, QTreeWidget, QTableView, QListView { background: #101d2f; color: #e8f2ff;
    alternate-background-color: #19293e; gridline-color: #324a63;
    border: 1px solid #425d79; border-radius: 8px; selection-background-color: #315b80; }
QHeaderView::section { background: #22364c; color: #d7ebf9; padding: 8px 10px;
                       border: none; border-right: 1px solid #3b5570; }
QScrollBar:vertical { background: #132137; width: 12px; }
QScrollBar::handle:vertical { background: #526f8a; min-height: 30px; border-radius: 5px; }
QScrollBar:horizontal { background: #132137; height: 12px; }
QScrollBar::handle:horizontal { background: #526f8a; min-width: 30px; border-radius: 5px; }
QSlider::groove:horizontal { height: 5px; background: #49647d; border-radius: 2px; }
QSlider::handle:horizontal { background: #8bdffa; border: 1px solid #c3f5ff;
                             border-radius: 9px; width: 17px; margin: -7px 0; }
QProgressBar { color: #e4f5ff; background: #1c3045; border: 1px solid #526981;
               border-radius: 6px; text-align: center; }
QProgressBar::chunk { background: #55b8de; border-radius: 5px; }
QToolTip { color: #eaf7ff; background: #1e3048; border: 1px solid #74b4d5; }
)QSS");
}
inline QString panel() {
    return QString::fromUtf8(R"QSS(
QFrame#psStudioPanel { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
       stop:0 rgba(47,77,105,230),stop:0.52 rgba(29,48,72,222),stop:1 rgba(18,33,53,237));
       border: 1px solid #7493ad; border-radius: 17px; color:#f0f9ff; }
QFrame#psStudioPanel QLabel, QFrame#psStudioPanel QCheckBox {
       color:#edf7ff; border:none; background:transparent; }
QFrame#psStudioPanel QTabWidget::pane { border:1px solid #4c6b84; border-radius:11px;
       background:rgba(16,34,55,210); }
QWidget#psResizeTab, QWidget#psCompressTab, QWidget#psEnhanceTab, QWidget#psUploadTab {
       background:#15263a; color:#eff8ff; }
QFrame#psStudioPanel QTabBar::tab { background:#263e58; color:#d6e8f6; border:1px solid #45647f;
       min-width:72px; padding:9px 12px; }
QFrame#psStudioPanel QTabBar::tab:selected { background:#98e5ff; color:#092237; font-weight:700; }
QFrame#psStudioPanel QComboBox, QFrame#psStudioPanel QSpinBox,
QFrame#psStudioPanel QDoubleSpinBox { background:#1d334b; color:#f2faff; border:1px solid #647f98;
       border-radius:8px; min-height:27px; padding:2px 7px; }
QFrame#psStudioPanel QPushButton, QFrame#psStudioPanel QToolButton { background:#315878;
       color:#f5fbff; border:1px solid #75a4c3; border-radius:8px; padding:6px 11px; }
QFrame#psStudioPanel QPushButton:hover, QFrame#psStudioPanel QToolButton:hover { background:#3c7091; }
QFrame#psStudioPanel QSlider::groove:horizontal { height:5px; background:#57748e; border-radius:2px; }
QFrame#psStudioPanel QSlider::handle:horizontal { background:#91e8ff; border-radius:8px;
       width:17px; margin:-6px 0; }
)QSS");
}
} // namespace PixelShroomGlass
