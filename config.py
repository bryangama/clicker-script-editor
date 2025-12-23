"""Configurações e constantes do aplicativo."""

import os
import sys

def get_base_directory():
    """Obtém o diretório base para salvar arquivos.
    Se executado como .exe, usa o diretório do executável.
    Caso contrário, usa o diretório atual do script.
    """
    if getattr(sys, 'frozen', False):
        # Executando como executável compilado (.exe)
        # sys.executable aponta para o .exe
        base_dir = os.path.dirname(sys.executable)
    else:
        # Executando como script Python
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    return base_dir

# Diretórios e arquivos
BASE_DIR = get_base_directory()
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
SCRIPTS_LIST_FILE = os.path.join(BASE_DIR, 'scripts_list.json')

# Tema padrão
DEFAULT_THEME = 'DarkGray15'
ALTERNATIVE_THEME = 'SystemDefault1'

# Tipos de ações disponíveis
ACTION_TYPES = {
    'clique': 'Clique Simples',
    'clique_duplo': 'Clique Duplo',
    'digitar': 'Digitar Texto',
    'esperar': 'Esperar (segundos)',
    'tecla': 'Pressionar Tecla',
    'atalho': 'Atalho (ex: ctrl+c)',
    'abrir_app': 'Abrir Aplicativo',
    'redimensionar_janela': 'Redimensionar Janela',
    'capturar_tela': 'Capturar Tela (Print Screen)'
}

# Diretório padrão para screenshots
SCREENSHOTS_DIR = os.path.join(BASE_DIR, 'screenshots')

