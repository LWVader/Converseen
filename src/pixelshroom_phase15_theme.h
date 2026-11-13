#pragma once
/*
 * Pixel Shroom Image Studio — Phase 15 responsive glass materials.
 * Visual-only: does not affect bitmap pixels, ImageMagick or conversion settings.
 * Native Windows Acrylic/Mica continues to be managed by BackdropController.
 */
#include <QColor>
#include <QSettings>
#include <QString>

namespace PixelShroomPhase15Theme {

inline QColor accent() {
    QSettings s(QStringLiteral("Pixel Shroom Studio"),
                QStringLiteral("Pixel Shroom Image Studio"));
    QColor color(s.value(QStringLiteral("appearance/accentColor"),
                         QStringLiteral("#78b6f7")).toString());
    return color.isValid() ? color : QColor(QStringLiteral("#78b6f7"));
}
inline QString canvasChoice() {
    QSettings s(QStringLiteral("Pixel Shroom Studio"),
                QStringLiteral("Pixel Shroom Image Studio"));
    return s.value(QStringLiteral("appearance/canvasColor"),
                   QStringLiteral("auto")).toString();
}
inline QColor canvas(bool dark) {
    if (canvasChoice() == QStringLiteral("auto"))
        return dark ? QColor(18, 29, 48) : QColor(232, 241, 251);
    const QColor c(canvasChoice());
    return c.isValid() ? c : (dark ? QColor(18,29,48) : QColor(232,241,251));
}
inline QString rgba(const QColor &c, int a) {
    return QStringLiteral("rgba(%1,%2,%3,%4)")
        .arg(c.red()).arg(c.green()).arg(c.blue()).arg(a);
}

// Installed LAST in the app's global stylesheet, but BEFORE the native DWM
// root transparency overrides. Keep opaque fills off the window backdrop.
inline QString app(bool dark) {
    const QColor a = accent();
    const QColor mat = canvas(dark);
    const QString border = dark ? QStringLiteral("rgba(211,234,255,80)")
                                : QStringLiteral("rgba(255,255,255,186)");
    const QString cardTop = dark ? QStringLiteral("rgba(157,186,222,80)")
                                 : QStringLiteral("rgba(255,255,255,155)");
    const QString cardBottom = dark ? QStringLiteral("rgba(29,48,75,104)")
                                    : QStringLiteral("rgba(215,231,249,101)");
    const QString text = dark ? QStringLiteral("#edf6ff") : QStringLiteral("#263b57");
    const QString selected = dark ? QStringLiteral("#112640") : QStringLiteral("#142940");
    const QString light = a.lighter(125).name();
    const QString hover = dark ? rgba(a, 107) : rgba(a, 61);
    const QString pane = dark ? QStringLiteral("rgba(28,47,72,78)")
                               : QStringLiteral("rgba(255,255,255,73)");
    const QString canvasBg = rgba(mat, 213);

    QString qss = QString::fromUtf8(R"QSS(
/* Phase 15: optical depth, nested translucent glass, clear focus */
QWidget#psSettingsTab, QWidget#psSettingsContent, QScrollArea#psSettingsScroll,
QScrollArea#psSettingsScroll > QWidget, QTabWidget#psStudioTabs { background:transparent; border:none; }
QFrame#psAppearanceCard, QFrame#psPersonalizationCard,
QGroupBox#groupBox_3, QGroupBox#groupBox_4,
QGroupBox#groupBox, QGroupBox#groupBox_2 {
 background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
  stop:0 @CARDTOP@, stop:0.45 @PANE@, stop:1 @CARDBOTTOM@);
 border:1px solid @BORDER@; border-radius:18px; padding:11px;
}
QFrame#psAppearanceCard QLabel, QFrame#psPersonalizationCard QLabel,
QFrame#psAppearanceCard QCheckBox, QFrame#psPersonalizationCard QCheckBox {
 background:transparent; border:0; color:@TEXT@;
}
QFrame#psAppearanceCard QLabel#psAppearanceTitle,
QFrame#psPersonalizationCard QLabel#psPersonalizationTitle { font-weight:700; font-size:13pt; }
QFrame#psAppearanceCard QToolButton#psGlassModeToggle { border-color:@ACCENT@; }
QTabWidget#psStudioTabs::pane { background:@PANE@; border:1px solid @BORDER@; border-radius:16px; padding:7px; }
QTabWidget#psStudioTabs QTabBar::tab:selected { background:@ACCENT@; color:@SELECTED@; border-color:@LIGHT@; }
QTabWidget#psStudioTabs QTabBar::tab:hover { background:@HOVER@; border-color:@ACCENT@; }
QWidget#labelPreview, QGraphicsView#psGlassImageCanvas,
QLabel#psGlassImageCanvas, QAbstractScrollArea#psGlassImageCanvas {
 background:@CANVAS@; border:1px solid @BORDER@; border-radius:17px;
}
QTreeWidget#treeWidget { background:@PANE@; border:1px solid @BORDER@; border-radius:15px;
 selection-background-color:@HOVER@; selection-color:@TEXT@; }
