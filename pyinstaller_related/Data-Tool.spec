# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

datas = [('C:/Users/FlorianBERGERE/miniconda3/envs/test_env/Lib/site-packages/altair/vegalite/v5/schema/vega-lite-schema.json', './altair/vegalite/v5/schema/'), ('C:/Users/FlorianBERGERE/miniconda3/envs/test_env/Lib/site-packages/streamlit', './streamlit'), ('C:/Users/FlorianBERGERE/miniconda3/envs/test_env/Lib/site-packages/reportlab', './reportlab'), ('CSV_files/*.csv', 'CSV_files'), ('.streamlit/*.toml', '.streamlit'), ('pages/*.py', 'pages'), ('utils/*.py', 'utils'), ('lib/*.py', 'lib'), ('layouts/*.py', 'layouts'), ('General.py', '.')]
datas += copy_metadata('streamlit')


a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['pandas', 'numpy', 'plotly', 'scipy'],
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
    name='Data-Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon\\tool.ico'],
)
