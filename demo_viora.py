"""
Viora - Professional Medical AI Platform
Estil Apple amb funcionalitats multimodals
Executa: python demo_viora.py
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import random
import base64
from datetime import datetime
import io

app = FastAPI(title="Viora - Medical AI Platform")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models de dades
class BloodAnalysis(BaseModel):
    hemoglobin: Optional[float] = None
    white_blood_cells: Optional[float] = None
    platelets: Optional[float] = None
    crp: Optional[float] = None
    cholesterol: Optional[float] = None
    glucose: Optional[float] = None
    ferritin: Optional[float] = None
    alt: Optional[float] = None
    ast: Optional[float] = None
    creatinine: Optional[float] = None

# HTML del frontend amb estil Apple
HTML = """
<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Viora - Medical AI Platform</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container { max-width: 1200px; margin: 0 auto; }
        
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
        }
        
        .main-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .section { margin-bottom: 35px; }
        
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
        
        .file-upload input { display: none; }
        
        .blood-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        
        .input-group {
            display: flex;
            flex-direction: column;
        }
        
        .input-group label {
            font-weight: 600;
            color: #495057;
            margin-bottom: 8px;
        }
        
        .input-group input {
            padding: 12px;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            font-size: 1em;
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
            margin-top: 30px;
        }
        
        .btn-analyze:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .loading.active { display: block; }
        
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
        
        .results.active { display: block; }
        
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
        
        .result-item li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }
        
        .demo-badge {
            background: #17a2b8;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            display: inline-block;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏥 Viora <span class="demo-badge">DEMO</span></h1>
            <p style="font-size: 1.2em;">AI Medical Screening System</p>
        </header>
        
        <div class="disclaimer">
            ⚠️ <strong>Important:</strong> Aquest és un sistema DEMO amb prediccions simulades. 
            NO utilitzar per diagnòstics reals. Sempre consulta amb personal mèdic qualificat.
        </div>
        
        <div class="main-card">
            <form id="analysisForm">
                <div class="section">
                    <h2>📸 Radiografia de Tòrax</h2>
                    <div class="file-upload" onclick="document.getElementById('xrayFile').click()">
                        <input type="file" id="xrayFile" accept="image/*">
                        <div style="font-size: 1.2em; color: #667eea; font-weight: bold;">
                            📁 Clica per pujar una radiografia
                        </div>
                        <div id="fileName" style="margin-top: 10px; color: #28a745; font-weight: bold;"></div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🩸 Analítica de Sang</h2>
                    <div class="blood-grid">
                        <div class="input-group">
                            <label>Hemoglobina (g/dL)</label>
                            <input type="number" step="0.1" id="hemoglobin" placeholder="12.0 - 16.0">
                        </div>
                        <div class="input-group">
                            <label>Glòbuls blancs (/μL)</label>
                            <input type="number" id="wbc" placeholder="4000 - 11000">
                        </div>
                        <div class="input-group">
                            <label>Plaquetes (/μL)</label>
                            <input type="number" id="platelets" placeholder="150000 - 400000">
                        </div>
                        <div class="input-group">
                            <label>PCR (mg/L)</label>
                            <input type="number" step="0.1" id="crp" placeholder="0 - 10">
                        </div>
                        <div class="input-group">
                            <label>Colesterol (mg/dL)</label>
                            <input type="number" id="cholesterol" placeholder="< 200">
                        </div>
                        <div class="input-group">
                            <label>Glucosa (mg/dL)</label>
                            <input type="number" id="glucose" placeholder="70 - 100">
                        </div>
                    </div>
                </div>
                
                <button type="submit" class="btn-analyze">
                    🔬 Analitzar (Demo)
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
                    📋 Resultats de l'Anàlisi (Simulats)
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
        document.getElementById('xrayFile').addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                document.getElementById('fileName').textContent = '✓ ' + fileName;
            }
        });
        
        document.getElementById('analysisForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const xrayFile = document.getElementById('xrayFile').files[0];
            if (!xrayFile) {
                alert('Si us plau, puja una radiografia');
                return;
            }
            
            // Recollir dades
            const bloodData = {
                hemoglobin: parseFloat(document.getElementById('hemoglobin').value) || 0,
                white_blood_cells: parseFloat(document.getElementById('wbc').value) || 0,
                platelets: parseFloat(document.getElementById('platelets').value) || 0,
                crp: parseFloat(document.getElementById('crp').value) || 0,
                cholesterol: parseFloat(document.getElementById('cholesterol').value) || 0,
                glucose: parseFloat(document.getElementById('glucose').value) || 0
            };
            
            // Mostrar loading
            document.getElementById('loading').classList.add('active');
            document.getElementById('results').classList.remove('active');
            
            // Simular anàlisi
            setTimeout(() => {
                const result = generateDemoResult(bloodData);
                displayResults(result);
                document.getElementById('loading').classList.remove('active');
            }, 2000);
        });
        
        function generateDemoResult(bloodData) {
            // Lògica simple per generar resultats demo
            let riskLevel = 'Baix';
            let condition = 'Normal';
            let evidence = ['Radiografia processada correctament'];
            let recommendations = ['Mantenir hàbits saludables', 'Revisió anual recomanada'];
            
            if (bloodData.hemoglobin > 0 && bloodData.hemoglobin < 12) {
                condition = 'Possible Anèmia';
                riskLevel = 'Moderat';
                evidence.push('Hemoglobina baixa detectada');
                recommendations = ['Consultar metge de família', 'Possible suplementació de ferro'];
            }
            
            if (bloodData.white_blood_cells > 11000) {
                condition = 'Possible Infecció';
                riskLevel = 'Moderat';
                evidence.push('Glòbuls blancs elevats');
                recommendations = ['Consulta mèdica recomanada', 'Possible analítica de seguiment'];
            }
            
            if (bloodData.crp > 10) {
                riskLevel = 'Alt';
                evidence.push('PCR elevada - possible inflamació');
                recommendations = ['Consulta mèdica urgent', 'Proves addicionals recomanades'];
            }
            
            if (bloodData.glucose > 126) {
                condition = 'Possible Diabetis';
                evidence.push('Glucosa elevada');
                recommendations.push('Control de glucosa recomanat');
            }
            
            return {
                risk_level: riskLevel,
                possible_condition: condition,
                evidence: evidence,
                recommendations: recommendations
            };
        }
        
        function displayResults(result) {
            const riskBadge = document.getElementById('riskBadge');
            riskBadge.textContent = 'Nivell de Risc: ' + result.risk_level;
            riskBadge.className = 'risk-badge risk-' + result.risk_level.toLowerCase();
            
            document.getElementById('condition').textContent = result.possible_condition;
            
            const evidenceList = document.getElementById('evidence');
            evidenceList.innerHTML = '';
            result.evidence.forEach(ev => {
                const li = document.createElement('li');
                li.textContent = ev;
                evidenceList.appendChild(li);
            });
            
            const recList = document.getElementById('recommendations');
            recList.innerHTML = '';
            result.recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                recList.appendChild(li);
            });
            
            document.getElementById('results').classList.add('active');
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML

@app.get("/health")
async def health():
    return {"status": "ok", "mode": "demo"}

if __name__ == "__main__":
    try:
        import uvicorn
        print("="*60)
        print("🏥 VIORA - Demo Mode")
        print("="*60)
        print("\n✅ Servidor iniciat correctament")
        print("📍 Obre el navegador a: http://localhost:8000")
        print("\n⚠️  Mode DEMO - Prediccions simulades")
        print("💡 Per mode complet, entrena els models primer\n")
        print("="*60)
        print("\nPrem Ctrl+C per aturar el servidor\n")
        
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except ImportError:
        print("❌ Error: FastAPI o uvicorn no instal·lats")
        print("\n📦 Instal·la les dependencies:")
        print("pip install fastapi uvicorn")
    except Exception as e:
        print(f"❌ Error: {e}")
