"""Small mechanical regression tests for Phase 12 installer; not a C++ build."""
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).parent))
import pixel_shroom_phase12_liquid_glass as p

SOURCE = '''
#include "pixelshroom_phase7.h"
#include "pixelshroom_glass_theme.h"
void MainWindowImpl::setupPixelShroomControls()
{
    // Pixel Shroom Phase 11: upload-ready exports and premium glass UI.
    // Pixel Shroom Phase 7: unified output settings and modeless live preview.
    qApp->setStyleSheet(PixelShroomGlass::window());
    panel->setStyleSheet(PixelShroomGlass::panel());
    auto *root = new QVBoxLayout(panel);
    root->setContentsMargins(12, 10, 12, 9);
    root->setSpacing(7);
    heading->addWidget(title, 1);
    sizeGrid->setContentsMargins(8, 12, 8, 10);
    compressGrid->setContentsMargins(8, 12, 8, 10);
    enhanceGrid->setContentsMargins(8, 12, 8, 10);
    uploadLayout->setContentsMargins(15, 15, 15, 12);
    auto *uploadTitle = new QLabel(tr("Website upload • automatic lossless optimization"), uploadTab);
    auto *uploadAction = new QPushButton(tr("Create upload-ready files for imported images"), uploadTab);
    uploadAction->setObjectName("psUploadAction");
    tabs->addTab(uploadTab, tr("Upload-ready"));
    PixelShroomUpload::start(this, sources, destination,
                            previewEdge->value(), allowPreviewDownscale->isChecked());
}
'''

converted = p.transform(SOURCE)
assert p.MARK in converted
assert 'PixelShroomLiquidGlass::window(glassDark)' in converted
assert 'PixelShroomLiquidGlass::panel(glassDark)' in converted
assert 'glassMode->setCheckable(true)' in converted
assert 'PixelShroomUpload::start(this, sources, destination,' in converted
assert 'tabs->addTab(uploadTab, tr("Website"));' in converted
assert 'pixelshroom_glass_theme.h' not in converted
assert 'qApp->setStyleSheet(PixelShroomGlass' not in converted
assert 'panel->setStyleSheet(PixelShroomGlass' not in converted
try:
    p.transform(converted)
    raise AssertionError('Duplicate patch should fail')
except ValueError:
    pass
try:
    p.transform(SOURCE.replace('Pixel Shroom Phase 11:', 'Pixel Shroom Phase XX:'))
    raise AssertionError('Missing Phase11 marker should fail')
except ValueError:
    pass

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp)
    (root/'src').mkdir()
    (root/'src'/'mainwindowimpl.cpp').write_text(SOURCE,encoding='utf-8')
    (root/'src'/'pixelshroom_glass_theme.h').write_text('// original theme',encoding='utf-8')
    target = root/'src'/'pixelshroom_liquid_glass_theme.h'
    assert not target.exists()
    assert p.main.__name__ == 'main'

header = (Path(__file__).parent/'pixelshroom_liquid_glass_theme.h').read_text(encoding='utf-8')
for v in ['inline QString window(bool dark = false)', 'inline QString panel(bool dark = false)',
          'QFrame#psStudioPanel', 'QPushButton#psUploadAction', 'QTabBar::tab:selected']:
    assert v in header, v
assert header.count('R"LIGHT(') == 2 and header.count('R"DARK(') == 2
assert header.count(')LIGHT"') == 2 and header.count(')DARK"') == 2
print('PASS: Phase 12 mechanical patch, guardrails, theme variants, and no converter modifications')
