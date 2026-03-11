import numpy as np
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, List
import joblib

class BloodAnalysisModel:
    """Model ML per analitzar paràmetres de sang"""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.feature_names = [
            'hemoglobin',
            'white_blood_cells',
            'platelets',
            'crp',
            'cholesterol',
            'glucose',
            'ferritin',
            'alt',
            'ast',
            'creatinine'
        ]
        self.conditions = [
            'Normal',
            'Anemia',
            'Infection',
            'Inflammation',
            'Metabolic_Disorder'
        ]
    
    def preprocess_data(self, blood_data: Dict) -> np.ndarray:
        """Preprocessa dades d'analítica"""
        features = []
        for feature in self.feature_names:
            features.append(blood_data.get(feature, 0))
        return np.array(features).reshape(1, -1)
    
    def analyze_parameters(self, blood_data: Dict) -> Dict:
        """Analitza paràmetres individuals"""
        abnormalities = []
        
        # Ranges normals
        ranges = {
            'hemoglobin': (12.0, 16.0),
            'white_blood_cells': (4000, 11000),
            'platelets': (150000, 400000),
            'crp': (0, 10),
            'cholesterol': (0, 200),
            'glucose': (70, 100),
            'ferritin': (20, 200),
            'alt': (7, 56),
            'ast': (10, 40),
            'creatinine': (0.7, 1.3)
        }
        
        for param, (min_val, max_val) in ranges.items():
            value = blood_data.get(param)
            if value is not None:
                if value < min_val:
                    abnormalities.append(f"{param}: baix ({value})")
                elif value > max_val:
                    abnormalities.append(f"{param}: alt ({value})")
        
        return {
            'abnormalities': abnormalities,
            'abnormal_count': len(abnormalities)
        }
    
    def predict(self, blood_data: Dict) -> Dict:
        """Prediu condició a partir d'analítica"""
        features = self.preprocess_data(blood_data)
        analysis = self.analyze_parameters(blood_data)
        
        # Lògica simple de classificació basada en paràmetres
        risk_score = 0
        condition = 'Normal'
        
        if blood_data.get('hemoglobin', 15) < 12:
            risk_score += 2
            condition = 'Anemia'
        
        if blood_data.get('white_blood_cells', 7000) > 11000:
            risk_score += 3
            condition = 'Infection'
        
        if blood_data.get('crp', 5) > 10:
            risk_score += 3
            condition = 'Inflammation'
        
        if blood_data.get('glucose', 90) > 126:
            risk_score += 2
            condition = 'Metabolic_Disorder'
        
        confidence = min(0.5 + (risk_score * 0.1), 0.95)
        
        return {
            'condition': condition,
            'confidence': confidence,
            'risk_score': risk_score,
            'analysis': analysis
        }
