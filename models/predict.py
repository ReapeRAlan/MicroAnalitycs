from pathlib import Path
from datetime import datetime, timedelta
import joblib
import numpy as np
from typing import List, Optional
from .utils.data_processing import obtener_datos_enriquecidos
import pandas as pd

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
        """Genera predicciones con todos los features"""
        # Obtener últimos valores conocidos
        ultimo_dato = obtener_datos_enriquecidos(self.producto_id).iloc[-1]
        # Agregar validación:
        data = obtener_datos_enriquecidos(self.producto_id)
        if data.empty:
            raise ValueError(f"No hay datos para el producto {self.producto_id}")
        
        # Generar fechas futuras
        start = datetime.now()
        fechas = [start + timedelta(days=i) for i in range(1, dias_adelante + 1)]
        
        # Crear features futuros
        X_future = pd.DataFrame([{
            'dia_semana': fecha.weekday(),
            'mes': fecha.month,
            'precio_base': ultimo_dato['precio_base'],
            'stock_actual': ultimo_dato['stock_actual'],
            'precio_proveedor_promedio': ultimo_dato['precio_proveedor_promedio'],
            'ventas_7_dias': 0,  # Usar últimos valores o predicciones previas
            'ventas_30_dias': 0,
            'margen': ultimo_dato['margen'],
            'variacion_precio': ultimo_dato['variacion_precio']
        } for fecha in fechas])
        
        return model.predict(X_future).tolist()