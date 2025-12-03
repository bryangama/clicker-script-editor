# -*- mode: python ; coding: utf-8 -*-
import os
import sys

datas = []
binaries = []

# Imports ocultos básicos
hiddenimports = [
    'FreeSimpleGUI',
    'pyautogui', 
    'schedule', 
    'config', 
    'script_manager', 
    'script_executor', 
    'gui_components', 
    'scheduler', 
    'utils',
    'PIL',
    'PIL._tkinter_finder',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox'
]

# Forçar inclusão do FreeSimpleGUI e seus submódulos
# Isso garante que mesmo que o PyInstaller não detecte automaticamente,
# o módulo será incluído
try:
    import FreeSimpleGUI
    import pkgutil
    fsg_path = os.path.dirname(FreeSimpleGUI.__file__)
    
    # Adicionar todos os submódulos encontrados
    for importer, modname, ispkg in pkgutil.walk_packages([fsg_path], prefix='FreeSimpleGUI.'):
        if modname not in hiddenimports:
            hiddenimports.append(modname)
except Exception as e:
    print(f"Aviso ao processar FreeSimpleGUI: {e}")
    # Se falhar, adicionar pelo menos os módulos principais conhecidos
    hiddenimports.extend([
        'FreeSimpleGUI._utils',
        'FreeSimpleGUI.elements',
        'FreeSimpleGUI.window',
        'FreeSimpleGUI.themes',
        'FreeSimpleGUI.tray'
    ])


a = Analysis(
    ['listagem.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=['.'],  # Incluir hook personalizado do diretório atual
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
    name='ClickerScriptEditor',
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
