# Instruções para Criar Executável

Este guia explica como criar um executável (.exe) a partir do projeto Clicker Script Editor.

## Método 1: Usando PyInstaller (Recomendado)

### Passo 1: Instalar PyInstaller

```powershell
pip install pyinstaller
```

### Passo 2: Criar o Executável

#### Opção A: Usando o script de build (Mais fácil)

```powershell
python build_exe.py
```

#### Opção B: Usando o arquivo .spec

```powershell
pyinstaller ClickerScriptEditor.spec
```

#### Opção C: Comando direto (Mais controle)

```powershell
pyinstaller --name=ClickerScriptEditor --onefile --windowed --hidden-import=FreeSimpleGUI --hidden-import=pyautogui --hidden-import=schedule --collect-all=FreeSimpleGUI listagem.py
```

### Passo 3: Localizar o Executável

Após a compilação, o executável estará em:
```
dist/ClickerScriptEditor.exe
```

## Método 2: Usando cx_Freeze (Alternativa)

### Instalação

```powershell
pip install cx_Freeze
```

### Criar setup.py

Crie um arquivo `setup.py` com:

```python
from cx_Freeze import setup, Executable

setup(
    name="ClickerScriptEditor",
    version="1.0",
    description="Editor de Scripts de Cliques",
    executables=[Executable("listagem.py", base="Win32GUI")]
)
```

### Compilar

```powershell
python setup.py build
```

## Estrutura do Executável

O executável criado será um arquivo único (.exe) que contém:
- Todo o código Python compilado
- Todas as dependências necessárias
- Os módulos do projeto (config, script_manager, etc.)

## Notas Importantes

1. **Tamanho do Executável**: O arquivo .exe pode ter entre 20-50 MB devido às dependências incluídas.

2. **Antivírus**: Alguns antivírus podem marcar executáveis criados com PyInstaller como suspeitos. Isso é um falso positivo comum.

3. **Primeira Execução**: A primeira execução pode ser mais lenta devido à extração temporária dos arquivos.

4. **Dependências Opcionais**: Se você usar `pywin32`, certifique-se de que está instalado antes de criar o executável.

5. **Ícone Personalizado**: Para adicionar um ícone personalizado:
   - Crie ou baixe um arquivo `.ico`
   - Adicione `--icon=seu_icone.ico` ao comando PyInstaller
   - Ou edite o arquivo `.spec` e adicione `icon='seu_icone.ico'`

## Distribuição

Para distribuir o aplicativo:

1. Copie o arquivo `ClickerScriptEditor.exe` da pasta `dist/`
2. O usuário pode executar diretamente sem precisar instalar Python ou dependências
3. Opcionalmente, crie um instalador usando ferramentas como Inno Setup ou NSIS

## Solução de Problemas

### Erro: "No module named 'FreeSimpleGUI'"

**Problema**: Ao executar o .exe em outro computador, aparece o erro "No module named 'FreeSimpleGUI'".

**Causa**: O PyInstaller não está incluindo corretamente o FreeSimpleGUI e suas dependências no executável.

**Solução**: Use o arquivo `.spec` atualizado que já inclui todas as dependências necessárias:

```powershell
# Limpar builds anteriores (PowerShell)
Remove-Item -Path build,dist -Recurse -Force -ErrorAction SilentlyContinue

# Reconstruir usando o arquivo .spec (RECOMENDADO)
pyinstaller ClickerScriptEditor.spec --clean

# OU usar o script de build atualizado
python build_exe.py
```

**Nota:** Se estiver usando CMD (não PowerShell), use:
```cmd
rmdir /s /q build dist
pyinstaller ClickerScriptEditor.spec --clean
```

O arquivo `.spec` foi configurado para incluir:
- FreeSimpleGUI e todos os seus submódulos
- PIL/Pillow (necessário para imagens)
- tkinter (necessário para a GUI)
- Todas as dependências do projeto

**Importante**: Sempre use o arquivo `.spec` ou o script `build_exe.py` atualizado, não use comandos PyInstaller simples que podem não incluir todas as dependências.

### Erro: "ModuleNotFoundError" (outros módulos)

Se algum módulo não for encontrado, adicione-o como `--hidden-import`:

```powershell
pyinstaller --hidden-import=nome_do_modulo listagem.py
```

### Executável muito grande

Use `--exclude-module` para excluir módulos desnecessários:

```powershell
pyinstaller --exclude-module=matplotlib --exclude-module=numpy listagem.py
```

### Executável não funciona em outro PC

Certifique-se de incluir todos os arquivos necessários usando `--add-data`:

```powershell
pyinstaller --add-data="config.py;." --add-data="scripts;scripts" listagem.py
```

