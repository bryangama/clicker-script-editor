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

REM O build_exe.py agora instala o PyInstaller automaticamente se necessário

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

