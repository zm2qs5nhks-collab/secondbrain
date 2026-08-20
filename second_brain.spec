# -*- mode: python ; coding: utf-8 -*-
import os, sys, glob
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

src_dir = os.getcwd()
datas = []

# Add all project source files
for root, dirs, files in os.walk(src_dir):
    rel = os.path.relpath(root, src_dir)
    # Skip unwanted dirs
    if any(x in rel.split(os.sep) for x in ['venv', '__pycache__', '.git', 'build', 'data', 'competition']):
        continue
    # Skip individual unwanted files
    for f in files:
        if f.endswith('.pyc') or f == 'graph_data.json':
            continue
        full = os.path.join(root, f)
        datas.append((full, rel))

# Copy metadata for streamlit
datas += copy_metadata('streamlit')

# Collect all data from key packages
for pkg in ['streamlit', 'openai', 'supabase', 'networkx', 'numpy', 'pandas']:
    datas += collect_data_files(pkg)

hiddenimports = [
    'nest_asyncio', 'scipy',
    'streamlit.runtime.scriptrunner.magic_funcs',
    'streamlit.web.server.routes',
    'streamlit.runtime.caching',
    'streamlit.runtime.state.session_state',
]

a = Analysis(
    ['launcher.py'],
    pathex=[src_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SecondBrain',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SecondBrain',
)
