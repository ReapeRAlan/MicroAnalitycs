import os
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
import json

# Imports que pueden fallar se manejan con try/except
try:
    from sklearn.preprocessing import PolynomialFeatures, StandardScaler, RobustScaler
    from sklearn.pipeline import make_pipeline
    from sklearn.linear_model import Ridge, ElasticNet
    from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
    from sklearn.feature_selection import SelectKBest, f_regression
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn no está instalado. Instale con: pip install scikit-learn")

from ..utils.data_processing import obtener_datos_enriquecidos
from ..utils.logger import model_logger

warnings.filterwarnings('ignore')

# Clases de error personalizadas
class ModelTrainingError(Exception):
    """Error en el entrenamiento de modelos"""
    pass

# Decorador simple para manejo de errores
def handle_errors(error_type=Exception, default_return=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_type as e:
                print(f"Error en {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator

# Validador de datos simplificado
class SimpleDataValidator:
    """Validador simple de calidad de datos"""
    
    def __init__(self):
        self.required_columns = [
            'fecha', 'producto_id', 'cantidad_vendida', 
            'precio_base', 'stock_actual'
        ]
    
    def validate_data_quality(self, data: pd.DataFrame, producto_id: int) -> dict:
        """Valida calidad básica de datos"""
        issues = {}
        
        # Verificar columnas requeridas
        missing_cols = [col for col in self.required_columns if col not in data.columns]
        if missing_cols:
            issues['missing_columns'] = missing_cols
            issues['fatal_errors'] = True
        
        # Verificar valores faltantes críticos
        critical_missing = data[['cantidad_vendida', 'precio_base']].isnull().sum()
        if critical_missing.any():
            issues['critical_missing'] = critical_missing.to_dict()
        
        return issues

# Limpiador de datos simplificado
class SimpleDataCleaner:
    """Limpiador simple de datos"""
    
    def clean_data(self, data: pd.DataFrame, producto_id=None) -> pd.DataFrame:
        """Limpia datos básicos"""
        cleaned = data.copy()
        
        # Rellenar valores faltantes básicos
        if 'stock_actual' in cleaned.columns:
            cleaned['stock_actual'] = cleaned['stock_actual'].fillna(0)
        
        if 'precio_proveedor_promedio' in cleaned.columns:
            cleaned['precio_proveedor_promedio'] = cleaned['precio_proveedor_promedio'].fillna(
                cleaned['precio_base']
            )
        
        # Eliminar filas con valores críticos faltantes
        cleaned = cleaned.dropna(subset=['cantidad_vendida', 'precio_base'])
        
        return cleaned

class ModeloPolinomicoMejorado:
    """Modelo de regresión polinómica mejorado para predicción de ventas."""
    
    def __init__(self, producto_id: int, grado: int = 2):
        self.producto_id = producto_id
        self.grado = grado
        self.model_path = Path(f"models/artifacts/polynomial/producto_{producto_id}_grado_{grado}.pkl")
        self.metrics_path = Path(f"models/metrics/polynomial_metrics_{producto_id}_{grado}.json")
        self.model = None
        self.feature_selector = None
        
        # Features para el modelo
        self.features_base = [
            'dia_semana', 'mes', 'precio_base', 
            'stock_actual', 'precio_proveedor_promedio'
        ]
        
        self.features_calculados = [
            'ventas_7_dias', 'ventas_30_dias',
            'margen', 'variacion_precio',
            'tendencia_30_dias', 'estacionalidad',
            'precio_competencia', 'promocion_activa'
        ]
        
        # Configuraciones de hiperparámetros
        self.param_grid = {
            'ridge__alpha': [0.1, 1.0, 10.0, 100.0],
            'polynomialfeatures__degree': [2, 3, 4] if grado == 'auto' else [grado]
        }
    
    @handle_errors(ModelTrainingError, default_return=None)
    def train_with_validation(self, use_feature_selection=True, cross_validate=True) -> dict:
        """
        Entrena el modelo polinómico con validación de calidad y optimización automática.
        
        Args:
            use_feature_selection: Si aplicar selección de features
            cross_validate: Si usar validación cruzada para hiperparámetros
            
        Returns:
            dict: Métricas de rendimiento y información del modelo
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'scikit-learn no disponible'}
        
        print(f"Iniciando entrenamiento polinómico para producto {self.producto_id}")
        
        # 1. Obtener y validar datos
        data = self._get_validated_data()
        if data is None or data.empty:
            raise ModelTrainingError(f"No hay datos válidos para producto {self.producto_id}")
        
        # 2. Preparar features con manejo de datos faltantes
        X, y = self._prepare_features(data, use_feature_selection)
        
        # 3. Crear y optimizar modelo polinómico
        self._create_optimized_model(X, y, cross_validate)
        
        # 4. Entrenamiento final y evaluación
        metrics = self._train_and_evaluate(X, y)
        
        # 5. Guardar artefactos
        self._save_artifacts()
        
        print(f"Entrenamiento polinómico completado para producto {self.producto_id}")
        return metrics
    
    def _get_validated_data(self) -> pd.DataFrame:
        """Obtiene y valida los datos con limpieza automática."""
        # Obtener datos
        data = obtener_datos_enriquecidos(self.producto_id)
        
        if data.empty:
            print(f"No hay datos para producto {self.producto_id}")
            return pd.DataFrame()
        
        # Validar calidad de datos
        validator = SimpleDataValidator()
        validation_result = validator.validate_data_quality(data, self.producto_id)
        
        if validation_result.get('fatal_errors'):
            print(f"Errores fatales en datos: {validation_result.get('fatal_errors')}")
            return pd.DataFrame()
        
        # Limpiar datos automáticamente
        cleaner = SimpleDataCleaner()
        cleaned_data = cleaner.clean_data(data, self.producto_id)
        
        # Actualizar features históricos si hay datos faltantes
        cleaned_data = self._update_historical_features(cleaned_data)
        
        print(f"Datos validados y limpiados: {len(cleaned_data)} registros")
        return cleaned_data
    
    def _update_historical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Actualiza y corrige features históricos."""
        try:
            # Asegurar orden temporal
            data = data.sort_values('fecha')
            
            # Recalcular features históricos si están faltantes
            if 'ventas_7_dias' not in data.columns or data['ventas_7_dias'].isna().any():
                data['ventas_7_dias'] = data['cantidad_vendida'].rolling(window=7, min_periods=1).mean()
            
            if 'ventas_30_dias' not in data.columns or data['ventas_30_dias'].isna().any():
                data['ventas_30_dias'] = data['cantidad_vendida'].rolling(window=30, min_periods=1).mean()
            
            if 'tendencia_30_dias' not in data.columns:
                # Calcular tendencia como la pendiente de los últimos 30 días
                def calculate_trend(series):
                    if len(series) < 2:
                        return 0
                    x = np.arange(len(series))
                    return np.polyfit(x, series, 1)[0]
                
                data['tendencia_30_dias'] = data['cantidad_vendida'].rolling(
                    window=30, min_periods=2
                ).apply(calculate_trend)
            
            # Rellenar valores faltantes con métodos apropiados
            data['estacionalidad'] = data.get('estacionalidad', 1.0)
            data['precio_competencia'] = data.get('precio_competencia', data['precio_base'])
            data['promocion_activa'] = data.get('promocion_activa', 0)
            
            return data
            
        except Exception as e:
            print(f"Error actualizando features históricos: {e}")
            return data
    
    def _prepare_features(self, data: pd.DataFrame, use_feature_selection: bool) -> tuple:
        """Prepara features con escalado robusto y selección automática."""
        # Combinar todas las features
        all_features = self.features_base + self.features_calculados
        available_features = [f for f in all_features if f in data.columns]
        
        X = data[available_features].copy()
        y = data['cantidad_vendida'].copy()
        
        # Manejar valores faltantes
        X = X.fillna(X.median())
        
        # Selección de features si está habilitada y hay suficientes features
        if use_feature_selection and len(available_features) > 5:
            if SKLEARN_AVAILABLE:
                k_features = min(8, len(available_features))  # Menos features para polinómicos
                self.feature_selector = SelectKBest(score_func=f_regression, k=k_features)
                X_selected = self.feature_selector.fit_transform(X, y)
                
                # Obtener nombres de features seleccionadas
                selected_indices = self.feature_selector.get_support(indices=True)
                selected_features = [available_features[i] for i in selected_indices]
                X = pd.DataFrame(X_selected, columns=selected_features, index=X.index)
                
                print(f"Features seleccionadas para modelo polinómico: {selected_features}")
        
        return X, y
    
    def _create_optimized_model(self, X: pd.DataFrame, y: pd.Series, cross_validate: bool):
        """Crea modelo polinómico optimizado."""
        if not SKLEARN_AVAILABLE:
            return
        
        # Crear pipeline base
        base_pipeline = make_pipeline(
            RobustScaler(),  # Escalado robusto
            PolynomialFeatures(degree=self.grado, include_bias=False, interaction_only=False),
            Ridge(alpha=1.0)
        )
        
        if cross_validate and len(X) > 50:  # Solo si hay suficientes datos
            try:
                # Optimización de hiperparámetros
                grid_search = GridSearchCV(
                    base_pipeline,
                    self.param_grid,
                    cv=TimeSeriesSplit(n_splits=3),
                    scoring='r2',
                    n_jobs=-1
                )
                grid_search.fit(X, y)
                self.model = grid_search.best_estimator_
                
                print(f"Mejores parámetros: {grid_search.best_params_}")
                print(f"Mejor puntuación R²: {grid_search.best_score_:.4f}")
                
            except Exception as e:
                print(f"Error en grid search: {e}, usando modelo base")
                self.model = base_pipeline
        else:
            self.model = base_pipeline
    
    def _train_and_evaluate(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Entrena el modelo final y calcula métricas completas."""
        if not SKLEARN_AVAILABLE:
            return {'error': 'scikit-learn no disponible'}
        
        # Validación cruzada temporal para métricas
        tscv = TimeSeriesSplit(n_splits=5)
        metrics = {
            'r2_scores': [],
            'mae_scores': [],
            'rmse_scores': [],
            'mape_scores': []
        }
        
        for train_idx, test_idx in tscv.split(X):
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
            
            # Crear modelo temporal
            temp_model = make_pipeline(
                RobustScaler(),
                PolynomialFeatures(degree=self.grado, include_bias=False),
                Ridge(alpha=1.0)
            )
            
            temp_model.fit(X_train, y_train)
            y_pred = temp_model.predict(X_test)
            
            # Calcular métricas
            metrics['r2_scores'].append(r2_score(y_test, y_pred))
            metrics['mae_scores'].append(mean_absolute_error(y_test, y_pred))
            metrics['rmse_scores'].append(np.sqrt(mean_squared_error(y_test, y_pred)))
            
            # MAPE
            mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-10))) * 100
            metrics['mape_scores'].append(mape)
        
        # Entrenar modelo final
        if self.model and hasattr(self.model, 'fit'):
            self.model.fit(X, y)
        
        # Obtener información del modelo
        poly_features = None
        ridge_model = None
        
        if self.model and hasattr(self.model, 'named_steps'):
            poly_features = self.model.named_steps.get('polynomialfeatures')
            ridge_model = self.model.named_steps.get('ridge')
        
        feature_names = self._get_polynomial_feature_names(poly_features, list(X.columns)) if poly_features else list(X.columns)
        
        # Calcular importancia (coeficientes)
        importance_info = []
        if ridge_model and hasattr(ridge_model, 'coef_'):
            importance_df = pd.DataFrame({
                'feature': feature_names[:len(ridge_model.coef_)],
                'coeficiente': ridge_model.coef_
            }).sort_values('coeficiente', key=abs, ascending=False)
            importance_info = importance_df.head(20).to_dict('records')  # Top 20 features
        
        return {
            'modelo_tipo': f'polynomial_degree_{self.grado}',
            'metricas': {
                'r2_medio': np.mean(metrics['r2_scores']),
                'r2_std': np.std(metrics['r2_scores']),
                'mae_medio': np.mean(metrics['mae_scores']),
                'rmse_medio': np.mean(metrics['rmse_scores']),
                'mape_medio': np.mean(metrics['mape_scores'])
            },
            'top_features': importance_info,
            'fecha_entrenamiento': datetime.now().isoformat(),
            'n_features_originales': len(X.columns),
            'n_features_polinomicas': len(feature_names),
            'grado_polinomio': self.grado,
            'n_samples': len(X)
        }
    
    def _get_polynomial_feature_names(self, poly, input_features: list) -> list:
        """Genera nombres descriptivos para features polinómicos."""
        try:
            if hasattr(poly, 'powers_'):
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
            else:
                return list(input_features)
        except Exception:
            return list(input_features)
    
    def _save_artifacts(self):
        """Guarda todos los artefactos del modelo."""
        try:
            if not SKLEARN_AVAILABLE:
                return
            
            # Crear directorios
            os.makedirs(self.model_path.parent, exist_ok=True)
            os.makedirs(self.metrics_path.parent, exist_ok=True)
            
            # Guardar modelo
            if self.model:
                joblib.dump(self.model, self.model_path)
            
            # Guardar selector de features si existe
            if self.feature_selector:
                selector_path = self.model_path.parent / f"selector_{self.producto_id}_{self.grado}.pkl"
                joblib.dump(self.feature_selector, selector_path)
            
            print("Artefactos polinómicos guardados exitosamente")
            
        except Exception as e:
            print(f"Error guardando artefactos polinómicos: {e}")