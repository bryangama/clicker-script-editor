"""Script para criar executável do aplicativo usando PyInstaller."""

import subprocess
import sys
import os

def install_dependencies():
    """Instala as dependências do requirements.txt se necessário."""
    requirements_file = 'requirements.txt'
    
    if not os.path.exists(requirements_file):
        print(f"Aviso: Arquivo {requirements_file} não encontrado. Pulando instalação de dependências.")
        return True
    
    print("Verificando e instalando dependências...")
    print("="*60)
    try:
        # Ler requirements.txt e instalar cada dependência
        with open(requirements_file, 'r', encoding='utf-8') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        
        for req in requirements:
            # Verificar se o módulo já está instalado
            module_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip()
            try:
                __import__(module_name)
                print(f"✓ {module_name} já está instalado")
            except ImportError:
                print(f"Instalando {req}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", req], 
                                    stdout=sys.stdout, stderr=sys.stderr)
                print(f"✓ {req} instalado")
        
        print("="*60)
        print("✓ Todas as dependências verificadas/instaladas!")
        print("="*60)
        print()
        return True
    except subprocess.CalledProcessError as e:
        print("="*60)
        print(f"ERRO: Falha ao instalar dependências!")
        print("="*60)
        print(f"Código de erro: {e.returncode}")
        print("Tente instalar manualmente com: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"Aviso: Erro ao verificar dependências: {e}")
        return True  # Continuar mesmo se houver erro

def install_pyinstaller():
    """Instala o PyInstaller se não estiver disponível."""
    print("PyInstaller não encontrado. Instalando...")
    print("="*60)
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                            stdout=sys.stdout, stderr=sys.stderr)
        print("="*60)
        print("✓ PyInstaller instalado com sucesso!")
        print("="*60)
        print()
        return True
    except subprocess.CalledProcessError as e:
        print("="*60)
        print("ERRO: Falha ao instalar PyInstaller!")
        print("="*60)
        print(f"Código de erro: {e.returncode}")
        print("Tente instalar manualmente com: pip install pyinstaller")
        return False

def build_executable():
    """Cria o executável usando PyInstaller."""
    
    # Primeiro, verificar e instalar dependências
    print("="*60)
    print("Verificando dependências...")
    print("="*60)
    if not install_dependencies():
        print("Aviso: Algumas dependências podem não estar instaladas.")
        print("Continuando mesmo assim...")
        print()
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
    except ImportError:
        # Tentar instalar automaticamente
        if not install_pyinstaller():
            sys.exit(1)
        # Tentar importar novamente após instalação
        try:
            import PyInstaller
        except ImportError:
            print("ERRO: PyInstaller ainda não está disponível após instalação!")
            print("Tente instalar manualmente com: pip install pyinstaller")
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
    
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
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
        print("ERRO: Python não encontrado!")
        print("="*60)
        print("Certifique-se de que Python está instalado e no PATH.")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()

