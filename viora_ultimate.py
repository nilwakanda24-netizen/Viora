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
    """Extreu valors d'analítica de sang d'un text OCR amb patrons millorats"""
    values = {}
    
    # Normalitzar text: eliminar salts de línia dins de paraules
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text)  # Múltiples espais a un sol espai
    
    print(f"\n[DEBUG] Buscant valors al text normalitzat...")
    
    # Patrons MOLT més flexibles i específics per al format del PDF mèdic
    patterns = {
        'hemoglobin': [
            r'hemoglobin[aíi]?\s*:?\s*\*?\s*(\d+[.,]\d+)\s*g/dl',
            r'hb\s*:?\s*\*?\s*(\d+[.,]\d+)\s*g',
        ],
        'hematocrit': [
            r'hematocrit[oó]?\s*:?\s*\*?\s*(\d+[.,]\d+)\s*%',
        ],
        'white_blood_cells': [
            r'leucocit[eos]?\s*:?\s*\*?\s*(\d+[.,]?\d*)\s*(?:10\s*exp\s*9|10\^?exp9)',
            r'leucocitos?\s*:?\s*\*?\s*(\d+[.,]?\d*)\s*(?:10\s*exp\s*9|10\^?exp9)',
        ],
        'neutrophils': [
            r'neutr[oó]fil[eos]?\s+segmentad[eo]s?\s*:?\s*\*?\s*(\d+)\s*cel',
        ],
        'lymphocytes': [
            r'linfocit[eos]?\s*:?\s*\*?\s*(\d+)\s*cel',
        ],
        'monocytes': [
            r'monocit[eos]?\s*:?\s*\*?\s*(\d+)\s*cel',
        ],
        'eosinophils': [
            r'eosin[oó]fil[eos]?\s*:?\s*\*?\s*(\d+)\s*cel',
        ],
        'basophils': [
            r'bas[oó]fil[eos]?\s*:?\s*\*?\s*(\d+[.,]?\d*)\s*cel',
        ],
        'platelets': [
            r'plaquet[ae]s?\s*:?\s*\*?\s*(\d+)\s*(?:10\s*exp\s*9|10\^?exp9)',
        ],
        'glucose': [
            r'glucos[ae]?\s*,?\s*suero\s*.*?resultado\s*:?\s*\*?\s*(\d+)\s*mg/dl',
            r'glucos[ae]?\s*:?\s*\*?\s*(\d+)\s*mg/dl',
        ],
        'hba1c': [
            r'hemoglobin[aí]?\s+a1c\s*%?\s*:?\s*\*?\s*(\d+[.,]\d+)\s*%',
            r'hemoglobin[aí]?\s+glicosilad[ae]?\s*.*?resultado\s*:?\s*(\d+[.,]\d+)\s*%',
        ],
        'creatinine': [
            r'creatinin[ae]?\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)\s*mg/dl',
        ],
        'uric_acid': [
            r'[aá]cid[eo]?\s+[uú]ric[eo]?\s*\(?urato\)?\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        'ast': [
            r'aspartato?\s+aminotransferasa\s*\(got/ast\)\s*,?\s*suero\s*.*?resultado\s*:?\s*\*?\s*(\d+[.,]?\d*)\s*u/l',
            r'(?:ast|got)\s*:?\s*\*?\s*(\d+)\s*u/l',
        ],
        'alt': [
            r'alanin[ae]?\s+aminotransferasa\s*\(gpt/alt\)\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)\s*u/l',
        ],
        'ggt': [
            r'gamma\s+glutamil\s+transferasa\s*\(ggt\)\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)\s*u/l',
        ],
        'albumin': [
            r'alb[uú]min[ae]?\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        'bilirubin': [
            r'bilirrubina\s+total\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        'calcium': [
            r'calci[eo]?\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        'iron': [
            r'hierro\s*\(ii\+iii\)\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        'transferrin': [
            r'transferrina\s*\(?siderofilina\)?\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+)',
        ],
        'ferritin': [
            r'ferritin[ae]?\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]?\d*)',
        ],
        'cholesterol': [
            r'colesterol\s*,?\s*suero\s*.*?resultado\s*:?\s*\*?\s*(\d+)\s*mg/dl',
        ],
        'hdl': [
            r'colesterol\s+hdl\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        'ldl': [
            r'colesterol\s+ldl\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]?\d*)',
        ],
        'triglycerides': [
            r'trigl[ií]c[eé]rid[eo]s?\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        'sodium': [
            r'sodio\s+ion\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+)',
        ],
        'potassium': [
            r'potasio\s+ion\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        'ige': [
            r'inmunoglobulina\s+e\s*\(ige\)\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        'vitamin_d': [
            r'vitamina\s+d\s*\(25-oh-colecalciferol\)\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        'vitamin_b12': [
            r'vitamina\s+b12\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]?\d*)',
        ],
        'folic_acid': [
            r'[aá]cid[eo]?\s+f[oó]lic[eo]\s*.*?resultado\s*:?\s*\*?\s*(\d+[.,]\d+)',
        ],
        'tsh': [
            r'tsh\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        't4_free': [
            r't4\s+libre\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        't3_free': [
            r't3\s+libre\s*.*?resultado\s*:?\s*(\d+[.,]\d+)',
        ],
        'testosterone': [
            r'testosterona\s*,?\s*suero\s*.*?resultado\s*:?\s*(\d+[.,]?\d*)',
        ],
    }
    
    text_lower = text.lower()
    
    # Intentar cada patró per cada paràmetre
    for key, pattern_list in patterns.items():
        for pattern in pattern_list:
            match = re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL)
            if match:
                try:
                    # Convertir comes a punts
                    value_str = match.group(1).replace(',', '.')
                    value = float(value_str)
                    values[key] = value
                    print(f"  ✓ {key} = {value}")
                    break  # Si trobem un valor, no cal provar més patrons
                except Exception as e:
                    print(f"  ✗ Error convertint {key}: {e}")
    
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
