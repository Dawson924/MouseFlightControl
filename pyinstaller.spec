# MouseFlight.spec

# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path


def find_dist_info(pkg_name):
    dist_info_paths = list(Path('.venv/Lib/site-packages').glob(f"{pkg_name}*.dist-info"))
    if dist_info_paths:
        return str(dist_info_paths[0])
    raise FileNotFoundError(f"'{pkg_name}' is not found")

try:
    DIST_INFO = find_dist_info("mouseflight")
except FileNotFoundError as e:
    print(e)
    exit(1)

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[(DIST_INFO, os.path.basename(DIST_INFO))],
    hiddenimports=[],
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    exclude_binaries=False,
    win_no_prefer_redirects=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries + a.zipfiles + a.datas,
    [],
    name='MouseFlight',
    contents_directory='.',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
