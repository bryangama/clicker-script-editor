# Hook para PyInstaller - FreeSimpleGUI
# Este hook garante que o FreeSimpleGUI e todos os seus submódulos sejam incluídos
# Nome do arquivo deve ser: hook-FreeSimpleGUI.py (com F e S maiúsculos)

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import os

hiddenimports = []
datas = []

# Tentar coletar submódulos usando collect_submodules
try:
    hiddenimports = collect_submodules('FreeSimpleGUI')
    print(f"[Hook] Coletados {len(hiddenimports)} submódulos do FreeSimpleGUI")
except Exception as e:
    print(f"[Hook] Erro ao coletar submódulos: {e}")

# Se collect_submodules falhou ou retornou vazio, tentar manualmente
if not hiddenimports:
    try:
        import FreeSimpleGUI
        import pkgutil
        fsg_path = os.path.dirname(FreeSimpleGUI.__file__)
        
        # Adicionar todos os submódulos encontrados
        for importer, modname, ispkg in pkgutil.walk_packages([fsg_path], prefix='FreeSimpleGUI.'):
            hiddenimports.append(modname)
        
        print(f"[Hook] Coletados {len(hiddenimports)} submódulos manualmente")
    except Exception as e:
        print(f"[Hook] Erro ao coletar manualmente: {e}")
        # Fallback: adicionar módulos principais conhecidos
        hiddenimports = [
            'FreeSimpleGUI',
            'FreeSimpleGUI._utils',
            'FreeSimpleGUI.elements',
            'FreeSimpleGUI.window',
            'FreeSimpleGUI.themes',
            'FreeSimpleGUI.tray',
            'FreeSimpleGUI.pysimplegui',
            'FreeSimpleGUI.pysimplegui_flex',
            'FreeSimpleGUI.pysimplegui_flex_qt'
        ]

# Sempre incluir o módulo principal
if 'FreeSimpleGUI' not in hiddenimports:
    hiddenimports.insert(0, 'FreeSimpleGUI')

# Tentar coletar arquivos de dados
try:
    datas = collect_data_files('FreeSimpleGUI', includes=['*.png', '*.gif', '*.jpg', '*.ico', '*.txt', '*.json', '*.ttf', '*.otf'])
    print(f"[Hook] Coletados {len(datas)} arquivos de dados")
except Exception as e:
    print(f"[Hook] Erro ao coletar arquivos de dados: {e}")
    # Tentar incluir o diretório completo como fallback
    try:
        import FreeSimpleGUI
        fsg_path = os.path.dirname(FreeSimpleGUI.__file__)
        if os.path.exists(fsg_path):
            datas.append((fsg_path, 'FreeSimpleGUI'))
            print(f"[Hook] Incluído diretório completo: {fsg_path}")
    except:
        pass

