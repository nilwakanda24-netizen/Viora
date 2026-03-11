import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
from typing import Dict, Tuple

class ChestXRayModel:
    """Model CNN per analitzar radiografies de tòrax"""
    
    def __init__(self, input_shape=(224, 224, 3)):
        self.input_shape = input_shape
        self.model = self._build_model()
        self.conditions = [
            'Normal',
            'Pneumonia',
            'Cardiomegaly',
            'Pulmonary_Nodules',
            'Pulmonary_Edema',
            'Tuberculosis',
            'Other_Abnormalities'
        ]
    
    def _build_model(self) -> models.Model:
        """Construeix arquitectura CNN"""
        model = models.Sequential([
            # Block 1
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Block 2
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Block 3
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Block 4
            layers.Conv2D(256, (3, 3), activation='relu'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Dense layers
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.5),
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(len(self.conditions), activation='softmax')
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocessa imatge per al model"""
        img = tf.keras.preprocessing.image.load_img(
            image_path, 
            target_size=self.input_shape[:2]
        )
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = img_array / 255.0
        return np.expand_dims(img_array, axis=0)
    
    def predict(self, image_path: str) -> Dict:
        """Prediu condició a partir de radiografia"""
        processed_img = self.preprocess_image(image_path)
        predictions = self.model.predict(processed_img)[0]
        
        predicted_idx = np.argmax(predictions)
        confidence = float(predictions[predicted_idx])
        
        return {
            'condition': self.conditions[predicted_idx],
            'confidence': confidence,
            'all_probabilities': {
                condition: float(prob) 
                for condition, prob in zip(self.conditions, predictions)
            }
        }
