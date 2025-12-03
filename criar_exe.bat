@echo off
echo ========================================
echo Criando Executavel do Clicker Script Editor
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    echo Instale o Python primeiro.
    pause
    exit /b 1
)

REM Verificar se PyInstaller está instalado
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller nao encontrado. Instalando...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERRO ao instalar PyInstaller!
        pause
        exit /b 1
    )
)

echo.
echo Executando build...
echo.

REM Executar o script de build
python build_exe.py

if errorlevel 1 (
    echo.
    echo ERRO ao criar executavel!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Concluido!
echo ========================================
echo O executavel esta em: dist\ClickerScriptEditor.exe
echo.
pause

