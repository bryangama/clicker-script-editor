"""Script para criar executável do aplicativo usando PyInstaller."""

import subprocess
import sys
import os

def build_executable():
    """Cria o executável usando PyInstaller."""
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
    except ImportError:
        print("ERRO: PyInstaller não está instalado!")
        print("Instale com: pip install pyinstaller")
        sys.exit(1)
    
    # Caminho do arquivo principal
    main_script = 'listagem.py'
    
    # Verificar se o arquivo existe
    if not os.path.exists(main_script):
        print(f"ERRO: Arquivo {main_script} não encontrado!")
        sys.exit(1)
    
    # Usar o arquivo .spec que já tem todas as configurações necessárias
    # incluindo o hook personalizado para FreeSimpleGUI
    spec_file = 'ClickerScriptEditor.spec'
    
    if not os.path.exists(spec_file):
        print(f"ERRO: Arquivo {spec_file} não encontrado!")
        sys.exit(1)
    
    # Comando PyInstaller usando o arquivo .spec
    cmd = [
        'pyinstaller',
        '--clean',
        spec_file
    ]
    
    print("="*60)
    print("Criando executável do Clicker Script Editor...")
    print("="*60)
    print(f"Arquivo principal: {main_script}")
    print(f"Comando: {' '.join(cmd)}")
    print("="*60)
    print()
    
    # Executar PyInstaller
    try:
        result = subprocess.run(cmd, check=True)
        
        print()
        print("="*60)
        print("✓ Executável criado com sucesso!")
        print("="*60)
        print(f"Arquivo está em: dist/ClickerScriptEditor.exe")
        print("="*60)
        
    except subprocess.CalledProcessError as e:
        print()
        print("="*60)
        print("ERRO ao criar executável!")
        print("="*60)
        print(f"Código de erro: {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print()
        print("="*60)
        print("ERRO: PyInstaller não encontrado!")
        print("="*60)
        print("Certifique-se de que PyInstaller está instalado:")
        print("  pip install pyinstaller")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()

