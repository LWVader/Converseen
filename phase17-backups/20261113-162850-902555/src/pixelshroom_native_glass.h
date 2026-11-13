#pragma once
/*
 * Pixel Shroom Image Studio — Phase 13 native Windows glass.
 * DWM uses the Windows compositor for system backdrop materials.
 * Windows 11 build 22621+ supports DWMWA_SYSTEMBACKDROP_TYPE.
 * This is native Windows Mica/Desktop Acrylic, NOT Apple's Liquid Glass.
 *
 * No undocumented SetWindowCompositionAttribute APIs, no frameless window,
 * no direct dependency on the Windows App SDK, no new redistributable DLLs.
 * The existing Qt Widgets surface is kept, with an opaque Qt fallback.
 */

#include <QApplication>
#include <QEvent>
#include <QFrame>
#include <QLabel>
#include <QMainWindow>
#include <QObject>
#include <QPointer>
#include <QSettings>
#include <QString>
#include <QTimer>
#include <QWidget>

#include "pixelshroom_liquid_glass_theme.h"
#include "pixelshroom_appwide_glass.h"
#include "pixelshroom_phase15_theme.h"

#if defined(Q_OS_WIN)
#  ifndef WIN32_LEAN_AND_MEAN
#    define WIN32_LEAN_AND_MEAN
#  endif
#  ifndef NOMINMAX
#    define NOMINMAX
#  endif
#  include <windows.h>
#  include <dwmapi.h>
#endif

namespace PixelShroomNativeGlass {

enum class Material : int {
    Off = 0,
    Mica = 1,
    Acrylic = 2
};

struct NativeResult {
    bool applied = false;
    QString description;
};

inline QString nativeWindowOverrides() {
    // This style MUST follow the Phase 12 QSS: an opaque Qt root would
    // conceal the real DWM backdrop even when DwmSetWindowAttribute succeeds.
    return QStringLiteral(R"QSS(
    QMainWindow { background: transparent; }
    QWidget#centralwidget { background: transparent; }
    )QSS");
}

#if defined(Q_OS_WIN)
// Use documented values instead of recent SDK identifiers because MSYS2
// MinGW headers may be older than the Windows 11 system backdrop definitions.
// DWM attribute 38: DWMWA_SYSTEMBACKDROP_TYPE (Win11 22621+).
// DWM attribute 33: DWMWA_WINDOW_CORNER_PREFERENCE.
// DWM attribute 20: DWMWA_USE_IMMERSIVE_DARK_MODE.
constexpr DWORD kSystemBackdrop = 38;
constexpr DWORD kCornerPreference = 33;
constexpr DWORD kImmersiveDarkMode = 20;
constexpr int kBackdropNone = 1;       // DWMSBT_NONE
constexpr int kBackdropMica = 2;       // DWMSBT_MAINWINDOW
constexpr int kBackdropAcrylic = 3;    // DWMSBT_TRANSIENTWINDOW
constexpr int kRoundedCorners = 2;     // DWMWCP_ROUND

using SetDwmAttributeFn = HRESULT (WINAPI *)(HWND, DWORD, LPCVOID, DWORD);
using ExtendDwmFrameFn = HRESULT (WINAPI *)(HWND, const MARGINS *);

inline NativeResult configureDwm(QMainWindow *window, Material material, bool dark) {
    if (!window)
        return {false, QStringLiteral("No main window handle")};

    HMODULE dwm = ::LoadLibraryW(L"dwmapi.dll");
    if (!dwm)
        return {false, QStringLiteral("Windows Desktop Window Manager unavailable")};

    auto setAttribute = reinterpret_cast<SetDwmAttributeFn>(
        ::GetProcAddress(dwm, "DwmSetWindowAttribute"));
    auto extendFrame = reinterpret_cast<ExtendDwmFrameFn>(
        ::GetProcAddress(dwm, "DwmExtendFrameIntoClientArea"));
    if (!setAttribute) {
        ::FreeLibrary(dwm);
        return {false, QStringLiteral("Windows system backdrop API unavailable")};
    }

    // Preserve the native title bar, minimize/maximize/close controls and
    // Windows accessibility/window-management behavior.
    const HWND hwnd = reinterpret_cast<HWND>(window->winId());
    const BOOL darkCaption = dark ? TRUE : FALSE;
    setAttribute(hwnd, kImmersiveDarkMode, &darkCaption, sizeof(darkCaption));
    const int corners = kRoundedCorners;
    setAttribute(hwnd, kCornerPreference, &corners, sizeof(corners));

    const int backdrop = material == Material::Mica ? kBackdropMica
                       : material == Material::Acrylic ? kBackdropAcrylic
                       : kBackdropNone;
    const HRESULT hr = setAttribute(hwnd, kSystemBackdrop, &backdrop, sizeof(backdrop));

    // The DWM backdrop lies behind window contents. Extend the frame into
    // the client area and make the Qt central surface non-opaque to expose it.
    // Reset extension when switching Off. On older Windows, the requested
    // backdrop HRESULT will fail and the Phase 12 Qt theme stays in place.
    HRESULT frameHr = S_OK;
    if (extendFrame) {
        const MARGINS margins = (SUCCEEDED(hr) && material != Material::Off)
            ? MARGINS{-1, -1, -1, -1}
            : MARGINS{0, 0, 0, 0};
        frameHr = extendFrame(hwnd, &margins);
    }
    ::FreeLibrary(dwm);

    if (material == Material::Off)
        return {false, QStringLiteral("Backdrop off — using the Qt glass theme")};
    if (FAILED(hr))
        return {false, QStringLiteral("Native backdrop unavailable — using Qt glass fallback")};
    if (!extendFrame || FAILED(frameHr))
        return {false, QStringLiteral("Window-wide glass unavailable — using Qt glass fallback")};

    return {true, material == Material::Acrylic
        ? QStringLiteral("Windows Desktop Acrylic active — native background blur")
        : QStringLiteral("Windows Mica active — native wallpaper-tinted backdrop")};
}
#else
inline NativeResult configureDwm(QMainWindow *, Material, bool) {
    return {false, QStringLiteral("Native glass requires Windows 11; Qt glass fallback active")};
}
#endif

// Small QObject helper, intentionally no Q_OBJECT or moc generation needed.
// Keeps native effects synchronized with the light/dark toggle and recreated
// native HWND, and handles graceful fallback without touching converter paths.
class BackdropController final : public QObject {
public:
    BackdropController(QMainWindow *window, QWidget *central,
                       QFrame *studioPanel, QLabel *status)
        : QObject(window), window_(window), central_(central),
          panel_(studioPanel), status_(status) {
        if (window_) window_->installEventFilter(this);
    }

