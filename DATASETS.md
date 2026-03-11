# Datasets Recomanats per Viora

## Radiografies de Tòrax (Gratuïts)

### 1. ChestX-ray14 (NIH)
- **Imatges**: 112,120 radiografies
- **Patologies**: 14 categories diferents
- **Link**: https://nihcc.app.box.com/v/ChestXray-NIHCC
- **Ús**: Ideal per començar, molt utilitzat en recerca

### 2. CheXpert (Stanford)
- **Imatges**: 224,316 radiografies
- **Patologies**: 14 observacions
- **Link**: https://stanfordmlgroup.github.io/competitions/chexpert/
- **Ús**: Dataset d'alta qualitat, excel·lent per producció

### 3. MIMIC-CXR
- **Imatges**: 377,110 radiografies
- **Patologies**: Múltiples amb informes mèdics
- **Link**: https://physionet.org/content/mimic-cxr/2.0.0/
- **Ús**: Dataset més complet, requereix registre

### 4. RSNA Pneumonia Detection (Kaggle)
- **Imatges**: ~30,000 radiografies
- **Patologies**: Pneumònia
- **Link**: https://www.kaggle.com/c/rsna-pneumonia-detection-challenge
- **Ús**: Específic per pneumònia, fàcil d'usar

### 5. COVID-19 Radiography Database
- **Imatges**: ~21,000 radiografies
- **Patologies**: COVID-19, pneumònia viral/bacteriana, normal
- **Link**: https://www.kaggle.com/datasets/tawsifurrahman/covid19-radiography-database
- **Ús**: Actualitzat amb casos COVID

## Analítiques de Sang

### Datasets sintètics i reals:

1. **UCI Machine Learning Repository**
   - Diversos datasets mèdics amb paràmetres de sang
   - https://archive.ics.uci.edu/ml/index.php

2. **Kaggle Medical Datasets**
   - Blood Test Results
   - https://www.kaggle.com/datasets

3. **MIMIC-III Clinical Database**
   - Dades clíniques reals (requereix certificació)
   - https://physionet.org/content/mimiciii/

## Com Descarregar i Preparar

```bash
# Crear estructura de directoris
mkdir -p data/chest_xray/{train,val,test}
mkdir -p data/blood_tests

# Exemple: Descarregar ChestX-ray14
# 1. Registra't a: https://nihcc.app.box.com/v/ChestXray-NIHCC
# 2. Descarrega els arxius
# 3. Organitza en train/val/test (70/15/15)

# Exemple: Kaggle dataset
pip install kaggle
kaggle datasets download -d tawsifurrahman/covid19-radiography-database
unzip covid19-radiography-database.zip -d data/chest_xray/
```

## Preprocessament Recomanat

```python
# Organitzar dataset en estructura esperada
data/
├── chest_xray/
│   ├── train/
│   │   ├── Normal/
│   │   ├── Pneumonia/
│   │   ├── Cardiomegaly/
│   │   └── ...
│   ├── val/
│   └── test/
└── blood_tests/
    └── samples.csv
```

## Notes Importants

- Alguns datasets requereixen registre i acceptació de termes d'ús
- Respecta sempre les llicències i l'ús ètic de dades mèdiques
- No comparteixis dades de pacients reals sense autorització
- Utilitza datasets anonimitzats per desenvolupament
