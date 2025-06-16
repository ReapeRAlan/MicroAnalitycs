import os
from pathlib import Path
import joblib
from sklearn.linear_model import LinearRegression
from ..utils.data_processing import get_training_data

class LinearModel:
    """Modelo de regresión lineal para predicción de ventas."""
    
    def __init__(self, producto_id: int):
        self.producto_id = producto_id
        self.model_path = Path(f"models/artifacts/linear/producto_{producto_id}.pkl")
        self.model = None
    
    def train(self) -> bool:
        """
        Entrena el modelo con los datos históricos.
        Returns:
            bool: True si el entrenamiento fue exitoso
        """
        X, y = get_training_data(self.producto_id)
        if X is None:
            print(f"No hay datos suficientes para producto {self.producto_id}")
            return False
            
        # Entrenar modelo
        self.model = LinearRegression()
        self.model.fit(X, y)
        
        # Guardar modelo
        os.makedirs(self.model_path.parent, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"Modelo guardado en {self.model_path}")
        return True