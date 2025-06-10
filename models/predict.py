from pathlib import Path
from datetime import datetime
import joblib
import numpy as np
from typing import List, Optional

class ModelPredictor:
    """Clase para manejar predicciones de diferentes modelos."""
    
    def __init__(self, producto_id: int):
        self.producto_id = producto_id
        self.models_path = Path("models/artifacts")
        
    def predict_all_models(self, dias_adelante: int) -> dict:
        """
        Realiza predicciones con todos los modelos disponibles.
        
        Args:
            dias_adelante: Número de días a predecir
            
        Returns:
            dict: Predicciones de cada modelo
        """
        predictions = {}
        
        # Buscar todos los modelos disponibles para este producto
        for model_path in self.models_path.glob(f"**/*producto_{self.producto_id}.pkl"):
            model_type = model_path.parent.name
            try:
                model = joblib.load(model_path)
                preds = self._generate_predictions(model, dias_adelante)
                predictions[model_type] = preds
            except Exception as e:
                print(f"Error al cargar modelo {model_type}: {e}")
                
        return predictions
    
    def _generate_predictions(self, model, dias_adelante: int) -> List[float]:
        """Genera predicciones para días futuros."""
        start = datetime.now().toordinal()
        X_future = [[start + i] for i in range(1, dias_adelante + 1)]
        return model.predict(X_future).tolist()