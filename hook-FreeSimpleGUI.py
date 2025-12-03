# Hook para PyInstaller - FreeSimpleGUI
# Este hook garante que o FreeSimpleGUI e todos os seus submódulos sejam incluídos

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

hiddenimports = []
datas = []

# Tentar coletar submódulos usando collect_submodules
try:
    hiddenimports = collect_submodules('FreeSimpleGUI')
except:
    pass

# Se collect_submodules falhou, tentar manualmente
if not hiddenimports:
    try:
        import FreeSimpleGUI
        import pkgutil
        fsg_path = os.path.dirname(FreeSimpleGUI.__file__)
        
        # Adicionar todos os submódulos encontrados
        for importer, modname, ispkg in pkgutil.walk_packages([fsg_path], prefix='FreeSimpleGUI.'):
            hiddenimports.append(modname)
    except:
        # Fallback: adicionar módulos principais conhecidos
        hiddenimports = [
            'FreeSimpleGUI',
            'FreeSimpleGUI._utils',
            'FreeSimpleGUI.elements',
            'FreeSimpleGUI.window',
            'FreeSimpleGUI.themes',
            'FreeSimpleGUI.tray'
        ]

# Sempre incluir o módulo principal
if 'FreeSimpleGUI' not in hiddenimports:
    hiddenimports.insert(0, 'FreeSimpleGUI')

# Tentar coletar arquivos de dados
try:
    datas = collect_data_files('FreeSimpleGUI', includes=['*.png', '*.gif', '*.jpg', '*.ico', '*.txt', '*.json'])
except:
    pass

