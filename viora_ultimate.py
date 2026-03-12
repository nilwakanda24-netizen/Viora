"""
Viora Ultimate - Professional Medical AI Platform
Amb pestanyes interactives, logo modern i funcionalitats completes
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
from datetime import datetime
import sqlite3
import re
import io
from PIL import Image
import pytesseract

# Configurar pytesseract (pot requerir instal·lació)
# Windows: descarregar de https://github.com/UB-Mannheim/tesseract/wiki
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = FastAPI(title="Viora Ultimate")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialitzar base de dades per comentaris
def init_db():
    conn = sqlite3.connect('viora_comments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  email TEXT,
                  comment TEXT,
                  rating INTEGER,
                  timestamp TEXT,
                  approved INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

class PatientInfo(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    medical_history: Optional[str] = None

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

class Comment(BaseModel):
    name: str
    email: str
    comment: str
    rating: int

# Valors de referència
REFERENCE_VALUES = {
    'hemoglobin': {'min': 10.0, 'max': 13.5, 'unit': 'g/dL', 'name': 'Hemoglobina'},
    'hematocrit': {'min': 32.0, 'max': 41.0, 'unit': '%', 'name': 'Hematòcrit'},
    'white_blood_cells': {'min': 4190, 'max': 9680, 'unit': '/μL', 'name': 'Leucòcits'},
    'neutrophils': {'min': 1820, 'max': 7150, 'unit': 'cel/mm³', 'name': 'Neutròfils'},
    'lymphocytes': {'min': 1140, 'max': 3260, 'unit': 'cel/mm³', 'name': 'Limfòcits'},
    'platelets': {'min': 150000, 'max': 332000, 'unit': '/μL', 'name': 'Plaquetes'},
    'glucose': {'min': 73.8, 'max': 106, 'unit': 'mg/dL', 'name': 'Glucosa'},
    'creatinine': {'min': 0.70, 'max': 1.20, 'unit': 'mg/dL', 'name': 'Creatinina'},
    'uric_acid': {'min': 3.40, 'max': 7.00, 'unit': 'mg/dL', 'name': 'Àcid úric'},
    'ast': {'min': 0, 'max': 50.0, 'unit': 'U/L', 'name': 'AST (GOT)'},
    'alt': {'min': 0, 'max': 50.0, 'unit': 'U/L', 'name': 'ALT (GPT)'},
    'ggt': {'min': 0, 'max': 60.0, 'unit': 'U/L', 'name': 'GGT'},
    'bilirubin': {'min': 0, 'max': 1.00, 'unit': 'mg/dL', 'name': 'Bilirrubina total'},
    'calcium': {'min': 8.72, 'max': 10.4, 'unit': 'mg/dL', 'name': 'Calci'},
    'iron': {'min': 33.0, 'max': 193, 'unit': 'μg/dL', 'name': 'Ferro'},
    'ferritin': {'min': 30.0, 'max': 400, 'unit': 'ng/mL', 'name': 'Ferritina'},
    'cholesterol': {'min': 0, 'max': 200, 'unit': 'mg/dL', 'name': 'Colesterol total'},
    'hdl': {'min': 40.14, 'max': 200, 'unit': 'mg/dL', 'name': 'Colesterol HDL'},
    'ldl': {'min': 0, 'max': 99.6, 'unit': 'mg/dL', 'name': 'Colesterol LDL'},
    'triglycerides': {'min': 0, 'max': 150, 'unit': 'mg/dL', 'name': 'Triglicèrids'},
    'hba1c': {'min': 0, 'max': 5.7, 'unit': '%', 'name': 'Hemoglobina glicosilada'},
    'vitamin_d': {'min': 30.0, 'max': 100, 'unit': 'ng/mL', 'name': 'Vitamina D'},
    'vitamin_b12': {'min': 300, 'max': 2000, 'unit': 'pg/mL', 'name': 'Vitamina B12'},
    'tsh': {'min': 0.51, 'max': 4.30, 'unit': 'mUI/L', 'name': 'TSH'},
    't4_free': {'min': 0.98, 'max': 1.63, 'unit': 'ng/dL', 'name': 'T4 lliure'},
    'testosterone': {'min': 249, 'max': 836, 'unit': 'ng/dL', 'name': 'Testosterona'}
}

def analyze_blood_data(data: Dict) -> Dict:
    """Analitza dades de sang amb lògica clínica avançada basada en valors reals"""
    risk_score = 0
    condition = "Paràmetres normals"
    evidence = []
    recommendations = []
    abnormal_values = []
    
    # Comptar quants valors s'han introduït
    values_count = sum(1 for v in data.values() if v is not None)
    
    if values_count == 0:
        return {
            'condition': 'Sense dades',
            'risk_level': 'Baix',
            'risk_score': 0,
            'evidence': ['No s\'han introduït valors d\'analítica'],
            'recommendations': ['Introdueix valors per obtenir una anàlisi'],
            'abnormal_values': [],
            'confidence': 0.0
        }
    
    # Analitzar cada paràmetre
    for key, value in data.items():
        if value and key in REFERENCE_VALUES:
            ref = REFERENCE_VALUES[key]
            if value < ref['min']:
                risk_score += 2
                abnormal_values.append({
                    'parameter': ref['name'],
                    'value': value,
                    'reference': f"{ref['min']}-{ref['max']}",
                    'status': 'baix'
                })
                evidence.append(f"{ref['name']} baix: {value} {ref['unit']} (normal: {ref['min']}-{ref['max']})")
            elif value > ref['max']:
                risk_score += 2
                abnormal_values.append({
                    'parameter': ref['name'],
                    'value': value,
                    'reference': f"{ref['min']}-{ref['max']}",
                    'status': 'alt'
                })
                evidence.append(f"{ref['name']} alt: {value} {ref['unit']} (normal: {ref['min']}-{ref['max']})")
    
    # Anàlisi específica per condicions
    
    # Hemoglobina i anèmia
    if data.get('hemoglobin'):
        hb = data['hemoglobin']
        if hb < 10:
            condition = "Anèmia Severa"
            risk_score += 4
            recommendations.append("⚠️ Consulta mèdica urgent - anèmia severa")
            recommendations.append("Possible necessitat de transfusió")
        elif hb < 12:
            condition = "Anèmia Lleu-Moderada"
            risk_score += 2
            recommendations.append("Suplementació de ferro sota supervisió mèdica")
            recommendations.append("Dieta rica en ferro: carn vermella, espinacs, llegums")
        elif hb > 16:
            evidence.append(f"Hemoglobina elevada: {hb} g/dL")
            recommendations.append("Hemoglobina alta - assegurar bona hidratació")
    
    # Leucòcits i infecció
    if data.get('white_blood_cells'):
        wbc = data['white_blood_cells']
        if wbc > 11000:
            condition = "Possible Infecció o Procés Inflamatori"
            risk_score += 3
            recommendations.append("Leucocitosi detectada - possible infecció")
            recommendations.append("Consulta mèdica per avaluar causa")
        elif wbc < 4000:
            condition = "Leucopènia"
            risk_score += 3
            recommendations.append("Leucòcits baixos - possible immunosupressió")
            recommendations.append("Consulta amb hematòleg")
    
    # Glucosa i diabetis
    if data.get('glucose'):
        gluc = data['glucose']
        if gluc > 126:
            condition = "Diabetis Mellitus"
            risk_score += 4
            recommendations.append("Glucosa elevada - criteri diagnòstic de diabetis")
            recommendations.append("Consulta urgent amb endocrinologia")
            recommendations.append("Control dietètic estricte")
        elif gluc > 106:
            condition = "Prediabetis"
            risk_score += 2
            recommendations.append("Glucosa en rang de prediabetis")
            recommendations.append("Dieta baixa en sucres i carbohidrats refinats")
            recommendations.append("Exercici regular mínim 150 min/setmana")
    
    # HbA1c
    if data.get('hba1c'):
        hba1c = data['hba1c']
        if hba1c >= 6.5:
            condition = "Diabetis Mellitus (per HbA1c)"
            risk_score += 4
            recommendations.append("HbA1c elevada - diabetis confirmada")
        elif hba1c >= 5.7:
            recommendations.append("HbA1c en rang de prediabetis")
    
    # Colesterol i risc cardiovascular
    if data.get('cholesterol'):
        chol = data['cholesterol']
        if chol > 240:
            risk_score += 2
            recommendations.append("Colesterol total alt - risc cardiovascular")
            recommendations.append("Dieta baixa en greixos saturats")
            recommendations.append("Considerar estatines (consulta mèdica)")
        elif chol > 200:
            recommendations.append("Colesterol lleugerament elevat")
            recommendations.append("Dieta mediterrània recomanada")
    
    # LDL (colesterol dolent)
    if data.get('ldl'):
        ldl = data['ldl']
        if ldl > 160:
            risk_score += 3
            recommendations.append("LDL molt alt - risc cardiovascular elevat")
        elif ldl > 130:
            recommendations.append("LDL elevat - millorar dieta")
    
    # HDL (colesterol bo)
    if data.get('hdl'):
        hdl = data['hdl']
        if hdl < 40:
            risk_score += 2
            recommendations.append("HDL baix - augmentar exercici aeròbic")
            recommendations.append("Considerar omega-3")
    
    # Triglicèrids
    if data.get('triglycerides'):
        tg = data['triglycerides']
        if tg > 200:
            risk_score += 2
            recommendations.append("Triglicèrids alts - reduir alcohol i sucres")
        elif tg > 150:
            recommendations.append("Triglicèrids lleugerament elevats")
    
    # Enzims hepàtics
    if data.get('ast') and data['ast'] > 50:
        risk_score += 2
        recommendations.append("AST elevada - possible dany hepàtic")
        recommendations.append("Evitar alcohol completament")
    
    if data.get('alt') and data['alt'] > 50:
        risk_score += 2
        recommendations.append("ALT elevada - possible hepatitis")
        recommendations.append("Consulta amb hepatòleg")
    
    if data.get('ggt') and data['ggt'] > 60:
        recommendations.append("GGT elevada - reduir consum d'alcohol")
    
    # Funció renal
    if data.get('creatinine'):
        creat = data['creatinine']
        if creat > 1.3:
            risk_score += 3
            recommendations.append("Creatinina elevada - possible insuficiència renal")
            recommendations.append("Consulta amb nefrologia")
    
    # Vitamines
    if data.get('vitamin_d'):
        vit_d = data['vitamin_d']
        if vit_d < 20:
            recommendations.append("Dèficit de vitamina D - suplementació recomanada")
        elif vit_d < 30:
            recommendations.append("Insuficiència de vitamina D")
    
    if data.get('vitamin_b12'):
        b12 = data['vitamin_b12']
        if b12 < 200:
            risk_score += 2
            recommendations.append("Dèficit de B12 - suplementació urgent")
    
    # Tiroides
    if data.get('tsh'):
        tsh = data['tsh']
        if tsh > 4.3:
            recommendations.append("TSH elevada - possible hipotiroidisme")
            recommendations.append("Consulta amb endocrinologia")
        elif tsh < 0.51:
            recommendations.append("TSH baixa - possible hipertiroidisme")
    
    # Determinar nivell de risc
    if risk_score >= 8:
        risk_level = "Alt"
    elif risk_score >= 4:
        risk_level = "Moderat"
    else:
        risk_level = "Baix"
    
    if not evidence:
        evidence.append(f"S'han analitzat {values_count} paràmetres")
        evidence.append("Tots els valors introduïts dins dels rangs normals")
    
    if not recommendations:
        recommendations.extend([
            "Paràmetres dins de la normalitat",
            "Mantenir hàbits saludables",
            "Dieta mediterrània equilibrada",
            "Exercici regular 150 min/setmana",
            "Revisió anual recomanada"
        ])
    
    # Ajustar confiança segons nombre de valors
    base_confidence = 0.5 + (risk_score * 0.06)
    confidence_factor = min(values_count / 10, 1.0)
    confidence = min(base_confidence * confidence_factor, 0.95)
    
    return {
        'condition': condition,
        'risk_level': risk_level,
        'risk_score': risk_score,
        'evidence': evidence,
        'recommendations': recommendations,
        'abnormal_values': abnormal_values,
        'confidence': confidence,
        'values_analyzed': values_count
    }

def extract_blood_values_from_text(text: str) -> Dict:
    """
    Extreu valors d'analítica de sang amb detecció ULTRA flexible
    Segueix les normes de transcripció literal del document
    """
    values = {}
    
    print(f"\n{'='*70}")
    print(f"[DEBUG] INICI EXTRACCIÓ - Text de {len(text)} caràcters")
    print(f"{'='*70}")
    
    # Preparar text per anàlisi
    text_lower = text.lower()
    lines = text.split('\n')
    print(f"[DEBUG] Document amb {len(lines)} línies")
    
    # Funció per validar si un valor és vàlid (no és any, codi, etc.)
    def is_valid_value(value: float, param_type: str) -> bool:
        """Valida que el valor estigui dins de rangs raonables"""
        ranges = {
            'hemoglobin': (5, 25),
            'hematocrit': (20, 60),
            'white_blood_cells': (0.5, 50),
            'neutrophils': (100, 15000),
            'lymphocytes': (100, 10000),
            'monocytes': (0, 3000),
            'eosinophils': (0, 2000),
            'basophils': (0, 500),
            'platelets': (10, 1000),
            'glucose': (30, 600),
            'hba1c': (3, 20),
            'creatinine': (0.3, 15),
            'uric_acid': (1, 20),
            'ast': (5, 5000),
            'alt': (5, 5000),
            'ggt': (5, 5000),
            'albumin': (1, 10),
            'bilirubin': (0.1, 30),
            'calcium': (5, 15),
            'iron': (10, 500),
            'transferrin': (100, 500),
            'ferritin': (5, 5000),
            'cholesterol': (50, 500),
            'hdl': (10, 200),
            'ldl': (10, 300),
            'triglycerides': (20, 1000),
            'sodium': (120, 160),
            'potassium': (2, 8),
            'ige': (0, 5000),
            'vitamin_d': (5, 200),
            'vitamin_b12': (100, 5000),
            'folic_acid': (1, 50),
            'tsh': (0.01, 50),
            't4_free': (0.1, 10),
            't3_free': (0.5, 10),
            'testosterone': (10, 2000),
        }
        
        if param_type in ranges:
            min_val, max_val = ranges[param_type]
            is_valid = min_val <= value <= max_val
            if not is_valid:
                print(f"    ⚠️  Valor {value} fora de rang per {param_type} ({min_val}-{max_val})")
            return is_valid
        return True
    
    # ESTRATÈGIA 1: Patrons ULTRA flexibles amb [^0-9]{0,100}
    # Això permet trobar números fins i tot amb molt text entremig
    ultra_patterns = {
        'hemoglobin': [
            r'hemoglobin[aíi]?[^0-9]{0,100}(\d+[.,]\d+)[^0-9]{0,20}g[/\s]*d?l',
            r'\bhb\b[^0-9]{0,50}(\d+[.,]\d+)',
        ],
        'hematocrit': [
            r'hematocrit[oó]?[^0-9]{0,100}(\d+[.,]\d+)[^0-9]{0,20}%',
            r'hto[^0-9]{0,50}(\d+[.,]\d+)',
        ],
        'white_blood_cells': [
            r'leucocit[eos]?[^0-9]{0,100}(\d+[.,]?\d*)[^0-9]{0,50}(?:10\s*exp|x\s*10|e\+?0?9)',
            r'wbc[^0-9]{0,50}(\d+[.,]?\d*)',
            r'gl[oó]bul[eos]?\s+blanc[eos]?[^0-9]{0,100}(\d+)',
        ],
        'neutrophils': [
            r'neutr[oó]fil[eos]?[^0-9]{0,100}(\d+)[^0-9]{0,30}cel',
            r'neutrophils?[^0-9]{0,50}(\d+)',
        ],
        'lymphocytes': [
            r'linfocit[eos]?[^0-9]{0,100}(\d+)[^0-9]{0,30}cel',
            r'lymphocytes?[^0-9]{0,50}(\d+)',
        ],
        'monocytes': [
            r'monocit[eos]?[^0-9]{0,100}(\d+)[^0-9]{0,30}cel',
        ],
        'eosinophils': [
            r'eosin[oó]fil[eos]?[^0-9]{0,100}(\d+)[^0-9]{0,30}cel',
        ],
        'basophils': [
            r'bas[oó]fil[eos]?[^0-9]{0,100}(\d+[.,]?\d*)[^0-9]{0,30}cel',
        ],
        'platelets': [
            r'plaquet[ae]s?[^0-9]{0,100}(\d+)[^0-9]{0,50}(?:10\s*exp|x\s*10|e\+?0?9)',
            r'plt[^0-9]{0,50}(\d+)',
        ],
        'glucose': [
            r'glucos[ae]?[^0-9]{0,100}(\d+)[^0-9]{0,30}mg[/\s]*d?l',
        ],
        'hba1c': [
            r'hemoglobin[aí]?\s+(?:a1c|glicosilad[ae]?)[^0-9]{0,100}(\d+[.,]\d+)[^0-9]{0,20}%',
            r'hba1c[^0-9]{0,50}(\d+[.,]\d+)',
        ],
        'creatinine': [
            r'creatinin[ae]?[^0-9]{0,100}(\d+[.,]\d+)[^0-9]{0,30}mg[/\s]*d?l',
        ],
        'uric_acid': [
            r'[aá]cid[eo]?\s+[uú]ric[eo]?[^0-9]{0,100}(\d+[.,]\d+)',
            r'urato[^0-9]{0,50}(\d+[.,]\d+)',
        ],
        'ast': [
            r'(?:ast|got|aspartat[eo])[^0-9]{0,100}(\d+[.,]?\d*)[^0-9]{0,30}u[/\s]*l',
        ],
        'alt': [
            r'(?:alt|gpt|alanin[ae]?)[^0-9]{0,100}(\d+[.,]\d+)[^0-9]{0,30}u[/\s]*l',
        ],
        'ggt': [
            r'ggt[^0-9]{0,100}(\d+[.,]\d+)[^0-9]{0,30}u[/\s]*l',
            r'gamma[^0-9]{0,100}(\d+[.,]\d+)[^0-9]{0,30}u[/\s]*l',
        ],
        'albumin': [
            r'alb[uú]min[ae]?[^0-9]{0,100}(\d+[.,]\d+)',
        ],
        'bilirubin': [
            r'bilirrubina[^0-9]{0,100}(\d+[.,]\d+)',
        ],
        'calcium': [
            r'calci[eo]?[^0-9]{0,100}(\d+[.,]\d+)',
        ],
        'iron': [
            r'hierro[^0-9]{0,100}(\d+[.,]?\d*)',
            r'ferro[^0-9]{0,100}(\d+[.,]?\d*)',
        ],
        'transferrin': [
            r'transferrina[^0-9]{0,100}(\d+)',
        ],
        'ferritin': [
            r'ferritin[ae]?[^0-9]{0,100}(\d+[.,]?\d*)',
        ],
        'cholesterol': [
            r'colesterol(?!\s+(?:hdl|ldl))[^0-9]{0,100}(\d+)[^0-9]{0,30}mg[/\s]*d?l',
        ],
        'hdl': [
            r'(?:hdl|colesterol\s+hdl)[^0-9]{0,100}(\d+[.,]\d+)',
        ],
        'ldl': [
            r'(?:ldl|colesterol\s+ldl)[^0-9]{0,100}(\d+[.,]?\d*)',
        ],
        'triglycerides': [
            r'trigl[ií]c[eé]rid[eo]s?[^0-9]{0,100}(\d+[.,]\d+)',
        ],
        'sodium': [
            r'sodi[eo]?[^0-9]{0,100}(\d+)',
        ],
        'potassium': [
            r'potasi[eo]?[^0-9]{0,100}(\d+[.,]\d+)',
        ],
        'ige': [
            r'inmunoglobulina\s+e[^0-9]{0,100}(\d+[.,]?\d*)',
            r'\bige\b[^0-9]{0,50}(\d+[.,]?\d*)',
        ],
        'vitamin_d': [
            r'vitamina\s+d[^0-9]{0,100}(\d+[.,]\d+)',
            r'25[- ]oh[^0-9]{0,50}(\d+[.,]\d+)',
        ],
        'vitamin_b12': [
            r'vitamina\s+b12[^0-9]{0,100}(\d+[.,]?\d*)',
            r'\bb12\b[^0-9]{0,50}(\d+[.,]?\d*)',
        ],
        'folic_acid': [
            r'[aá]cid[eo]?\s+f[oó]lic[eo][^0-9]{0,100}(\d+[.,]\d+)',
        ],
        'tsh': [
            r'\btsh\b[^0-9]{0,100}(\d+[.,]\d+)',
        ],
        't4_free': [
            r't4\s+libre[^0-9]{0,100}(\d+[.,]\d+)',
            r't4\s+free[^0-9]{0,100}(\d+[.,]\d+)',
        ],
        't3_free': [
            r't3\s+libre[^0-9]{0,100}(\d+[.,]\d+)',
            r't3\s+free[^0-9]{0,100}(\d+[.,]\d+)',
        ],
        'testosterone': [
            r'testosterona[^0-9]{0,100}(\d+[.,]?\d*)',
        ],
    }
    
    print(f"\n[ESTRATÈGIA 1] Patrons ultra-flexibles...")
    for key, pattern_list in ultra_patterns.items():
        if key in values:
            continue  # Ja trobat
        
        for pattern in pattern_list:
            match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    value_str = match.group(1).replace(',', '.')
                    value = float(value_str)
                    
                    if is_valid_value(value, key):
                        values[key] = value
                        print(f"  ✅ {key} = {value} (patró: {pattern[:50]}...)")
                        break
                except Exception as e:
                    print(f"  ❌ Error convertint {key}: {e}")
    
    # ESTRATÈGIA 2: Anàlisi línia per línia (per taules)
    print(f"\n[ESTRATÈGIA 2] Anàlisi línia per línia...")
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        if not line_lower or len(line_lower) < 5:
            continue
        
        # Buscar números a la línia
        numbers = re.findall(r'\d+[.,]\d+|\d+', line_lower)
        if not numbers:
            continue
        
        # Identificar paràmetre per paraules clau
        param_keywords = {
            'hemoglobin': ['hemoglobin', 'hb'],
            'hematocrit': ['hematocrit', 'hto'],
            'white_blood_cells': ['leucocit', 'wbc', 'globul blanc'],
            'neutrophils': ['neutrofil', 'neutrophil'],
            'lymphocytes': ['linfocit', 'lymphocyte'],
            'monocytes': ['monocit', 'monocyte'],
            'eosinophils': ['eosinofil', 'eosinophil'],
            'basophils': ['basofil', 'basophil'],
            'platelets': ['plaquet', 'plt'],
            'glucose': ['glucos', 'glucose'],
            'hba1c': ['hba1c', 'a1c', 'glicosilad'],
            'creatinine': ['creatinin'],
            'uric_acid': ['acid uric', 'urato'],
            'ast': ['ast', 'got', 'aspartat'],
            'alt': ['alt', 'gpt', 'alanin'],
            'ggt': ['ggt', 'gamma'],
            'cholesterol': ['colesterol total'],
            'hdl': ['hdl'],
            'ldl': ['ldl'],
            'triglycerides': ['triglicerid'],
            'ferritin': ['ferritin'],
            'vitamin_d': ['vitamina d', '25-oh'],
            'vitamin_b12': ['vitamina b12', 'b12'],
            'tsh': ['tsh'],
            'testosterone': ['testosterona'],
        }
        
        for param, keywords in param_keywords.items():
            if param in values:
                continue
            
            if any(kw in line_lower for kw in keywords):
                # Trobar el número més proper
                for num_str in numbers:
                    try:
                        value = float(num_str.replace(',', '.'))
                        if is_valid_value(value, param):
                            values[param] = value
                            print(f"  ✅ {param} = {value} (línia {i+1}: {line[:60]}...)")
                            break
                    except:
                        pass
    
    # ESTRATÈGIA 3: Cerca de números després de paraules clau (molt permissiva)
    print(f"\n[ESTRATÈGIA 3] Cerca permissiva de números...")
    simple_keywords = {
        'hemoglobin': r'(?:hemoglobin[aí]?|hb)\D{0,200}?(\d+[.,]\d+)',
        'glucose': r'glucos[ae]?\D{0,200}?(\d+[.,]?\d*)',
        'cholesterol': r'colesterol(?!\s+(?:hdl|ldl))\D{0,200}?(\d+)',
        'creatinine': r'creatinin[ae]?\D{0,200}?(\d+[.,]\d+)',
        'ast': r'(?:ast|got)\D{0,200}?(\d+)',
        'alt': r'(?:alt|gpt)\D{0,200}?(\d+)',
    }
    
    for key, pattern in simple_keywords.items():
        if key in values:
            continue
        
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1).replace(',', '.'))
                if is_valid_value(value, key):
                    values[key] = value
                    print(f"  ✅ {param} = {value} (cerca permissiva)")
            except:
                pass
    
    print(f"\n{'='*70}")
    print(f"[RESULTAT FINAL] S'han extret {len(values)} paràmetres:")
    for key, value in values.items():
        ref = REFERENCE_VALUES.get(key, {})
        print(f"  • {ref.get('name', key)}: {value} {ref.get('unit', '')}")
    print(f"{'='*70}\n")
    
    return values


@app.post("/api/extract-blood-data")
async def extract_blood_data(file: UploadFile = File(...)):
    """Extreu dades d'analítica d'un PDF o imatge amb OCR millorat"""
    try:
        content = await file.read()
        text = ""
        file_type = file.filename.lower().split('.')[-1]
        
        print(f"[INFO] Processant fitxer: {file.filename} (tipus: {file_type})")
        
        # Identificar tipus de fitxer
        if file_type in ['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff']:
            # És una imatge - aplicar OCR directament
            try:
                image = Image.open(io.BytesIO(content))
                print(f"[IMATGE] Dimensions: {image.size}, Mode: {image.mode}")
                
                # Aplicar OCR amb configuració millorada
                custom_config = r'--oem 3 --psm 6'  # PSM 6: assumeix un bloc de text uniforme
                text = pytesseract.image_to_string(image, lang='spa+cat+eng', config=custom_config)
                print(f"[OCR] Text extret de la imatge ({len(text)} caràcters)")
            except Exception as img_error:
                print(f"[ERROR] Error processant imatge: {img_error}")
                return JSONResponse(content={
                    'status': 'error',
                    'message': f'Error processant la imatge: {str(img_error)}'
                })
                
        elif file_type == 'pdf':
            # És un PDF - intentar extracció de text digital primer
            try:
                import PyPDF2
                pdf_file = io.BytesIO(content)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
                print(f"[PDF] Document amb {num_pages} pàgines")
                
                # Extreure text de cada pàgina
                for i, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 50:
                        text += f"\n=== PÀGINA {i} ===\n{page_text}\n"
                        print(f"[PDF] Pàgina {i}: {len(page_text)} caràcters extrets")
                    else:
                        print(f"[PDF] Pàgina {i}: Poc text detectat, pot ser escanejada")
                
                # Si no s'ha extret gaire text, pot ser un PDF escanejat
                if len(text.strip()) < 100:
                    print("[PDF] PDF escanejat detectat - aplicant OCR...")
                    try:
                        import pdf2image
                        # Convertir PDF a imatges i aplicar OCR
                        images = pdf2image.convert_from_bytes(content)
                        text = ""
                        for i, img in enumerate(images, 1):
                            print(f"[OCR] Processant pàgina {i}/{len(images)}...")
                            custom_config = r'--oem 3 --psm 6'
                            page_text = pytesseract.image_to_string(img, lang='spa+cat+eng', config=custom_config)
                            text += f"\n=== PÀGINA {i} ===\n{page_text}\n"
                    except ImportError:
                        print("[WARNING] pdf2image no instal·lat - no es pot fer OCR del PDF escanejat")
                        print("[INFO] Instal·la amb: pip install pdf2image")
                    except Exception as ocr_error:
                        print(f"[ERROR] Error aplicant OCR al PDF: {ocr_error}")
                
                print(f"[PDF] Total text extret: {len(text)} caràcters")
                
            except Exception as pdf_error:
                print(f"[ERROR] Error processant PDF: {pdf_error}")
                return JSONResponse(content={
                    'status': 'error',
                    'message': f'Error processant el PDF: {str(pdf_error)}'
                })
        else:
            return JSONResponse(content={
                'status': 'error',
                'message': f'Tipus de fitxer no suportat: {file_type}. Utilitza PDF o imatges (JPG, PNG, etc.)'
            })
        
        # Debug: Mostrar text extret
        print("\n" + "="*70)
        print("[DEBUG] TEXT COMPLET EXTRET:")
        print("="*70)
        print(text[:2000])  # Primeres 2000 caràcters
        print("="*70 + "\n")
        
        # Extreure valors amb els patrons millorats
        values = extract_blood_values_from_text(text)
        
        print(f"\n[RESULT] ✅ S'han extret {len(values)} valors:")
        for key, value in values.items():
            print(f"  • {key}: {value}")
        
        if not values:
            return JSONResponse(content={
                'status': 'warning',
                'message': 'No s\'han trobat valors d\'analítica al document. Revisa la consola per veure el text extret.',
                'values': {},
                'debug_text': text[:2000]
            })
        
        return JSONResponse(content={
            'status': 'success',
            'message': f'S\'han extret {len(values)} paràmetres',
            'values': values,
            'debug_text': text[:1000]
        })
        
    except Exception as e:
        print(f"[ERROR] Exception general: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={
            'status': 'error',
            'message': f'Error processant el fitxer: {str(e)}'
        })

@app.get("/", response_class=HTMLResponse)
async def home():
    with open('templates/viora_ultimate.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.get("/api/reference-values")
async def get_reference_values():
    """Retorna valors de referència"""
    return JSONResponse(content=REFERENCE_VALUES)

@app.post("/api/analyze")
async def analyze(
    patient_info: Optional[str] = Form(None),
    xray_file: Optional[UploadFile] = File(None),
    blood_pdf: Optional[UploadFile] = File(None),
    blood_data: Optional[str] = Form(None)
):
    """Endpoint principal d'anàlisi multimodal"""
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'patient_info': json.loads(patient_info) if patient_info else None,
        'has_xray': xray_file is not None,
        'has_blood': blood_data is not None or blood_pdf is not None,
        'xray_analysis': None,
        'blood_analysis': None,
        'combined_analysis': None
    }
    
    # Analitzar radiografia
    if xray_file:
        # Simulació d'anàlisi de radiografia
        results['xray_analysis'] = {
            'condition': 'Camps pulmonars clars',
            'confidence': 0.85,
            'regions': ['Camps pulmonars clars', 'Silueta cardíaca normal', 'Sense infiltrats visibles'],
            'evidence': ['Radiografia de tòrax processada correctament', 'No s\'observen anomalies evidents'],
            'recommendations': ['Radiografia dins de la normalitat', 'Mantenir controls periòdics']
        }
    
    # Analitzar sang
    if blood_data:
        blood_dict = json.loads(blood_data)
        # Filtrar valors nuls
        blood_dict = {k: v for k, v in blood_dict.items() if v is not None}
        if blood_dict:  # Només analitzar si hi ha valors
            results['blood_analysis'] = analyze_blood_data(blood_dict)
    
    # Anàlisi combinada
    if results['xray_analysis'] and results['blood_analysis']:
        # Ambdues anàlisis disponibles
        xray = results['xray_analysis']
        blood = results['blood_analysis']
        
        combined_evidence = []
        if xray['evidence']:
            combined_evidence.extend([f"📸 {e}" for e in xray['evidence']])
        if blood['evidence']:
            combined_evidence.extend([f"🩸 {e}" for e in blood['evidence']])
        
        # Combinar recomanacions
        combined_recommendations = []
        if blood['risk_level'] != 'Baix':
            combined_recommendations.extend(blood['recommendations'])
        else:
            combined_recommendations.extend(xray.get('recommendations', []))
        
        results['combined_analysis'] = {
            'condition': blood['condition'] if blood['risk_level'] != 'Baix' else xray['condition'],
            'risk_level': blood['risk_level'],
            'evidence': combined_evidence,
            'recommendations': combined_recommendations,
            'abnormal_values': blood.get('abnormal_values', []),
            'confidence': (xray['confidence'] + blood['confidence']) / 2
        }
    elif results['xray_analysis']:
        # Només radiografia
        xray = results['xray_analysis']
        results['combined_analysis'] = {
            'condition': xray['condition'],
            'risk_level': 'Baix',
            'evidence': [f"📸 {e}" for e in xray['evidence']],
            'recommendations': xray.get('recommendations', ['Radiografia processada correctament']),
            'abnormal_values': [],
            'confidence': xray['confidence']
        }
    elif results['blood_analysis']:
        # Només analítica
        blood = results['blood_analysis']
        results['combined_analysis'] = {
            'condition': blood['condition'],
            'risk_level': blood['risk_level'],
            'evidence': [f"🩸 {e}" for e in blood['evidence']],
            'recommendations': blood['recommendations'],
            'abnormal_values': blood.get('abnormal_values', []),
            'confidence': blood['confidence']
        }
    
    return JSONResponse(content=results)

