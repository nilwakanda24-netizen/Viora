import tensorflow as tf
from pathlib import Path
from typing import Tuple, List
import numpy as np

class DatasetLoader:
    """Carrega i preprocessa datasets per entrenament"""
    
    def __init__(self, data_dir: str, img_size: Tuple[int, int] = (224, 224)):
        self.data_dir = Path(data_dir)
        self.img_size = img_size
    
    def load_chest_xray_dataset(self, batch_size: int = 32) -> Tuple:
        """
        Carrega dataset de radiografies
        
        Datasets recomanats:
        - ChestX-ray14: https://nihcc.app.box.com/v/ChestXray-NIHCC
        - CheXpert: https://stanfordmlgroup.github.io/competitions/chexpert/
        - MIMIC-CXR: https://physionet.org/content/mimic-cxr/2.0.0/
        """
        train_ds = tf.keras.preprocessing.image_dataset_from_directory(
            self.data_dir / 'train',
            image_size=self.img_size,
            batch_size=batch_size,
            label_mode='categorical'
        )
        
        val_ds = tf.keras.preprocessing.image_dataset_from_directory(
            self.data_dir / 'val',
            image_size=self.img_size,
            batch_size=batch_size,
            label_mode='categorical'
        )
        
        # Normalització
        normalization_layer = tf.keras.layers.Rescaling(1./255)
        train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
        val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))
        
        # Optimització
        train_ds = train_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
        val_ds = val_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
        
        return train_ds, val_ds
    
    def augment_data(self, dataset):
        """Aplica data augmentation"""
        data_augmentation = tf.keras.Sequential([
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.1),
            tf.keras.layers.RandomZoom(0.1),
        ])
        
        return dataset.map(
            lambda x, y: (data_augmentation(x, training=True), y)
        )
