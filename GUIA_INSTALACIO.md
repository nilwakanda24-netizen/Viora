# 🚀 Guia Pas a Pas - Viora AI Medical Screening

## Prerequisits

Abans de començar, assegura't de tenir instal·lat:
- Python 3.9 o superior
- pip (gestor de paquets Python)

Comprova les versions:
```bash
python --version
pip --version
```

**Opcional (només si vols usar React):**
- Node.js 16 o superior (gratuït: https://nodejs.org/)
- npm (ve inclòs amb Node.js)

**Nota:** Node.js és completament gratuït i open source. No cal pagar res!

---

## Pas 1: Instal·lar Dependencies Python

### 1.1 Crear entorn virtual (recomanat)

```bash
# Crear entorn virtual
python -m venv venv

# Activar entorn virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 1.2 Instal·lar paquets

```bash
pip install -r requirements.txt
```

Això instal·larà:
- TensorFlow (deep learning)
- PyTorch (deep learning alternatiu)
- FastAPI (API backend)
- Scikit-learn (machine learning)
- OpenCV (processament d'imatges)
- I altres dependencies

⏱️ Temps estimat: 5-10 minuts

---

## Pas 2: Descarregar Dataset

### Opció A: Dataset Petit per Proves (Recomanat per començar)

**RSNA Pneumonia Detection Challenge** (Kaggle)

```bash
# 1. Instal·lar Kaggle CLI
pip install kaggle

# 2. Configurar credencials Kaggle
# - Ves a https://www.kaggle.com/settings
# - Crea un API token (descarregarà kaggle.json)
# - Col·loca kaggle.json a:
#   Windows: C:\Users\<username>\.kaggle\kaggle.json
#   macOS/Linux: ~/.kaggle/kaggle.json

# 3. Descarregar dataset
kaggle datasets download -d paultimothymooney/chest-xray-pneumonia
```

### Opció B: Dataset Gran per Producció

**ChestX-ray14 (NIH)**

1. Registra't a: https://nihcc.app.box.com/v/ChestXray-NIHCC
2. Descarrega els arxius (són grans, ~45GB)
3. Extreu els arxius

### 2.1 Organitzar Dataset

```bash
# Crear estructura de directoris
mkdir -p data/chest_xray/train/Normal
mkdir -p data/chest_xray/train/Pneumonia
mkdir -p data/chest_xray/train/Cardiomegaly
mkdir -p data/chest_xray/val/Normal
mkdir -p data/chest_xray/val/Pneumonia
mkdir -p data/chest_xray/val/Cardiomegaly
mkdir -p data/chest_xray/test/Normal
mkdir -p data/chest_xray/test/Pneumonia
mkdir -p data/chest_xray/test/Cardiomegaly
```

### 2.2 Extreure i Organitzar

```bash
# Si has descarregat el dataset de Kaggle
unzip chest-xray-pneumonia.zip -d data/

# El dataset ja vindrà organitzat en train/test/val
# Només cal moure'l a la ubicació correcta
mv data/chest_xray_pneumonia/* data/chest_xray/
```

⏱️ Temps estimat: 10-30 minuts (depèn de la mida del dataset)

---

## Pas 3: Entrenar el Model

### 3.1 Verificar estructura de dades

```bash
# Comprovar que les carpetes existeixen
ls data/chest_xray/train/
ls data/chest_xray/val/
```

Hauries de veure carpetes com: Normal, Pneumonia, etc.

### 3.2 Executar entrenament

```bash
python train_model.py
```

Això farà:
- Carregar les imatges
- Aplicar data augmentation
- Entrenar el model CNN
- Guardar el millor model a `models/saved/`

⏱️ Temps estimat: 
- Amb GPU: 30-60 minuts
- Sense GPU: 2-4 hores

### 3.3 Monitoritzar entrenament

Veuràs sortida com:
```
Epoch 1/50
100/100 [==============================] - 45s 450ms/step - loss: 0.5234 - accuracy: 0.7456 - val_loss: 0.4123 - val_accuracy: 0.8234
Epoch 2/50
...
```

---

## Pas 4: Iniciar API Backend

### 4.1 Executar servidor FastAPI

```bash
python api/main.py
```

O amb uvicorn directament:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 4.2 Verificar que funciona

Obre el navegador i ves a:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/

Hauries de veure la documentació interactiva de l'API.

⏱️ L'API estarà llesta en segons

---

## Pas 5: Iniciar Frontend

### Opció A: Frontend Simple (RECOMANAT - sense Node.js)

```bash
python frontend_simple.py
```

Això iniciarà:
- ✅ API backend
- ✅ Frontend web integrat
- ✅ Tot en un sol servidor

Obre el navegador a: http://localhost:8000

⏱️ Temps estimat: 5 segons

### Opció B: Frontend React (requereix Node.js)

Si prefereixes React i tens Node.js instal·lat:

```bash
cd frontend
npm install
npm start
```

Això obrirà automàticament el navegador a http://localhost:3000

⏱️ Temps estimat: 2-3 minuts

**Nota:** Node.js és gratuït i open source. Pots descarregar-lo de https://nodejs.org/

---

## Pas 6: Provar el Sistema

### 6.1 Preparar dades de prova

Crea un fitxer de prova o utilitza una imatge del dataset:

```bash
# Copiar una imatge de prova
cp data/chest_xray/test/Pneumonia/person1_virus_6.jpeg test_xray.jpg
```

### 6.2 Provar amb l'API directament

```bash
curl -X POST "http://localhost:8000/analyze/blood" \
  -H "Content-Type: application/json" \
  -d '{
    "hemoglobin": 11.2,
    "white_blood_cells": 14000,
    "platelets": 250000,
    "crp": 15,
    "cholesterol": 210,
    "glucose": 110
  }'
```

### 6.3 Provar amb la interfície web

1. Ves a http://localhost:3000
2. Puja una radiografia de tòrax
3. Introdueix valors d'analítica de sang
4. Clica "Analitzar"
5. Veuràs els resultats amb:
   - Possible condició
   - Nivell de risc
   - Evidències
   - Recomanacions

---

## Pas 7: Exemple d'Ús amb Script Python

```bash
python example_usage.py
```

Això executarà un exemple complet mostrant:
- Anàlisi de radiografia
- Anàlisi d'analítica
- Fusió de resultats
- Informe final

---

## Troubleshooting

### Error: "No module named 'tensorflow'"
```bash
pip install tensorflow
```

### Error: "CUDA not available"
TensorFlow funcionarà amb CPU, però més lent. Per usar GPU:
```bash
pip install tensorflow-gpu
```

### Error: "Port 8000 already in use"
```bash
# Canvia el port a l'arxiu api/main.py
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Error: "Cannot find module 'react'"
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### El model no entrena bé
- Comprova que tens prou dades (mínim 1000 imatges per classe)
- Augmenta el nombre d'epochs
- Ajusta el learning rate
- Prova amb transfer learning (ResNet, EfficientNet)

---

## Estructura Final

Després de completar tots els passos:

```
viora/
├── venv/                      # Entorn virtual
├── data/
│   └── chest_xray/
│       ├── train/            # Imatges d'entrenament
│       ├── val/              # Imatges de validació
│       └── test/             # Imatges de test
├── models/
│   └── saved/
│       ├── chest_xray_best.h5    # Millor model
│       └── chest_xray_final.h5   # Model final
├── frontend/
│   └── node_modules/         # Dependencies React
└── [altres arxius del projecte]
```

---

## Següents Passos Recomanats

### Millores Immediates
1. Afegir més classes de patologies
2. Implementar Grad-CAM per visualitzar regions d'interès
3. Afegir validació de dades d'entrada
4. Crear tests unitaris

### Millores Avançades
1. Transfer learning amb ResNet o EfficientNet
2. Implementar attention mechanisms
3. Afegir base de dades per guardar historial
4. Crear dashboard d'administració
5. Implementar autenticació d'usuaris

### Desplegament
1. Dockeritzar l'aplicació
2. Desplegar a AWS/GCP/Azure
3. Configurar CI/CD
4. Implementar monitorització

---

## Recursos Addicionals

- **Documentació TensorFlow**: https://www.tensorflow.org/tutorials
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **Papers d'IA Mèdica**: https://arxiv.org/list/cs.CV/recent

---

## Suport

Si tens problemes:
1. Revisa la secció Troubleshooting
2. Comprova els logs de l'API i frontend
3. Verifica que tots els prerequisits estan instal·lats
4. Assegura't que les rutes dels arxius són correctes

---

**⚠️ Recordatori Important**: Aquest és un sistema de suport clínic per a fins educatius i de recerca. NO utilitzar per diagnòstics mèdics reals sense validació clínica adequada i aprovació regulatòria.
