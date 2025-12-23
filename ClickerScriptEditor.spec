# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_all

datas = []
binaries = []

# Imports ocultos básicos
hiddenimports = [
    'pyautogui', 
    'pyscreeze',  # Dependência do pyautogui para capturas de tela
    'pytweening',  # Dependência do pyautogui para animações
    'schedule', 
    'config', 
    'script_manager', 
    'script_executor', 
    'gui_components', 
    'scheduler', 
    'utils',
    'PIL',
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL._imaging',
    'PIL._imagingtk',
    'PIL._webp',
    'PIL._binary',
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'win32gui',  # pywin32 para funcionalidades do Windows
    'win32con',
    'win32api',
    'winreg'
]

# Coletar submódulos do pyautogui
try:
    pyautogui_submodules = collect_submodules('pyautogui')
    hiddenimports.extend(pyautogui_submodules)
    print(f"Submódulos do pyautogui coletados: {len(pyautogui_submodules)}")
except Exception as e:
    print(f"Aviso ao coletar submódulos do pyautogui: {e}")

# Coletar submódulos do pyscreeze
try:
    pyscreeze_submodules = collect_submodules('pyscreeze')
    hiddenimports.extend(pyscreeze_submodules)
    print(f"Submódulos do pyscreeze coletados: {len(pyscreeze_submodules)}")
except Exception as e:
    print(f"Aviso ao coletar submódulos do pyscreeze: {e}")

# Coletar submódulos do Pillow (PIL) - necessário para pyscreeze
try:
    pil_submodules = collect_submodules('PIL')
    hiddenimports.extend(pil_submodules)
    print(f"Submódulos do PIL coletados: {len(pil_submodules)}")
except Exception as e:
    print(f"Aviso ao coletar submódulos do PIL: {e}")

# Coletar dados do pyautogui (pode ter imagens ou outros recursos)
try:
    pyautogui_datas = collect_data_files('pyautogui')
    datas.extend(pyautogui_datas)
except Exception as e:
    print(f"Aviso ao coletar dados do pyautogui: {e}")

# Coletar dados do pyscreeze
try:
    pyscreeze_datas = collect_data_files('pyscreeze')
    datas.extend(pyscreeze_datas)
except Exception as e:
    print(f"Aviso ao coletar dados do pyscreeze: {e}")

# Coletar dados do Pillow
try:
    pil_datas = collect_data_files('PIL')
    datas.extend(pil_datas)
except Exception as e:
    print(f"Aviso ao coletar dados do PIL: {e}")

# Garantir inclusão manual do pyscreeze e suas dependências
try:
    import pyscreeze
    import pkgutil
    pyscreeze_path = os.path.dirname(pyscreeze.__file__)
    
    # Adicionar todos os submódulos encontrados manualmente
    for importer, modname, ispkg in pkgutil.walk_packages([pyscreeze_path], prefix='pyscreeze.'):
        if modname not in hiddenimports:
            hiddenimports.append(modname)
    
    # Incluir o diretório completo do pyscreeze como dados
    if pyscreeze_path and os.path.exists(pyscreeze_path):
        datas.append((pyscreeze_path, 'pyscreeze'))
    
    print(f"pyscreeze encontrado em: {pyscreeze_path}")
except Exception as e:
    print(f"ERRO ao processar pyscreeze manualmente: {e}")
    import traceback
    traceback.print_exc()

# Garantir inclusão manual do Pillow
try:
    import PIL
    import pkgutil
    pil_path = os.path.dirname(PIL.__file__)
    
    # Adicionar todos os submódulos encontrados manualmente
    for importer, modname, ispkg in pkgutil.walk_packages([pil_path], prefix='PIL.'):
        if modname not in hiddenimports:
            hiddenimports.append(modname)
    
    # Incluir o diretório completo do PIL como dados
    if pil_path and os.path.exists(pil_path):
        datas.append((pil_path, 'PIL'))
    
    print(f"PIL encontrado em: {pil_path}")
except Exception as e:
    print(f"ERRO ao processar PIL manualmente: {e}")
    import traceback
    traceback.print_exc()

# Forçar inclusão completa do FreeSimpleGUI e seus submódulos
# Usar collect_all para garantir que tudo seja incluído
try:
    # Coletar todos os submódulos do FreeSimpleGUI
    fsg_submodules = collect_submodules('FreeSimpleGUI')
    hiddenimports.extend(fsg_submodules)
    
    # Coletar todos os arquivos de dados do FreeSimpleGUI
    fsg_datas = collect_data_files('FreeSimpleGUI')
    datas.extend(fsg_datas)
    
    # Também tentar incluir o pacote completo manualmente
    import FreeSimpleGUI
    import pkgutil
    fsg_path = os.path.dirname(FreeSimpleGUI.__file__)
    
    # Adicionar todos os submódulos encontrados manualmente também
    for importer, modname, ispkg in pkgutil.walk_packages([fsg_path], prefix='FreeSimpleGUI.'):
        if modname not in hiddenimports:
            hiddenimports.append(modname)
    
    # Incluir o diretório completo do FreeSimpleGUI como dados (fallback)
    # Isso garante que todos os arquivos sejam incluídos
    if fsg_path and os.path.exists(fsg_path):
        # Incluir o diretório completo do FreeSimpleGUI
        datas.append((fsg_path, 'FreeSimpleGUI'))
        # Também incluir o diretório pai para garantir que o pacote seja encontrado
        parent_path = os.path.dirname(fsg_path)
        if parent_path and os.path.exists(parent_path):
            # Verificar se já não está incluído
            if not any(d[0] == parent_path for d in datas):
                datas.append((parent_path, '.'))
    
    print(f"FreeSimpleGUI encontrado em: {fsg_path}")
    print(f"Submódulos coletados: {len(fsg_submodules)}")
    print(f"Arquivos de dados coletados: {len(fsg_datas)}")
    print(f"Total de hiddenimports: {len(hiddenimports)}")
    
except Exception as e:
    print(f"ERRO ao processar FreeSimpleGUI: {e}")
    import traceback
    traceback.print_exc()
    # Se falhar, adicionar pelo menos os módulos principais conhecidos
    hiddenimports.extend([
        'FreeSimpleGUI',
        'FreeSimpleGUI._utils',
        'FreeSimpleGUI.elements',
        'FreeSimpleGUI.window',
        'FreeSimpleGUI.themes',
        'FreeSimpleGUI.tray',
        'FreeSimpleGUI.pysimplegui',
        'FreeSimpleGUI.pysimplegui_flex',
        'FreeSimpleGUI.pysimplegui_flex_qt'
    ])

# Garantir que o módulo principal está na lista
if 'FreeSimpleGUI' not in hiddenimports:
    hiddenimports.insert(0, 'FreeSimpleGUI')


# Adicionar o diretório do site-packages ao pathex para garantir que os módulos sejam encontrados
pathex = []
try:
    import site
    for site_packages in site.getsitepackages():
        if os.path.exists(site_packages):
            pathex.append(site_packages)
except:
    pass

a = Analysis(
    ['listagem.py'],
    pathex=pathex,
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
