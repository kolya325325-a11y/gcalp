# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path


project_dir = Path(SPECPATH)
assets_dir = project_dir / "assets"
icon_file = assets_dir / ("calculator.ico" if sys.platform == "win32" else "calculator.icns")

a = Analysis(
    [str(project_dir / "calculator.py")],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[(str(assets_dir / "calculator.png"), "assets")],
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
    a.binaries,
    a.datas,
    [],
    name="Calculator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_file),
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="Calculator.app",
        icon=str(icon_file),
        bundle_identifier="com.gcalp.calculator",
        info_plist={"NSHighResolutionCapable": True},
    )
