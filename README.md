# Viora – AI Medical Screening System

Sistema d'intel·ligència artificial per analitzar radiografies de tòrax i resultats d'anàlisi de sang per detectar possibles patologies.

## ⚠️ Disclaimer Mèdic

Aquest sistema és una eina de suport clínic i NO substitueix el diagnòstic d'un metge professional. Sempre consulta amb personal mèdic qualificat.

## Característiques

- Anàlisi de radiografies de tòrax amb Computer Vision
- Processament de paràmetres d'analítica de sang
- Model multimodal que combina ambdues fonts
- Estimació de risc i recomanacions

## Estructura del Projecte

```
viora/
├── models/          # Models d'IA
├── api/             # FastAPI backend
├── frontend/        # React UI
├── data/            # Datasets i dades d'entrenament
└── utils/           # Utilitats i helpers
```

## Tecnologies

- Python 3.9+
- TensorFlow / PyTorch
- FastAPI
- React
- OpenCV
- Scikit-learn

## Instal·lació

### Opció 1: Quick Start (5 minuts)
```bash
# Veure QUICK_START.md per començar ràpidament
python scripts/test_installation.py
```

### Opció 2: Instal·lació Completa
```bash
# Veure GUIA_INSTALACIO.md per instruccions detallades pas a pas
pip install -r requirements.txt
python scripts/download_dataset.py
python train_model.py
```

## Ús

```bash
# Verificar instal·lació
python scripts/test_installation.py

# Opció 1: Tot en un (RECOMANAT - sense Node.js)
python frontend_simple.py

# Opció 2: API + Frontend separat
python api/main.py
cd frontend && npm start  # Requereix Node.js (gratuït)
```
