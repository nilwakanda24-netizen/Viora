@echo off
REM Script d'inici de Viora Medical AI Platform per Windows

echo ======================================================================
echo 🏥 VIORA MEDICAL AI PLATFORM - Inici
echo ======================================================================
echo.

REM Comprovar si Python està instal·lat
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no està instal·lat
    echo Instal·la Python 3.11 o superior: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detectat

REM Comprovar si l'entorn virtual existeix
if not exist "venv" (
    echo 📦 Creant entorn virtual...
    python -m venv venv
)

REM Activar entorn virtual
echo 🔧 Activant entorn virtual...
call venv\Scripts\activate.bat

REM Instal·lar/actualitzar dependències
echo 📥 Instal·lant dependències...
python -m pip install -q --upgrade pip
pip install -q -r requirements.txt

REM Comprovar Tesseract
where tesseract >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Tesseract OCR no està instal·lat
    echo Per OCR de PDFs/imatges, instal·la Tesseract:
    echo   Windows: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo L'aplicació funcionarà però sense OCR automàtic.
    echo.
)

echo.
echo ======================================================================
echo 🚀 Iniciant Viora...
echo ======================================================================
echo.

REM Executar aplicació
python viora_ultimate.py

pause
