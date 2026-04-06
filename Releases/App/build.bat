@echo off
chcp 65001 >nul
title Network Shield Builder
color 0A

echo ================================
echo   🛡️ NETWORK SHIELD BUILDER
echo ================================
echo.

REM 1. Verifica Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ERRO: Python nao encontrado!
    echo 📥 1. Baixe: https://www.python.org/downloads/
    echo 📥 2. INSTALE marcando "Add to PATH"
    echo 📥 3. Reinicie CMD
    pause
    exit /b 1
)
echo ✅ Python OK: %python --version%

REM 2. Instala pip (se necessario)
python -m ensurepip --upgrade >nul 2>&1
python -m pip install --upgrade pip >nul 2>&1
echo ✅ Pip atualizado

REM 3. Instala dependencias
echo 📦 Instalando psutil e pyinstaller...
python -m pip install psutil pyinstaller --quiet
echo ✅ Dependencias OK

REM 4. Limpa builds antigos
if exist build rmdir /s /q build >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1
if exist NetworkShield.spec del NetworkShield.spec >nul 2>&1

REM 5. Compila EXE
echo.
echo 🔨 Compilando NetworkShield.exe...
python -m PyInstaller --onefile --windowed --noconsole ^
    --name "NetworkShield" ^
    --distpath dist ^
    --workpath build ^
    NetworkShield-Windows.py

REM 6. Verifica resultado
if exist dist\NetworkShield.exe (
    echo.
    echo ================================
    echo   ✅ SUCESSO TOTAL!
    echo ================================
    echo 📁 EXE criado: dist\NetworkShield.exe
    echo 📏 Tamanho: %~z1 MB
    echo.
    echo 🎮 Testando agora...
    start dist\NetworkShield.exe
    echo.
    echo 👆 APP ABRIU! Esta funcionando!
    echo.
    pause
) else (
    echo.
    echo ❌ FALHA na compilacao!
    echo 📋 Verifique:
    echo    1. network_shield_app.py existe?
    echo    2. Erros acima?
    echo.
    dir
    pause
)