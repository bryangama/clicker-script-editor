"""Gerenciamento de arquivos de scripts."""

import json
import os
from config import SCRIPTS_DIR, SCRIPTS_LIST_FILE


def ensure_scripts_dir():
    """Garante que o diretório de scripts existe."""
    if not os.path.exists(SCRIPTS_DIR):
        os.makedirs(SCRIPTS_DIR)


def load_scripts_list():
    """Carrega a lista de scripts salvos."""
    ensure_scripts_dir()
    if os.path.exists(SCRIPTS_LIST_FILE):
        try:
            with open(SCRIPTS_LIST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_scripts_list(scripts_list):
    """Salva a lista de scripts."""
    ensure_scripts_dir()
    with open(SCRIPTS_LIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(scripts_list, f, indent=2, ensure_ascii=False)


def load_script(script_name):
    """Carrega um script específico."""
    script_path = os.path.join(SCRIPTS_DIR, f'{script_name}.json')
    if os.path.exists(script_path):
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None


def save_script(script_data):
    """Salva um script."""
    ensure_scripts_dir()
    script_name = script_data.get('name', 'script_sem_nome')
    script_path = os.path.join(SCRIPTS_DIR, f'{script_name}.json')
    with open(script_path, 'w', encoding='utf-8') as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)

