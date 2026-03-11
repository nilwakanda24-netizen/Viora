"""
Frontend simple amb Python (sense Node.js)
Utilitza FastAPI per servir HTML estàtic
"""

from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import sys
sys.path.append('.')

from models.chest_xray_model import ChestXRayModel
from models.blood_analysis_model import BloodAnalysisModel
from models.multimodal_fusion import MultimodalFusion

app = FastAPI(title="Viora - Frontend + API")

# Inicialitzar models
xray_model = ChestXRayModel()
blood_model = BloodAnalysisModel()
fusion_model = MultimodalFusion()

# HTML del frontend integrat
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Viora - AI Medical Screening</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }
        
        header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .disclaimer {
            background: rgba(255, 243, 205, 0.95);
            padding: 15px 20px;
            border-radius: 10px;
            border-left: 5px solid #ffc107;
            color: #856404;
            margin: 20px auto;
            max-width: 800px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        
        .section {
            margin-bottom: 35px;
        }
        
        .section h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }
        
        .file-upload {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: #f8f9fa;
        }
        
        .file-upload:hover {
            background: #e9ecef;
            border-color: #764ba2;
        }
        
        .file-upload input {
            display: none;
        }
        
        .file-upload-label {
            font-size: 1.2em;
            color: #667eea;
            font-weight: bold;
        }
        
        .blood-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .input-group {
            display: flex;
            flex-direction: column;
        }
        
        .input-group label {
            font-weight: 600;
            color: #495057;
            margin-bottom: 8px;
            font-size: 0.95em;
        }
        
        .input-group input {
            padding: 12px 15px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s;
        }
        
        .input-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn-analyze {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.3em;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 30px;
        }
        
        .btn-analyze:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }
        
        .btn-analyze:disabled {
            background: #95a5a6;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .loading.active {
            display: block;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .results {
            display: none;
            margin-top: 30px;
        }
        
        .results.active {
            display: block;
        }
        
        .risk-badge {
            display: inline-block;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.5em;
            font-weight: bold;
            margin: 20px 0;
        }
        
        .risk-baix {
            background: #d4edda;
            color: #155724;
            border-left: 5px solid #28a745;
        }
        
        .risk-moderat {
            background: #fff3cd;
            color: #856404;
            border-left: 5px solid #ffc107;
        }
        
        .risk-alt {
            background: #f8d7da;
            color: #721c24;
            border-left: 5px solid #dc3545;
        }
        
        .result-item {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
        }
        
        .result-item h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .result-item ul {
            list-style: none;
            padding: 0;
        }
        
        .result-item li {
            padding: 10px 0;
            padding-left: 30px;
            position: relative;
            border-bottom: 1px solid #dee2e6;
        }
        
        .result-item li:last-child {
            border-bottom: none;
        }
        
        .result-item li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
            font-size: 1.2em;
        }
        
        .file-name {
            margin-top: 10px;
            color: #28a745;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏥 Viora</h1>
            <p style="font-size: 1.2em;">AI Medical Screening System</p>
        </header>
        
        <div class="disclaimer">
            ⚠️ <strong>Important:</strong> Aquest és un sistema de suport clínic per a fins educatius. 
            NO substitueix el diagnòstic d'un metge professional. Sempre consulta amb personal mèdic qualificat.
        </div>
        
        <div class="main-card">
            <form id="analysisForm" enctype="multipart/form-data">
                <div class="section">
                    <h2>📸 Radiografia de Tòrax</h2>
                    <div class="file-upload" onclick="document.getElementById('xrayFile').click()">
                        <input type="file" id="xrayFile" name="xray_file" accept="image/*" required>
                        <div class="file-upload-label">
                            📁 Clica per pujar una radiografia
                        </div>
                        <div id="fileName" class="file-name"></div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🩸 Analítica de Sang</h2>
                    <div class="blood-grid">
                        <div class="input-group">
                            <label>Hemoglobina (g/dL)</label>
                            <input type="number" step="0.1" name="hemoglobin" placeholder="12.0 - 16.0">
                        </div>
                        <div class="input-group">
                            <label>Glòbuls blancs (/μL)</label>
                            <input type="number" name="white_blood_cells" placeholder="4000 - 11000">
                        </div>
                        <div class="input-group">
                            <label>Plaquetes (/μL)</label>
                            <input type="number" name="platelets" placeholder="150000 - 400000">
                        </div>
                        <div class="input-group">
                            <label>PCR (mg/L)</label>
                            <input type="number" step="0.1" name="crp" placeholder="0 - 10">
                        </div>
                        <div class="input-group">
                            <label>Colesterol (mg/dL)</label>
                            <input type="number" name="cholesterol" placeholder="< 200">
                        </div>
                        <div class="input-group">
                            <label>Glucosa (mg/dL)</label>
                            <input type="number" name="glucose" placeholder="70 - 100">
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn-analyze" id="analyzeBtn">
                    🔬 Analitzar
                </button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p style="margin-top: 20px; font-size: 1.2em; color: #667eea;">
                    Analitzant dades mèdiques...
                </p>
            </div>
            
            <div class="results" id="results">
                <h2 style="color: #667eea; text-align: center; margin-bottom: 30px;">
                    📋 Resultats de l'Anàlisi
                </h2>
                
                <div style="text-align: center;">
                    <div class="risk-badge" id="riskBadge"></div>
                </div>
                
                <div class="result-item">
                    <h3>🔍 Possible Condició</h3>
                    <p id="condition" style="font-size: 1.3em; font-weight: bold; color: #2c3e50;"></p>
                </div>
                
                <div class="result-item">
                    <h3>📊 Evidències Detectades</h3>
                    <ul id="evidence"></ul>
                </div>
                
                <div class="result-item">
                    <h3>💡 Recomanacions</h3>
                    <ul id="recommendations"></ul>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Mostrar nom del fitxer seleccionat
        document.getElementById('xrayFile').addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                document.getElementById('fileName').textContent = '✓ ' + fileName;
            }
        });
        
        // Gestionar enviament del formulari
        document.getElementById('analysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const xrayFile = document.getElementById('xrayFile').files[0];
            
            if (!xrayFile) {
                alert('Si us plau, puja una radiografia');
                return;
            }
            
            formData.append('xray_file', xrayFile);
            
            // Recollir dades de sang
            const bloodData = {};
            const inputs = document.querySelectorAll('.input-group input');
            inputs.forEach(input => {
                if (input.value) {
                    bloodData[input.name] = parseFloat(input.value);
                }
            });
            
            formData.append('blood_data', JSON.stringify(bloodData));
            
            // Mostrar loading
            document.getElementById('analyzeBtn').disabled = true;
            document.getElementById('loading').classList.add('active');
            document.getElementById('results').classList.remove('active');
            
            try {
                const response = await fetch('/analyze/complete', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    displayResults(data.result);
                } else {
                    alert('Error en l\'anàlisi: ' + data.message);
                }
            } catch (error) {
                alert('Error de connexió: ' + error.message);
            } finally {
                document.getElementById('analyzeBtn').disabled = false;
                document.getElementById('loading').classList.remove('active');
            }
        });
        
        function displayResults(result) {
            // Nivell de risc
            const riskBadge = document.getElementById('riskBadge');
            riskBadge.textContent = 'Nivell de Risc: ' + result.risk_level;
            riskBadge.className = 'risk-badge risk-' + result.risk_level.toLowerCase();
            
            // Condició
            document.getElementById('condition').textContent = result.possible_condition;
            
            // Evidències
            const evidenceList = document.getElementById('evidence');
            evidenceList.innerHTML = '';
            result.evidence.forEach(ev => {
                const li = document.createElement('li');
                li.textContent = ev;
                evidenceList.appendChild(li);
            });
            
            // Recomanacions
            const recList = document.getElementById('recommendations');
            recList.innerHTML = '';
            result.recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                recList.appendChild(li);
            });
            
            // Mostrar resultats
            document.getElementById('results').classList.add('active');
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    """Pàgina principal"""
    return HTML_TEMPLATE

@app.post("/analyze/complete")
async def complete_analysis(
    xray_file: UploadFile = File(...),
    blood_data: str = Form(...)
):
    """Anàlisi completa: radiografia + analítica"""
    try:
        # Processar radiografia
        temp_path = f"temp_{xray_file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await xray_file.read()
            buffer.write(content)
        
        xray_result = xray_model.predict(temp_path)
        
        # Processar analítica
        blood_dict = json.loads(blood_data)
        blood_result = blood_model.predict(blood_dict)
        
        # Fusionar resultats
        final_result = fusion_model.fuse_predictions(xray_result, blood_result)
        
        return {
            "status": "success",
            "result": final_result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("🏥 VIORA - AI Medical Screening System")
    print("="*60)
    print("\n✅ Frontend + API integrats en un sol servidor")
    print("📍 Obre el navegador a: http://localhost:8000")
    print("\n⚠️  Sistema de suport clínic - NO substitueix diagnòstic mèdic\n")
    print("="*60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