@app.post("/api/comments")
async def add_comment(comment: Comment):
    """Afegir comentari"""
    conn = sqlite3.connect('viora_comments.db')
    c = conn.cursor()
    c.execute('''INSERT INTO comments (name, email, comment, rating, timestamp)
                 VALUES (?, ?, ?, ?, ?)''',
              (comment.name, comment.email, comment.comment, comment.rating, 
               datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Comentari enviat per revisió"}

@app.get("/api/comments")
async def get_comments():
    """Obtenir comentaris aprovats"""
    conn = sqlite3.connect('viora_comments.db')
    c = conn.cursor()
    c.execute('SELECT name, comment, rating, timestamp FROM comments WHERE approved = 1 ORDER BY timestamp DESC LIMIT 10')
    comments = [{'name': row[0], 'comment': row[1], 'rating': row[2], 'timestamp': row[3]} 
                for row in c.fetchall()]
    conn.close()
    return JSONResponse(content=comments)

if __name__ == "__main__":
    import uvicorn
    print("="*70)
    print("🏥 VIORA ULTIMATE - Professional Medical AI Platform")
    print("="*70)
    print("\n✨ Pestanyes Interactives | Logo Modern | Estil Apple")
    print("📍 URL Local: http://localhost:8000")
    print("📍 URL Xarxa: http://<la-teva-ip>:8000")
    print("\n💡 Funcionalitats:")
    print("   • Informació bàsica del pacient")
    print("   • Valors de referència interactius")
    print("   • Informació addicional i recomanacions")
    print("   • Sistema de comentaris i feedback")
    print("   • Anàlisi multimodal completa")
    print("\n⚠️  Mode DEMO - Prediccions simulades per fins educatius")
    print("="*70)
    print("\nPrem Ctrl+C per aturar\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