    void setAppearance(bool dark, Material material) {
        dark_ = dark;
        material_ = material;
        updateBackdrop(true);
    }

protected:
    bool eventFilter(QObject *watched, QEvent *event) override {
        if (watched == window_ &&
            (event->type() == QEvent::Show || event->type() == QEvent::WinIdChange)) {
            // Defer until Qt has finished creating/recreating its HWND.
            QTimer::singleShot(0, this, [this]() { updateBackdrop(false); });
        }
        return QObject::eventFilter(watched, event);
    }

private:
    void updateBackdrop(bool force) {
        if (!window_ || !central_ || !panel_) return;
        const WId currentId = window_->winId();
        if (!force && currentId == previousId_) return;
        previousId_ = currentId;
        NativeResult result = configureDwm(window_, material_, dark_);
        const bool active = result.applied;
        // Never set Qt::WA_TranslucentBackground on this framed QWidget:
        // on Windows that would require FramelessWindowHint and would break
        // normal native caption buttons and window resizing.
        window_->setAutoFillBackground(false);
        central_->setAutoFillBackground(false);
        window_->setAttribute(Qt::WA_NoSystemBackground, active);
        central_->setAttribute(Qt::WA_NoSystemBackground, active);
        // Preserve native DWM backdrop while styling the entire Qt app.
        qApp->setStyleSheet(PixelShroomLiquidGlass::window(dark_) +
                            PixelShroomAppGlass::widgets(dark_) +
                            PixelShroomPhase15Theme::app(dark_) +
                            (active ? nativeWindowOverrides() : QString()));
        panel_->setStyleSheet(PixelShroomLiquidGlass::panel(dark_) +
                              PixelShroomAppGlass::settingsPanel(dark_) +
                              PixelShroomPhase15Theme::panel(dark_));
        if (status_) {
            status_->setText(result.description);
            status_->setToolTip(QObject::tr("DWM material is supplied by Windows. "
                "Appearance depends on OS support, transparency settings, "
                "power mode, and accessibility preferences."));
        }
        window_->update();
        central_->update();
    }

    QPointer<QMainWindow> window_;
    QPointer<QWidget> central_;
    QPointer<QFrame> panel_;
    QPointer<QLabel> status_;
    WId previousId_ = 0;
    bool dark_ = false;
    Material material_ = Material::Off;
};

} // namespace PixelShroomNativeGlass
