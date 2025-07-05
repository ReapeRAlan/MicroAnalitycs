import os
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime
import warnings

# Imports que pueden fallar se manejan con try/except
try:
    from sklearn.linear_model import LinearRegression, Ridge, ElasticNet
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler, RobustScaler
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

class DataValidationError(Exception):
    """Error en validación de datos"""
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
            return issues  # Retornar inmediatamente si faltan columnas críticas
        
        # Verificar valores faltantes críticos solo si las columnas existen
        critical_columns = ['cantidad_vendida', 'precio_base']
        available_critical = [col for col in critical_columns if col in data.columns]
        
        if available_critical:
            critical_missing = data[available_critical].isnull().sum()
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

class ModeloLinealMejorado:
    """Modelo de regresión lineal mejorado con validación de calidad y selección automática."""
    """
    Strategy Pattern:
    Implementa una estrategia específica de entrenamiento y predicción.
    Template Method Pattern:
    Define el flujo general de entrenamiento, permitiendo personalización de pasos.
    """
    
    def __init__(self, producto_id: int):
        self.producto_id = producto_id
        self.model_path = Path(f"models/artifacts/linear/producto_{producto_id}.pkl")
        self.scaler_path = Path(f"models/artifacts/linear/scaler_{producto_id}.pkl")
        self.selector_path = Path(f"models/artifacts/linear/selector_{producto_id}.pkl")
        self.metrics_path = Path(f"models/metrics/linear_metrics_{producto_id}.json")
        
        self.model = None
        self.scaler = None
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
        
        # Configuración de modelos disponibles
        self.modelo_configs = {
            'linear': LinearRegression(),
            'ridge': Ridge(),
            'elastic_net': ElasticNet(),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        # Parámetros para grid search
        self.param_grids = {
            'ridge': {'alpha': [0.1, 1.0, 10.0, 100.0]},
            'elastic_net': {
                'alpha': [0.1, 1.0, 10.0],
                'l1_ratio': [0.1, 0.5, 0.9]
            },
            'random_forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20]
            },
            'gradient_boosting': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2]
            }
        }
    
    @handle_errors(ModelTrainingError, default_return=None)
    def train_with_validation(self, model_type='auto', use_feature_selection=True) -> dict:
        """
        Entrena el modelo con validación de calidad de datos y selección automática.
        
        Args:
            model_type: Tipo de modelo ('auto', 'linear', 'ridge', etc.)
            use_feature_selection: Si aplicar selección de features
            
        Returns:
            dict: Métricas de rendimiento y información del modelo
        """
        print(f"Iniciando entrenamiento para producto {self.producto_id}")
        
        # 1. Obtener y validar datos
        data = self._get_validated_data()
        if data is None or data.empty:
            raise ModelTrainingError(f"No hay datos válidos para producto {self.producto_id}")
        
        # 2. Preparar features con manejo de datos faltantes
        X, y = self._prepare_features(data, use_feature_selection)
        
        # 3. Selección automática del mejor modelo
        if model_type == 'auto':
            best_model_info = self._select_best_model(X, y)
            self.model = best_model_info['model']
            model_type = best_model_info['type']
        else:
            self.model = self._get_optimized_model(model_type, X, y)
        
        # 4. Entrenamiento final y evaluación
        metrics = self._train_and_evaluate(X, y, model_type)
        
        # 5. Guardar artefactos
        self._save_artifacts()
        
        print(f"Entrenamiento completado para producto {self.producto_id}")
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
        
        # Escalado robusto (menos sensible a outliers)
        self.scaler = RobustScaler()
        X_scaled = self.scaler.fit_transform(X)
        X_scaled = pd.DataFrame(X_scaled, columns=available_features, index=X.index)
        
        # Selección de features si está habilitada
        if use_feature_selection and len(available_features) > 5:
            k_features = min(10, len(available_features))
            self.feature_selector = SelectKBest(score_func=f_regression, k=k_features)
            X_selected = self.feature_selector.fit_transform(X_scaled, y)
            
            # Obtener nombres de features seleccionadas
            selected_indices = self.feature_selector.get_support(indices=True)
            selected_features = [available_features[i] for i in selected_indices]
            X_scaled = pd.DataFrame(X_selected, columns=selected_features, index=X.index)
            
            print(f"Features seleccionadas: {selected_features}")
        
        return X_scaled, y
    
    def _select_best_model(self, X: pd.DataFrame, y: pd.Series) -> dict:
        """Selecciona automáticamente el mejor modelo basado en validación cruzada."""
        best_score = -np.inf
        best_model = None
        best_type = None
        
        # Validación cruzada temporal
        tscv = TimeSeriesSplit(n_splits=3)
        
        for model_type, base_model in self.modelo_configs.items():
            try:
                scores = []
                
                for train_idx, test_idx in tscv.split(X):
                    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                    
                    # Optimizar hiperparámetros si están disponibles
                    if model_type in self.param_grids:
                        grid = GridSearchCV(
                            base_model, 
                            self.param_grids[model_type],
                            cv=3, 
                            scoring='r2',
                            n_jobs=-1
                        )
                        grid.fit(X_train, y_train)
                        model = grid.best_estimator_
                    else:
                        model = base_model
                        model.fit(X_train, y_train)
                    
                    y_pred = model.predict(X_test)
                    score = r2_score(y_test, y_pred)
                    scores.append(score)
                
                mean_score = np.mean(scores)
                print(f"Modelo {model_type}: R² = {mean_score:.4f}")
                
                if mean_score > best_score:
                    best_score = mean_score
                    best_model = model
                    best_type = model_type
                    
            except Exception as e:
                print(f"Error evaluando modelo {model_type}: {e}")
                continue
        
        print(f"Mejor modelo seleccionado: {best_type} (R² = {best_score:.4f})")
        return {'model': best_model, 'type': best_type, 'score': best_score}
    
    def _get_optimized_model(self, model_type: str, X: pd.DataFrame, y: pd.Series):
        """Obtiene modelo optimizado con grid search."""
        base_model = self.modelo_configs[model_type]
        
        if model_type in self.param_grids:
            grid = GridSearchCV(
                base_model,
                self.param_grids[model_type],
                cv=TimeSeriesSplit(n_splits=3),
                scoring='r2',
                n_jobs=-1
            )
            grid.fit(X, y)
            return grid.best_estimator_
        else:
            base_model.fit(X, y)
            return base_model
    
    def _train_and_evaluate(self, X: pd.DataFrame, y: pd.Series, model_type: str) -> dict:
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
            
            # Crear modelo temporal con la misma configuración
            if hasattr(self.model, '__class__') and hasattr(self.model, 'get_params'):
                temp_model = self.model.__class__(**self.model.get_params())
                temp_model.fit(X_train, y_train)
                y_pred = temp_model.predict(X_test)
            else:
                # Fallback para modelos sin get_params
                continue
            
            # Calcular métricas
            metrics['r2_scores'].append(r2_score(y_test, y_pred))
            metrics['mae_scores'].append(mean_absolute_error(y_test, y_pred))
            metrics['rmse_scores'].append(np.sqrt(mean_squared_error(y_test, y_pred)))
            
            # MAPE
            mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-10))) * 100
            metrics['mape_scores'].append(mape)
        
        # Entrenar modelo final
        if hasattr(self.model, 'fit'):
            self.model.fit(X, y)
        
        # Calcular importancia de features
        feature_importance = self._calculate_feature_importance(list(X.columns))
        
        return {
            'modelo_tipo': model_type,
            'metricas': {
                'r2_medio': np.mean(metrics['r2_scores']) if metrics['r2_scores'] else 0,
                'r2_std': np.std(metrics['r2_scores']) if metrics['r2_scores'] else 0,
                'mae_medio': np.mean(metrics['mae_scores']) if metrics['mae_scores'] else 0,
                'rmse_medio': np.mean(metrics['rmse_scores']) if metrics['rmse_scores'] else 0,
                'mape_medio': np.mean(metrics['mape_scores']) if metrics['mape_scores'] else 0
            },
            'importancia_features': feature_importance,
            'fecha_entrenamiento': datetime.now().isoformat(),
            'n_features': len(X.columns),
            'n_samples': len(X)
        }
    
    def _calculate_feature_importance(self, feature_names: list) -> list:
        """Calcula importancia de features según el tipo de modelo."""
        try:
            if not SKLEARN_AVAILABLE or self.model is None:
                return []
                
            if hasattr(self.model, 'coef_') and self.model.coef_ is not None:
                # Modelos lineales
                importance = np.abs(self.model.coef_)
            elif hasattr(self.model, 'feature_importances_') and self.model.feature_importances_ is not None:
                # Modelos basados en árboles
                importance = self.model.feature_importances_
            else:
                # Fallback: importancia uniforme
                importance = np.ones(len(feature_names)) / len(feature_names)
            
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importancia': importance
            }).sort_values('importancia', ascending=False)
            
            return importance_df.to_dict('records')
            
        except Exception as e:
            print(f"Error calculando importancia: {e}")
            return []
    
    def _save_artifacts(self):
        """Guarda todos los artefactos del modelo."""
        try:
            # Crear directorios
            os.makedirs(self.model_path.parent, exist_ok=True)
            os.makedirs(self.metrics_path.parent, exist_ok=True)
            
            # Guardar modelo
            joblib.dump(self.model, self.model_path)
            
            # Guardar scaler
            if self.scaler:
                joblib.dump(self.scaler, self.scaler_path)
            
            # Guardar selector de features
            if self.feature_selector:
                joblib.dump(self.feature_selector, self.selector_path)
            
            print("Artefactos guardados exitosamente")
            
        except Exception as e:
            print(f"Error guardando artefactos: {e}")