"""
Script per entrenar el model de radiografies

Datasets recomanats (gratuïts):
1. ChestX-ray14 (NIH): 112,120 imatges amb 14 patologies
   https://nihcc.app.box.com/v/ChestXray-NIHCC

2. CheXpert (Stanford): 224,316 imatges
   https://stanfordmlgroup.github.io/competitions/chexpert/

3. RSNA Pneumonia Detection: Kaggle dataset
   https://www.kaggle.com/c/rsna-pneumonia-detection-challenge
"""

from models.chest_xray_model import ChestXRayModel
from utils.data_loader import DatasetLoader
import tensorflow as tf

def train_xray_model(data_dir: str, epochs: int = 50):
    """Entrena model de radiografies"""
    
    # Carregar dades
    loader = DatasetLoader(data_dir)
    train_ds, val_ds = loader.load_chest_xray_dataset(batch_size=32)
    train_ds = loader.augment_data(train_ds)
    
    # Crear model
    model = ChestXRayModel()
    
    # Callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5
        ),
        tf.keras.callbacks.ModelCheckpoint(
            'models/saved/chest_xray_best.h5',
            monitor='val_accuracy',
            save_best_only=True
        )
    ]
    
    # Entrenar
    history = model.model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs,
        callbacks=callbacks
    )
    
    # Guardar model final
    model.model.save('models/saved/chest_xray_final.h5')
    
    return history

if __name__ == "__main__":
    # Configurar path al dataset
    DATA_DIR = "data/chest_xray"
    
    print("🚀 Iniciant entrenament del model...")
    print("📊 Dataset:", DATA_DIR)
    
    history = train_xray_model(DATA_DIR, epochs=50)
    
    print("✅ Entrenament completat!")
