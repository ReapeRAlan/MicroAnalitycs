import os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
from ..utils.data_processing import obtener_datos_enriquecidos

class ModeloPolinomico:
    """Modelo de regresión polinómica para predicción de ventas."""
    
    def __init__(self, producto_id: int, grado: int = 2):
        self.producto_id = producto_id
        self.grado = grado
        self.model_path = Path(f"models/artifacts/polynomial/producto_{producto_id}_grado_{grado}.pkl")
        
        # Features para el modelo
        self.features_base = [
            'dia_semana', 'mes', 'precio_base', 
            'stock_actual', 'precio_proveedor_promedio'
        ]
        
        self.features_calculados = [
            'ventas_7_dias', 'ventas_30_dias',
            'margen', 'variacion_precio'
        ]
        
    def train(self, alpha: float = 1.0) -> dict:
        """
        Entrena el modelo polinómico con validación cruzada temporal.
        
        Args:
            alpha: Parámetro de regularización para Ridge
            
        Returns:
            dict: Métricas de rendimiento y coeficientes
        """
        # Obtener datos
        data = obtener_datos_enriquecidos(self.producto_id)
        if data.empty:
            print(f"No hay datos suficientes para producto {self.producto_id}")
            return None
            
        # Preparar features
        X = data[self.features_base + self.features_calculados]
        y = data['cantidad_vendida']
        
        # Crear pipeline con transformaciones
        self.model = make_pipeline(
            StandardScaler(),
            PolynomialFeatures(degree=self.grado, include_bias=False),
            Ridge(alpha=alpha)
        )
        
        # Validación cruzada temporal
        tscv = TimeSeriesSplit(n_splits=5)
        metrics = {
            'r2_scores': [],
            'mae_scores': [],
            'rmse_scores': []
        }
        
        # Entrenamiento con validación cruzada
        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict(X_test)
            
            metrics['r2_scores'].append(r2_score(y_test, y_pred))
            metrics['mae_scores'].append(mean_absolute_error(y_test, y_pred))
            metrics['rmse_scores'].append(np.sqrt(mean_squared_error(y_test, y_pred)))
        
        # Entrenar modelo final con todos los datos
        self.model.fit(X, y)
        
        # Guardar modelo
        os.makedirs(self.model_path.parent, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        
        # Obtener nombres de features polinómicos
        poly = self.model.named_steps['polynomialfeatures']
        feature_names = self._get_feature_names(poly, X.columns)
        
        # Obtener coeficientes del modelo
        coef = self.model.named_steps['ridge'].coef_
        importancia = pd.DataFrame({
            'feature': feature_names,
            'coeficiente': coef
        }).sort_values('coeficiente', key=abs, ascending=False)
        
        return {
            'metricas': {
                'r2_medio': np.mean(metrics['r2_scores']),
                'mae_medio': np.mean(metrics['mae_scores']),
                'rmse_medio': np.mean(metrics['rmse_scores'])
            },
            'coeficientes': importancia.to_dict('records')
        }
    
    def _get_feature_names(self, poly: PolynomialFeatures, input_features: list) -> list:
        """Genera nombres descriptivos para features polinómicos."""
        powers = poly.powers_
        feature_names = []
        
        for power in powers:
            current = []
            for feat, p in zip(input_features, power):
                if p == 0:
                    continue
                elif p == 1:
                    current.append(f"{feat}")
                else:
                    current.append(f"{feat}^{p}")
            name = " * ".join(current) if current else "1"
            feature_names.append(name)
            
        return feature_names