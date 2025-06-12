import os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
from ..utils.data_processing import obtener_datos_enriquecidos

class ModeloLineal:
    """Modelo de regresión lineal mejorado para predicción de ventas."""
    
    def __init__(self, producto_id: int):
        self.producto_id = producto_id
        self.model_path = Path(f"models/artifacts/linear/producto_{producto_id}.pkl")
        self.scaler_path = Path(f"models/artifacts/linear/scaler_{producto_id}.pkl")
        self.model = None
        self.scaler = StandardScaler()
        
        # Features para el modelo
        self.features_base = [
            'dia_semana', 'mes', 'precio_base', 
            'stock_actual', 'precio_proveedor_promedio'
        ]
        
        self.features_calculados = [
            'ventas_7_dias', 'ventas_30_dias',
            'margen', 'variacion_precio'
        ]
        
    def train(self, usar_ridge=True, alpha=1.0) -> dict:
        """
        Entrena el modelo con validación cruzada temporal.
        
        Args:
            usar_ridge: Si True usa Ridge regression, sino Linear regression
            alpha: Parámetro de regularización para Ridge
            
        Returns:
            dict: Métricas de rendimiento
        """
        # Obtener datos
        data = obtener_datos_enriquecidos(self.producto_id)
        if data.empty:
            print(f"No hay datos suficientes para producto {self.producto_id}")
            return None
            
        # Preparar features
        X = data[self.features_base + self.features_calculados]
        y = data['cantidad_vendida']
        
        # Escalar features
        X_scaled = self.scaler.fit_transform(X)
        
        # Validación cruzada temporal
        tscv = TimeSeriesSplit(n_splits=5)
        metrics = {
            'r2_scores': [],
            'mae_scores': [],
            'rmse_scores': []
        }
        
        # Seleccionar modelo
        self.model = Ridge(alpha=alpha) if usar_ridge else LinearRegression()
        
        # Entrenamiento con validación cruzada
        for train_idx, test_idx in tscv.split(X_scaled):
            X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            
            metrics['r2_scores'].append(r2_score(y_test, y_pred))
            metrics['mae_scores'].append(mean_absolute_error(y_test, y_pred))
            metrics['rmse_scores'].append(np.sqrt(mean_squared_error(y_test, y_pred)))
        
        # Entrenar modelo final con todos los datos
        self.model.fit(X_scaled, y)
        
        # Guardar modelo y scaler
        os.makedirs(self.model_path.parent, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        # Calcular importancia de features
        importancia = pd.DataFrame({
            'feature': self.features_base + self.features_calculados,
            'importancia': np.abs(self.model.coef_)
        }).sort_values('importancia', ascending=False)
        
        return {
            'metricas': {
                'r2_medio': np.mean(metrics['r2_scores']),
                'mae_medio': np.mean(metrics['mae_scores']),
                'rmse_medio': np.mean(metrics['rmse_scores'])
            },
            'importancia_features': importancia.to_dict('records')
        }