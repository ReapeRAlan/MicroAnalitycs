from typing import List, Tuple
import pandas as pd
import numpy as np
from backend.models.venta import Venta
from backend.database import SessionLocal

def get_training_data(producto_id: int) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Obtiene y preprocesa datos de entrenamiento para un producto específico.
    
    Args:
        producto_id: ID del producto a analizar
    
    Returns:
        Tuple con features (X) y target (y)
    """
    db = SessionLocal()
    try:
        ventas = db.query(Venta).filter(Venta.producto_id == producto_id).all()
        if not ventas:
            return None, None
            
        # Crear DataFrame base
        data = pd.DataFrame([
            {
                "fecha": v.fecha.toordinal(),
                "cantidad": v.cantidad,
                "dia_semana": v.fecha.weekday(),
                "mes": v.fecha.month
            } 
            for v in ventas
        ])
        
        # Features y target
        X = data[["fecha", "dia_semana", "mes"]]
        y = data["cantidad"]
        
        return X, y
    finally:
        db.close()