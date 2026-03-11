from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import sys
sys.path.append('..')

from models.chest_xray_model import ChestXRayModel
from models.blood_analysis_model import BloodAnalysisModel
from models.multimodal_fusion import MultimodalFusion

app = FastAPI(title="Viora API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialitzar models
xray_model = ChestXRayModel()
blood_model = BloodAnalysisModel()
fusion_model = MultimodalFusion()

class BloodData(BaseModel):
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

@app.get("/")
async def root():
    return {
        "message": "Viora AI Medical Screening System",
        "version": "1.0.0",
        "disclaimer": "Aquest és un sistema de suport clínic. NO substitueix el diagnòstic mèdic professional."
    }

@app.post("/analyze/xray")
async def analyze_xray(file: UploadFile = File(...)):
    """Analitza radiografia de tòrax"""
    temp_path = f"temp_{file.filename}"
    
    with open(temp_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    result = xray_model.predict(temp_path)
    
    return {
        "status": "success",
        "result": result
    }

@app.post("/analyze/blood")
async def analyze_blood(data: BloodData):
    """Analitza paràmetres de sang"""
    blood_dict = data.dict(exclude_none=True)
    result = blood_model.predict(blood_dict)
    
    return {
        "status": "success",
        "result": result
    }

@app.post("/analyze/complete")
async def complete_analysis(
    xray_file: UploadFile = File(...),
    blood_data: str = Form(...)
):
    """Anàlisi completa: radiografia + analítica"""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
