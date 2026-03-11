"""
Script automatitzat per descarregar i organitzar datasets
"""

import os
import zipfile
import shutil
from pathlib import Path
import urllib.request
from tqdm import tqdm

class DownloadProgress:
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar = tqdm(total=total_size, unit='B', unit_scale=True)
        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(block_size)
        else:
            self.pbar.close()

def download_sample_dataset():
    """
    Descarrega un dataset petit de mostra per proves
    """
    print("📥 Descarregant dataset de mostra...")
    
    # Crear directoris
    base_dir = Path("data/chest_xray")
    for split in ['train', 'val', 'test']:
        for category in ['Normal', 'Pneumonia']:
            (base_dir / split / category).mkdir(parents=True, exist_ok=True)
    
    print("✅ Estructura de directoris creada")
    
    # URLs de datasets públics petits
    sample_urls = {
        'kaggle': 'https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia',
        'github': 'https://github.com/ieee8023/covid-chestxray-dataset'
    }
    
    print("\n📋 Opcions de datasets:")
    print("1. Kaggle Pneumonia Dataset (recomanat per començar)")
    print("2. COVID-19 Chest X-ray Dataset")
    print("3. Manual (ja tinc el dataset descarregat)")
    
    choice = input("\nTria una opció (1-3): ")
    
    if choice == "1":
        print("\n📌 Per descarregar de Kaggle:")
        print("1. Instal·la: pip install kaggle")
        print("2. Configura credencials: https://www.kaggle.com/docs/api")
        print("3. Executa: kaggle datasets download -d paultimothymooney/chest-xray-pneumonia")
        print("4. Descomprimeix a: data/chest_xray/")
        
    elif choice == "2":
        print("\n📌 Per descarregar COVID dataset:")
        print("git clone https://github.com/ieee8023/covid-chestxray-dataset.git data/covid_dataset")
        
    elif choice == "3":
        print("\n📁 Col·loca les imatges en aquesta estructura:")
        print("data/chest_xray/")
        print("  ├── train/")
        print("  │   ├── Normal/")
        print("  │   └── Pneumonia/")
        print("  ├── val/")
        print("  └── test/")
    
    print("\n✅ Instruccions mostrades!")

def organize_dataset(source_dir: str):
    """
    Organitza un dataset descarregat en l'estructura correcta
    """
    source = Path(source_dir)
    target = Path("data/chest_xray")
    
    print(f"📂 Organitzant dataset de {source} a {target}")
    
    # Buscar imatges
    image_extensions = ['.jpg', '.jpeg', '.png']
    images = []
    
    for ext in image_extensions:
        images.extend(source.rglob(f'*{ext}'))
    
    print(f"🖼️  Trobades {len(images)} imatges")
    
    # Distribuir en train/val/test (70/15/15)
    from sklearn.model_selection import train_test_split
    
    train_imgs, temp_imgs = train_test_split(images, test_size=0.3, random_state=42)
    val_imgs, test_imgs = train_test_split(temp_imgs, test_size=0.5, random_state=42)
    
    splits = {
        'train': train_imgs,
        'val': val_imgs,
        'test': test_imgs
    }
    
    for split_name, img_list in splits.items():
        print(f"\n📋 Processant {split_name}: {len(img_list)} imatges")
        
        for img_path in tqdm(img_list):
            # Determinar categoria (Normal o Pneumonia) del nom del fitxer
            if 'normal' in img_path.name.lower():
                category = 'Normal'
            else:
                category = 'Pneumonia'
            
            # Copiar imatge
            dest = target / split_name / category / img_path.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(img_path, dest)
    
    print("\n✅ Dataset organitzat correctament!")

def verify_dataset():
    """
    Verifica que el dataset està ben organitzat
    """
    base_dir = Path("data/chest_xray")
    
    print("🔍 Verificant estructura del dataset...\n")
    
    total_images = 0
    for split in ['train', 'val', 'test']:
        print(f"📁 {split}/")
        for category in ['Normal', 'Pneumonia']:
            path = base_dir / split / category
            if path.exists():
                count = len(list(path.glob('*.jpg'))) + len(list(path.glob('*.jpeg'))) + len(list(path.glob('*.png')))
                print(f"   └── {category}: {count} imatges")
                total_images += count
            else:
                print(f"   └── {category}: ❌ No existeix")
    
    print(f"\n📊 Total: {total_images} imatges")
    
    if total_images > 0:
        print("✅ Dataset verificat correctament!")
        return True
    else:
        print("❌ No s'han trobat imatges. Revisa la configuració.")
        return False

if __name__ == "__main__":
    print("🏥 Viora - Gestor de Datasets\n")
    print("1. Descarregar dataset de mostra")
    print("2. Organitzar dataset existent")
    print("3. Verificar dataset")
    
    choice = input("\nTria una opció (1-3): ")
    
    if choice == "1":
        download_sample_dataset()
    elif choice == "2":
        source = input("Ruta del dataset descarregat: ")
        organize_dataset(source)
    elif choice == "3":
        verify_dataset()
