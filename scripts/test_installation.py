"""
Script per verificar que tot està instal·lat correctament
"""

import sys
from pathlib import Path

def check_python_version():
    """Verifica versió de Python"""
    version = sys.version_info
    print(f"🐍 Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 9:
        print("   ✅ Versió correcta (>= 3.9)")
        return True
    else:
        print("   ❌ Necessites Python 3.9 o superior")
        return False

def check_packages():
    """Verifica paquets instal·lats"""
    packages = {
        'tensorflow': 'TensorFlow',
        'torch': 'PyTorch',
        'fastapi': 'FastAPI',
        'sklearn': 'Scikit-learn',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'PIL': 'Pillow'
    }
    
    print("\n📦 Verificant paquets:")
    all_ok = True
    
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - Executa: pip install {package}")
            all_ok = False
    
    return all_ok

def check_directory_structure():
    """Verifica estructura de directoris"""
    print("\n📁 Verificant estructura:")
    
    required_dirs = [
        'models',
        'api',
        'utils',
        'data',
        'frontend'
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        path = Path(dir_name)
        if path.exists():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ - Falta aquest directori")
            all_ok = False
    
    return all_ok

def check_dataset():
    """Verifica si hi ha dataset"""
    print("\n🖼️  Verificant dataset:")
    
    data_dir = Path("data/chest_xray")
    if not data_dir.exists():
        print("   ⚠️  No s'ha trobat dataset")
        print("   💡 Executa: python scripts/download_dataset.py")
        return False
    
    total = 0
    for split in ['train', 'val', 'test']:
        split_dir = data_dir / split
        if split_dir.exists():
            count = len(list(split_dir.rglob('*.jpg'))) + len(list(split_dir.rglob('*.png')))
            total += count
            print(f"   ✅ {split}: {count} imatges")
    
    if total > 0:
        print(f"   ✅ Total: {total} imatges")
        return True
    else:
        print("   ⚠️  Dataset buit")
        return False

def check_models():
    """Verifica si hi ha models entrenats"""
    print("\n🤖 Verificant models:")
    
    models_dir = Path("models/saved")
    if not models_dir.exists():
        print("   ⚠️  No hi ha models entrenats")
        print("   💡 Executa: python train_model.py")
        return False
    
    model_files = list(models_dir.glob('*.h5'))
    if model_files:
        for model in model_files:
            print(f"   ✅ {model.name}")
        return True
    else:
        print("   ⚠️  No s'han trobat models")
        return False

def test_api_import():
    """Prova importar l'API"""
    print("\n🌐 Verificant API:")
    
    try:
        sys.path.append('.')
        from api.main import app
        print("   ✅ API importada correctament")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("="*60)
    print("🏥 VIORA - Test d'Instal·lació")
    print("="*60)
    
    results = {
        'Python': check_python_version(),
        'Paquets': check_packages(),
        'Estructura': check_directory_structure(),
        'Dataset': check_dataset(),
        'Models': check_models(),
        'API': test_api_import()
    }
    
    print("\n" + "="*60)
    print("📊 RESUM")
    print("="*60)
    
    for component, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {component}")
    
    all_ok = all(results.values())
    
    print("\n" + "="*60)
    if all_ok:
        print("🎉 Tot està correcte! Pots començar a usar Viora.")
        print("\nPròxims passos:")
        print("1. python api/main.py  # Iniciar API")
        print("2. cd frontend && npm start  # Iniciar frontend")
    else:
        print("⚠️  Hi ha alguns problemes. Revisa els errors anteriors.")
        print("\nConsells:")
        print("- Instal·la paquets: pip install -r requirements.txt")
        print("- Descarrega dataset: python scripts/download_dataset.py")
        print("- Entrena model: python train_model.py")
    print("="*60)

if __name__ == "__main__":
    main()
