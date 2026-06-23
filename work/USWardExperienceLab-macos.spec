# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

spec_dir = Path(SPECPATH)

a = Analysis(
    ['us_ward_simulator.py'],
    pathex=[str(spec_dir)],
    binaries=[],
    datas=[(str(spec_dir / 'assets'), 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='USWardExperienceLab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(spec_dir / 'assets' / 'us-ward-icon.icns'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='USWardExperienceLab',
)

app = BUNDLE(
    coll,
    name='USWardExperienceLab.app',
    icon=str(spec_dir / 'assets' / 'us-ward-icon.icns'),
    bundle_identifier='com.darkha123.uswardexperiencelab',
    info_plist={
        'CFBundleName': 'U.S. Ward Experience Lab',
        'CFBundleDisplayName': 'U.S. Ward Experience Lab',
        'CFBundleShortVersionString': '0.1.0-beta',
        'CFBundleVersion': '0.1.0',
        'NSHighResolutionCapable': 'True',
        'LSApplicationCategoryType': 'public.app-category.education',
    },
)
