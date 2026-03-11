FROM python:3.11-slim

# Instal·lar Tesseract OCR i dependències del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-cat \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Crear directori de treball
WORKDIR /app

# Copiar requirements i instal·lar dependències Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar tot el codi
COPY . .

# Crear directori per la base de dades
RUN mkdir -p /app/data

# Exposar port
EXPOSE 8000

# Variables d'entorn
ENV PYTHONUNBUFFERED=1

# Executar aplicació
CMD ["python", "viora_ultimate.py"]