QHeaderView::section { background:@PANE@; border-bottom:1px solid @BORDER@; color:@TEXT@; }
QTreeWidget::item:selected, QTableView::item:selected { background:@HOVER@; color:@TEXT@; }
QSplitter#psWorkspaceSplitter::handle:vertical { background:@HOVER@; border-radius:3px; height:8px; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus,
QPushButton:focus, QToolButton:focus { border:2px solid @ACCENT@; }
QSlider::handle:horizontal { border:2px solid @ACCENT@; }
QToolTip { border:1px solid @ACCENT@; }
)QSS");
    qss.replace(QStringLiteral("@ACCENT@"), a.name());
    qss.replace(QStringLiteral("@LIGHT@"), light);
    qss.replace(QStringLiteral("@SELECTED@"), selected);
    qss.replace(QStringLiteral("@HOVER@"), hover);
    qss.replace(QStringLiteral("@PANE@"), pane);
    qss.replace(QStringLiteral("@CARDTOP@"), cardTop);
    qss.replace(QStringLiteral("@CARDBOTTOM@"), cardBottom);
    qss.replace(QStringLiteral("@BORDER@"), border);
    qss.replace(QStringLiteral("@TEXT@"), text);
    qss.replace(QStringLiteral("@CANVAS@"), canvasBg);
    return qss;
}

// The Image Studio QFrame has a local stylesheet; override THAT sheet too.
inline QString panel(bool dark) {
    const QColor a = accent();
    QString qss = dark ? QString::fromUtf8(R"QSS(
QFrame#psStudioPanel {
 background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
 stop:0 rgba(133,166,202,115),stop:0.5 rgba(33,54,84,107),stop:1 rgba(40,61,91,132));
 border:1px solid rgba(204,230,255,132); border-radius:24px;
}
QFrame#psStudioPanel QTabWidget#psStudioTabs::pane { background:rgba(21,39,63,66); border:1px solid rgba(194,224,255,112); border-radius:17px; padding:7px; }
QFrame#psStudioPanel QFrame#psAppearanceCard, QFrame#psStudioPanel QFrame#psPersonalizationCard {
 background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(169,199,231,109),stop:0.55 rgba(68,97,132,72),stop:1 rgba(27,49,81,105));
 border:1px solid rgba(219,240,255,119); border-radius:19px;
}
)QSS") : QString::fromUtf8(R"QSS(
QFrame#psStudioPanel {
 background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
 stop:0 rgba(255,255,255,170),stop:0.53 rgba(243,250,255,116),stop:1 rgba(218,236,252,139));
 border:1px solid rgba(255,255,255,226); border-radius:24px;
}
QFrame#psStudioPanel QTabWidget#psStudioTabs::pane { background:rgba(255,255,255,74); border:1px solid rgba(255,255,255,175); border-radius:17px; padding:7px; }
QFrame#psStudioPanel QFrame#psAppearanceCard, QFrame#psStudioPanel QFrame#psPersonalizationCard {
 background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 rgba(255,255,255,184),stop:0.55 rgba(255,255,255,92),stop:1 rgba(216,231,248,106));
 border:1px solid rgba(255,255,255,229); border-radius:19px;
}
)QSS");
    qss += QString::fromUtf8(R"QSS(
QFrame#psStudioPanel QTabWidget#psStudioTabs QTabBar::tab:selected {
 background:@ACCENT@; color:@SELECTED@; border:1px solid @ACCENT@;
}
QFrame#psStudioPanel QTabWidget#psStudioTabs QTabBar::tab:hover {
 background:@HOVER@; border:1px solid @ACCENT@;
}
QFrame#psStudioPanel QPushButton#psUploadAction {
 background:@ACCENT@; color:@SELECTED@; border:1px solid @ACCENT@; font-weight:700;
}
QFrame#psStudioPanel QFrame#psAppearanceCard QLabel,
QFrame#psStudioPanel QFrame#psPersonalizationCard QLabel { background:transparent; border:0; }
)QSS");
    qss.replace(QStringLiteral("@ACCENT@"), a.name());
    qss.replace(QStringLiteral("@SELECTED@"), dark ? QStringLiteral("#112640") : QStringLiteral("#142940"));
    qss.replace(QStringLiteral("@HOVER@"), rgba(a, dark ? 92 : 67));
    return qss;
}

} // namespace PixelShroomPhase15Theme
