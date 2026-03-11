# ⚡ Quick Start - Viora (5 minuts)

Per si vols començar ràpidament sense entrenar el model complet.

## 1. Instal·lació Ràpida

```bash
# Crear entorn virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Instal·lar dependencies
pip install fastapi uvicorn pydantic python-multipart numpy pillow
```

## 2. Crear Dades de Prova

```bash
# Crear directoris
mkdir -p data/examples
mkdir -p models/saved
```

## 3. Mode Demo (sense model entrenat)

Crea `demo_mode.py`:

```python
from api.main import app
import uvicorn

# Modificar per mode demo
# Els models retornaran prediccions simulades

if __name__ == "__main__":
    print("🚀 Iniciant Viora en mode DEMO")
    print("📍 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```bash
python demo_mode.py
```

## 4. Provar amb cURL

```bash
# Test analítica de sang
curl -X POST "http://localhost:8000/analyze/blood" \
  -H "Content-Type: application/json" \
  -d '{
    "hemoglobin": 11.2,
    "white_blood_cells": 14000,
    "crp": 15
  }'
```

## 5. Frontend Integrat (sense Node.js)

Ja tens `frontend_simple.py` creat! Només executa:

```bash
python frontend_simple.py
```

Obre http://localhost:8000 al navegador.

## 6. Frontend Mínim Alternatiu (HTML estàtic)

Si vols un fitxer HTML independent, crea `index.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Viora Demo</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        input { margin: 10px 0; padding: 10px; width: 100%; }
        button { padding: 15px 30px; background: #3498db; color: white; border: none; cursor: pointer; }
        .result { margin-top: 20px; padding: 20px; background: #f0f0f0; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>🏥 Viora - Demo Ràpid</h1>
    
    <h3>Analítica de Sang</h3>
    <input type="number" id="hemoglobin" placeholder="Hemoglobina (g/dL)">
    <input type="number" id="wbc" placeholder="Glòbuls blancs (/μL)">
    <input type="number" id="crp" placeholder="PCR (mg/L)">
    
    <button onclick="analyze()">Analitzar</button>
    
    <div id="result" class="result" style="display:none;"></div>
    
    <script>
        async function analyze() {
            const data = {
                hemoglobin: parseFloat(document.getElementById('hemoglobin').value),
                white_blood_cells: parseFloat(document.getElementById('wbc').value),
                crp: parseFloat(document.getElementById('crp').value)
            };
            
            const response = await fetch('http://localhost:8000/analyze/blood', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            document.getElementById('result').style.display = 'block';
            document.getElementById('result').innerHTML = `
                <h3>Resultats</h3>
                <p><strong>Condició:</strong> ${result.result.condition}</p>
                <p><strong>Confiança:</strong> ${(result.result.confidence * 100).toFixed(1)}%</p>
            `;
        }
    </script>
</body>
</html>
```

Obre `index.html` al navegador.

---

Ara tens Viora funcionant en mode demo! Per la versió completa amb models entrenats, segueix la GUIA_INSTALACIO.md.
