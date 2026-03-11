"""
Viora Professional - Medical AI Platform
Estil Apple amb funcionalitats multimodals completes
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
from datetime import datetime

app = FastAPI(title="Viora Professional")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def analyze_blood_data(data: Dict) -> Dict:
    """Analitza dades de sang amb lògica millorada"""
    risk_score = 0
    condition = "Normal"
    evidence = []
    recommendations = []
    
    # Hemoglobina
    if data.get('hemoglobin'):
        hb = data['hemoglobin']
        if hb < 12:
            risk_score += 2
            condition = "Possible Anèmia"
            evidence.append(f"Hemoglobina baixa: {hb} g/dL (normal: 12-16)")
            recommendations.append("Suplementació de ferro sota supervisió mèdica")
        elif hb > 16:
            evidence.append(f"Hemoglobina elevada: {hb} g/dL")
    
    # Glòbuls blancs
    if data.get('white_blood_cells'):
        wbc = data['white_blood_cells']
        if wbc > 11000:
            risk_score += 3
            condition = "Possible Infecció"
            evidence.append(f"Leucòcits elevats: {wbc}/μL (normal: 4000-11000)")
            recommendations.append("Consulta mèdica per avaluar infecció")
        elif wbc < 4000:
            risk_score += 2
            evidence.append(f"Leucòcits baixos: {wbc}/μL")
    
    # PCR
    if data.get('crp'):
        crp = data['crp']
        if crp > 10:
            risk_score += 3
            evidence.append(f"PCR elevada: {crp} mg/L (normal: <10)")
            recommendations.append("Possible procés inflamatori actiu")
        if crp > 50:
            risk_score += 2
            condition = "Inflamació Severa"
    
    # Glucosa
    if data.get('glucose'):
        gluc = data['glucose']
        if gluc > 126:
            risk_score += 2
            condition = "Possible Diabetis"
            evidence.append(f"Glucosa elevada: {gluc} mg/dL (normal: 70-100)")
            recommendations.append("Control de glucosa i consulta endocrinologia")
        elif gluc > 100:
            evidence.append(f"Glucosa en límit alt: {gluc} mg/dL")
    
    # Colesterol
    if data.get('cholesterol'):
        chol = data['cholesterol']
        if chol > 240:
            risk_score += 1
            evidence.append(f"Colesterol alt: {chol} mg/dL (recomanat: <200)")
            recommendations.append("Dieta baixa en greixos saturats")
    
    # Determinar nivell de risc
    if risk_score >= 6:
        risk_level = "Alt"
    elif risk_score >= 3:
        risk_level = "Moderat"
    else:
        risk_level = "Baix"
    
    if not evidence:
        evidence.append("Paràmetres dins dels rangs normals")
    
    if not recommendations:
        recommendations.append("Mantenir hàbits saludables")
        recommendations.append("Revisió anual recomanada")
    
    return {
        'condition': condition,
        'risk_level': risk_level,
        'risk_score': risk_score,
        'evidence': evidence,
        'recommendations': recommendations,
        'confidence': min(0.5 + (risk_score * 0.08), 0.95)
    }

def analyze_xray_simulation() -> Dict:
    """Simula anàlisi de radiografia"""
    conditions = ['Normal', 'Possible Pneumònia', 'Possible Cardiomegàlia', 'Possible Nòdul Pulmonar']
    condition = conditions[0]  # Per defecte normal en demo
    
    return {
        'condition': condition,
        'confidence': 0.75,
        'regions': ['Camps pulmonars clars', 'Silueta cardíaca normal'],
        'evidence': ['Radiografia processada correctament']
    }

@app.get("/", response_class=HTMLResponse)
async def home():
    with open('templates/viora_apple.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.post("/api/analyze")
async def analyze(
    xray_file: Optional[UploadFile] = File(None),
    blood_pdf: Optional[UploadFile] = File(None),
    blood_data: Optional[str] = Form(None)
):
    """Endpoint principal d'anàlisi multimodal"""
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'has_xray': xray_file is not None,
        'has_blood': blood_data is not None or blood_pdf is not None,
        'xray_analysis': None,
        'blood_analysis': None,
        'combined_analysis': None
    }
    
    # Analitzar radiografia si existeix
    if xray_file:
        results['xray_analysis'] = analyze_xray_simulation()
    
    # Analitzar sang si existeix
    if blood_data:
        blood_dict = json.loads(blood_data)
        results['blood_analysis'] = analyze_blood_data(blood_dict)
    
    # Anàlisi combinada
    if results['xray_analysis'] and results['blood_analysis']:
        # Fusionar resultats
        xray = results['xray_analysis']
        blood = results['blood_analysis']
        
        combined_evidence = []
        if xray['evidence']:
            combined_evidence.extend([f"Radiografia: {e}" for e in xray['evidence']])
        if blood['evidence']:
            combined_evidence.extend([f"Analítica: {e}" for e in blood['evidence']])
        
        # Determinar condició principal
        if blood['risk_score'] > 5:
            main_condition = blood['condition']
            risk_level = blood['risk_level']
        else:
            main_condition = xray['condition']
            risk_level = blood.get('risk_level', 'Baix')
        
        results['combined_analysis'] = {
            'condition': main_condition,
            'risk_level': risk_level,
            'evidence': combined_evidence,
            'recommendations': blood.get('recommendations', []),
            'confidence': (xray['confidence'] + blood.get('confidence', 0.5)) / 2
        }
    elif results['xray_analysis']:
        results['combined_analysis'] = results['xray_analysis']
        results['combined_analysis']['risk_level'] = 'Baix'
    elif results['blood_analysis']:
        results['combined_analysis'] = results['blood_analysis']
    
    return JSONResponse(content=results)

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0", "mode": "professional"}

if __name__ == "__main__":
    import uvicorn
    print("="*70)
    print("🏥 VIORA PROFESSIONAL - Medical AI Platform")
    print("="*70)
    print("\n✨ Estil Apple | Funcionalitats Multimodals")
    print("📍 URL: http://localhost:8000")
    print("\n💡 Funcionalitats:")
    print("   • Anàlisi de radiografies (JPG/PNG)")
    print("   • Anàlisi d'analítiques (manual o PDF)")
    print("   • Anàlisi combinada multimodal")
    print("   • Informe mèdic orientatiu")
    print("\n⚠️  Mode DEMO - Prediccions simulades per fins educatius")
    print("="*70)
    print("\nPrem Ctrl+C per aturar\n")
    
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
