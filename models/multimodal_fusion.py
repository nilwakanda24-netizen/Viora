from typing import Dict, List
import numpy as np

class MultimodalFusion:
    """Combina prediccions de radiografia i analítica de sang"""
    
    def __init__(self):
        self.risk_levels = ['Baix', 'Moderat', 'Alt']
        
    def calculate_risk_level(self, xray_conf: float, blood_conf: float, 
                            xray_condition: str, blood_condition: str) -> str:
        """Calcula nivell de risc combinat"""
        avg_confidence = (xray_conf + blood_conf) / 2
        
        high_risk_conditions = ['Pneumonia', 'Tuberculosis', 'Pulmonary_Edema']
        
        if xray_condition in high_risk_conditions or blood_condition == 'Infection':
            if avg_confidence > 0.7:
                return 'Alt'
            else:
                return 'Moderat'
        
        if avg_confidence > 0.6:
            return 'Moderat'
        
        return 'Baix'
    
    def generate_evidence(self, xray_result: Dict, blood_result: Dict) -> List[str]:
        """Genera llista d'evidències"""
        evidence = []
        
        # Evidències de radiografia
        if xray_result['condition'] != 'Normal':
            evidence.append(f"Radiografia: {xray_result['condition']} detectat")
        
        # Evidències d'analítica
        if blood_result.get('analysis', {}).get('abnormalities'):
            for abnormality in blood_result['analysis']['abnormalities'][:3]:
                evidence.append(f"Analítica: {abnormality}")
        
        return evidence
    
    def generate_recommendations(self, risk_level: str, 
                                 xray_condition: str, 
                                 blood_condition: str) -> List[str]:
        """Genera recomanacions segons risc"""
        recommendations = []
        
        if risk_level == 'Baix':
            recommendations.extend([
                'Repetir analítica en 3 mesos',
                'Mantenir dieta equilibrada',
                'Exercici regular'
            ])
        
        elif risk_level == 'Moderat':
            recommendations.extend([
                'Consultar metge de família',
                'Possibles proves addicionals',
                'Seguiment en 2-4 setmanes'
            ])
            
            if 'Pneumonia' in xray_condition:
                recommendations.append('Possible radiografia de control')
        
        else:  # Alt
            recommendations.extend([
                '⚠️ Consulta mèdica urgent recomanada',
                'Possibles proves diagnòstiques immediates'
            ])
            
            if 'Pneumonia' in xray_condition or blood_condition == 'Infection':
                recommendations.append('Possible tractament antibiòtic (sota prescripció mèdica)')
            
            if 'Cardiomegaly' in xray_condition:
                recommendations.append('Electrocardiograma i ecocardiografia recomanats')
        
        return recommendations
    
    def fuse_predictions(self, xray_result: Dict, blood_result: Dict) -> Dict:
        """Fusiona prediccions dels dos models"""
        risk_level = self.calculate_risk_level(
            xray_result['confidence'],
            blood_result['confidence'],
            xray_result['condition'],
            blood_result['condition']
        )
        
        evidence = self.generate_evidence(xray_result, blood_result)
        recommendations = self.generate_recommendations(
            risk_level,
            xray_result['condition'],
            blood_result['condition']
        )
        
        # Determina condició principal
        if xray_result['confidence'] > blood_result['confidence']:
            primary_condition = xray_result['condition']
        else:
            primary_condition = blood_result['condition']
        
        return {
            'possible_condition': primary_condition,
            'risk_level': risk_level,
            'evidence': evidence,
            'recommendations': recommendations,
            'xray_analysis': xray_result,
            'blood_analysis': blood_result,
            'disclaimer': '⚠️ Aquest és un sistema de suport clínic. NO substitueix el diagnòstic mèdic professional.'
        }
