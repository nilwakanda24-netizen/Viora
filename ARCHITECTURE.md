# Arquitectura del Sistema Viora

## Visió General

Viora utilitza una arquitectura d'IA multimodal que combina:
1. Computer Vision (CNN) per radiografies
2. Machine Learning (Random Forest) per analítiques
3. Model de fusió per combinar prediccions

```
┌─────────────────┐         ┌──────────────────┐
│  Radiografia    │         │  Analítica Sang  │
│   (Imatge)      │         │     (JSON)       │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         ▼                           ▼
┌─────────────────┐         ┌──────────────────┐
│  CNN Model      │         │  RF/XGBoost      │
│  (TensorFlow)   │         │  (Scikit-learn)  │
└────────┬────────┘         └────────┬─────────┘
         │                           │
         │    ┌──────────────┐       │
         └───►│ Fusion Model │◄──────┘
              └──────┬───────┘
                     │
                     ▼
              ┌─────────────┐
              │   Informe   │
              │   Mèdic     │
              └─────────────┘
```

## Components Principals

### 1. ChestXRayModel (CNN)

Arquitectura basada en convolucions profundes:

```
Input (224x224x3)
    ↓
Conv2D(32) + BatchNorm + MaxPool
    ↓
Conv2D(64) + BatchNorm + MaxPool
    ↓
Conv2D(128) + BatchNorm + MaxPool
    ↓
Conv2D(256) + BatchNorm + MaxPool
    ↓
Flatten → Dense(512) → Dropout(0.5)
    ↓
Dense(256) → Dropout(0.3)
    ↓
Dense(7) → Softmax
```

Detecta:
- Pneumònia
- Cardiomegàlia
- Nòduls pulmonars
- Edema pulmonar
- Tuberculosi
- Altres anomalies

### 2. BloodAnalysisModel (ML)

Random Forest amb 10 features:
- Hemoglobina
- Glòbuls blancs
- Plaquetes
- PCR
- Colesterol
- Glucosa
- Ferritina
- ALT/AST
- Creatinina

Classifica:
- Normal
- Anèmia
- Infecció
- Inflamació
- Trastorn metabòlic

### 3. MultimodalFusion

Combina prediccions amb:
- Weighted averaging basat en confiança
- Regles clíniques per risc
- Generació de recomanacions contextuals

## Pipeline de Processament

```python
# 1. Preprocessament
xray_img = preprocess_image(xray_path)
blood_features = normalize_blood_data(blood_dict)

# 2. Predicció individual
xray_pred = cnn_model.predict(xray_img)
blood_pred = rf_model.predict(blood_features)

# 3. Fusió
final_result = fusion_model.combine(xray_pred, blood_pred)

# 4. Generació d'informe
report = generate_medical_report(final_result)
```

## Millores Futures

### Curt Termini
- Transfer learning amb models pre-entrenats (ResNet, EfficientNet)
- Augmentació de dades més sofisticada
- Validació creuada k-fold

### Mitjà Termini
- Attention mechanisms per explicabilitat
- Grad-CAM per visualitzar regions d'interès
- Integració amb més biomarcadors

### Llarg Termini
- Transformers multimodals (ViT + BERT)
- Federated learning per privacitat
- Integració amb sistemes hospitalaris (HL7/FHIR)

## Comparació amb Sistemes Reals

Hospitals i startups utilitzen arquitectures similars:

| Component | Viora | Sistemes Hospitalaris |
|-----------|-------|----------------------|
| CNN | Custom CNN | ResNet-50/DenseNet |
| Fusió | Rule-based | Deep fusion networks |
| Explicabilitat | Basic | Grad-CAM + SHAP |
| Validació | Offline | Clinical trials |

## Referències

- CheXNet (Stanford): https://arxiv.org/abs/1711.05225
- CheXpert: https://arxiv.org/abs/1901.07031
- Multimodal Medical AI: https://arxiv.org/abs/2010.00747
