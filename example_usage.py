"""
Exemple d'ús del sistema Viora
"""

from models.chest_xray_model import ChestXRayModel
from models.blood_analysis_model import BloodAnalysisModel
from models.multimodal_fusion import MultimodalFusion

def example_complete_analysis():
    """Exemple d'anàlisi completa"""
    
    # Inicialitzar models
    xray_model = ChestXRayModel()
    blood_model = BloodAnalysisModel()
    fusion_model = MultimodalFusion()
    
    # Dades d'exemple
    xray_path = "data/examples/chest_xray_sample.jpg"
    
    blood_data = {
        "hemoglobin": 11.2,
        "white_blood_cells": 14000,
        "platelets": 250000,
        "crp": 15,
        "cholesterol": 210,
        "glucose": 110,
        "ferritin": 80,
        "alt": 35,
        "ast": 28,
        "creatinine": 1.0
    }
    
    print("🔬 Analitzant radiografia...")
    xray_result = xray_model.predict(xray_path)
    print(f"   Condició: {xray_result['condition']}")
    print(f"   Confiança: {xray_result['confidence']:.2%}")
    
    print("\n🩸 Analitzant sang...")
    blood_result = blood_model.predict(blood_data)
    print(f"   Condició: {blood_result['condition']}")
    print(f"   Confiança: {blood_result['confidence']:.2%}")
    
    print("\n🤖 Fusionant resultats...")
    final_result = fusion_model.fuse_predictions(xray_result, blood_result)
    
    print("\n" + "="*60)
    print("📋 INFORME VIORA")
    print("="*60)
    print(f"\n🔍 Possible condició: {final_result['possible_condition']}")
    print(f"⚠️  Nivell de risc: {final_result['risk_level']}")
    
    print("\n📊 Evidències:")
    for evidence in final_result['evidence']:
        print(f"   • {evidence}")
    
    print("\n💡 Recomanacions:")
    for rec in final_result['recommendations']:
        print(f"   • {rec}")
    
    print(f"\n{final_result['disclaimer']}")
    print("="*60)

if __name__ == "__main__":
    example_complete_analysis()
