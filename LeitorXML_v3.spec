# -*- mode: python ; coding: utf-8 -*-
import glob
import os

datas = []
# Include all pngs
for file in glob.glob("images/*.png"):
    datas.append((file, "images"))

# Include all jsons
for file in glob.glob("*.json"):
    datas.append((file, "."))

# Include icon
if os.path.exists('images/icone.ico'):
    datas.append(('images/icone.ico', 'images'))

a = Analysis(
    ['leitor_xml.py'],
    pathex=[],
    binaries=[],
    datas=datas,
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
    name='LeitorXML_v3',
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
    icon=['images/icone.ico'],
)
