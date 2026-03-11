#!/bin/bash

# Script d'inici de Viora Medical AI Platform

echo "======================================================================"
echo "🏥 VIORA MEDICAL AI PLATFORM - Inici"
echo "======================================================================"
echo ""

# Comprovar si Python està instal·lat
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no està instal·lat"
    echo "Instal·la Python 3.11 o superior: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python $(python3 --version) detectat"

# Comprovar si l'entorn virtual existeix
if [ ! -d "venv" ]; then
    echo "📦 Creant entorn virtual..."
    python3 -m venv venv
fi

# Activar entorn virtual
echo "🔧 Activant entorn virtual..."
source venv/bin/activate

# Instal·lar/actualitzar dependències
echo "📥 Instal·lant dependències..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Comprovar Tesseract
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR no està instal·lat"
    echo "Per OCR de PDFs/imatges, instal·la Tesseract:"
    echo "  - Ubuntu/Debian: sudo apt install tesseract-ocr tesseract-ocr-spa tesseract-ocr-cat"
    echo "  - macOS: brew install tesseract tesseract-lang"
    echo "  - Windows: https://github.com/UB-Mannheim/tesseract/wiki"
    echo ""
    echo "L'aplicació funcionarà però sense OCR automàtic."
    echo ""
fi

echo ""
echo "======================================================================"
echo "🚀 Iniciant Viora..."
echo "======================================================================"
echo ""

# Executar aplicació
python viora_ultimate.py
