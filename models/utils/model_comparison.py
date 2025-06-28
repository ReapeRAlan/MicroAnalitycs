"""
Sistema de comparación y selección automática de modelos mejorado
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import json
from datetime import datetime
import warnings

# Imports con manejo de errores
try:
    import joblib
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import TimeSeriesSplit
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn no está instalado completamente")

from .logger import model_logger
from .data_validation import DataValidator, DataCleaner
from ..training.train_regresion import ModeloLinealMejorado
from ..training.train_polynomial import ModeloPolinomicoMejorado

warnings.filterwarnings('ignore')

class ModelComparatorMejorado:
    """Comparador mejorado de rendimiento de modelos con selección automática"""
    
    def __init__(self, producto_id: int):
        self.producto_id = producto_id
        self.models_path = Path("models/artifacts")
        self.metrics_history_path = Path("models/metrics_history")
        self.comparison_results_path = Path("models/comparison_results")
        
        # Crear directorios
        self.metrics_history_path.mkdir(exist_ok=True)
        self.comparison_results_path.mkdir(exist_ok=True)
        
        # Métricas de evaluación
        self.metrics = {
            'mae': self._calculate_mae,
            'rmse': self._calculate_rmse,
            'r2': self._calculate_r2,
            'mape': self._calculate_mape
        }
        
        # Configuración de modelos disponibles
        self.model_configs = {
            'linear_auto': {'class': ModeloLinealMejorado, 'params': {'model_type': 'auto'}},
            'linear_ridge': {'class': ModeloLinealMejorado, 'params': {'model_type': 'ridge'}},
            'polynomial_2': {'class': ModeloPolinomicoMejorado, 'params': {'grado': 2}},
            'polynomial_3': {'class': ModeloPolinomicoMejorado, 'params': {'grado': 3}},
            'polynomial_auto': {'class': ModeloPolinomicoMejorado, 'params': {'grado': 'auto'}}
        }
    
    def compare_all_models(self, data: pd.DataFrame, retrain_if_needed: bool = True) -> Dict[str, Any]:
        """
        Compara todos los modelos disponibles y selecciona el mejor.
        
        Args:
            data: DataFrame con datos de entrenamiento
            retrain_if_needed: Si reentrenar modelos si no existen o son antiguos
            
        Returns:
            Dict con resultados de comparación y recomendación
        """
        if data.empty:
            return {'error': 'No hay datos para comparar modelos'}
        
        print(f"Iniciando comparación de modelos para producto {self.producto_id}")
        
        comparison_results = {
            'producto_id': self.producto_id,
            'fecha_comparacion': datetime.now().isoformat(),
            'modelos_evaluados': {},
            'ranking_modelos': [],
            'mejor_modelo': None,
            'metricas_resumen': {},
            'recomendaciones': []
        }
        
        # Evaluar cada modelo
        for model_name, config in self.model_configs.items():
            try:
                print(f"Evaluando modelo: {model_name}")
                
                # Crear y entrenar modelo si es necesario
                model_results = self._evaluate_model(
                    model_name, config, data, retrain_if_needed
                )
                
                if model_results:
                    comparison_results['modelos_evaluados'][model_name] = model_results
                    
            except Exception as e:
                print(f"Error evaluando modelo {model_name}: {e}")
                comparison_results['modelos_evaluados'][model_name] = {
                    'error': str(e),
                    'evaluado': False
                }
        
        # Analizar resultados y hacer recomendaciones
        comparison_results = self._analyze_results(comparison_results)
        
        # Guardar resultados
        self._save_comparison_results(comparison_results)
        
        print(f"Comparación completada. Mejor modelo: {comparison_results.get('mejor_modelo', 'Ninguno')}")
        return comparison_results
    
    def _evaluate_model(self, model_name: str, config: dict, data: pd.DataFrame, retrain: bool) -> dict:
        """Evalúa un modelo específico."""
        try:
            # Verificar si el modelo existe y está actualizado
            model_path = self._get_model_path(model_name)
            needs_training = retrain or not model_path.exists() or self._is_model_outdated(model_path)
            
            if needs_training:
                # Entrenar modelo
                model_class = config['class']
                model_params = config['params']
                
                if model_class == ModeloLinealMejorado:
                    model_instance = model_class(self.producto_id)
                    training_results = model_instance.train_with_validation(**model_params)
                elif model_class == ModeloPolinomicoMejorado:
                    grado = model_params.get('grado', 2)
                    model_instance = model_class(self.producto_id, grado)
                    training_results = model_instance.train_with_validation()
                else:
                    return {'error': 'Tipo de modelo no reconocido', 'evaluado': False}
                
                if not training_results or 'error' in training_results:
                    return {'error': 'Error en entrenamiento', 'evaluado': False}
            
            # Evaluar modelo con validación cruzada independiente
            evaluation_metrics = self._cross_validate_model(model_name, data)
            
            # Calcular métricas adicionales de rendimiento
            performance_metrics = self._calculate_performance_metrics(model_name, data)
            
            return {
                'modelo_nombre': model_name,
                'evaluado': True,
                'metricas_validacion': evaluation_metrics,
                'metricas_rendimiento': performance_metrics,
                'fecha_evaluacion': datetime.now().isoformat(),
                'entrenado_recientemente': needs_training
            }
            
        except Exception as e:
            print(f"Error en evaluación de {model_name}: {e}")
            return {'error': str(e), 'evaluado': False}
    
    def _cross_validate_model(self, model_name: str, data: pd.DataFrame) -> dict:
        """Realiza validación cruzada independiente del modelo."""
        if not SKLEARN_AVAILABLE:
            return {'error': 'sklearn no disponible'}
        
        try:
            # Preparar datos
            features_base = ['dia_semana', 'mes', 'precio_base', 'stock_actual']
            features_calc = ['ventas_7_dias', 'ventas_30_dias', 'margen', 'variacion_precio']
            all_features = features_base + features_calc
            
            available_features = [f for f in all_features if f in data.columns]
            X = data[available_features].fillna(data[available_features].median())
            y = data['cantidad_vendida']
            
            # Validación cruzada temporal
            tscv = TimeSeriesSplit(n_splits=5)
            scores = {metric: [] for metric in self.metrics.keys()}
            
            # Cargar modelo entrenado
            model = self._load_model(model_name)
            if model is None:
                return {'error': 'Modelo no encontrado'}
            
            for train_idx, test_idx in tscv.split(X):
                X_test = X.iloc[test_idx]
                y_test = y.iloc[test_idx]
                
                # Predecir
                try:
                    if hasattr(model, 'predict'):
                        y_pred = model.predict(X_test)
                    else:
                        continue
                        
                    # Calcular métricas
                    for metric_name, metric_func in self.metrics.items():
                        score = metric_func(y_test, y_pred)
                        scores[metric_name].append(score)
                        
                except Exception as e:
                    print(f"Error en fold de validación: {e}")
                    continue
            
            # Resumir resultados
            return {
                metric: {
                    'mean': np.mean(values) if values else 0,
                    'std': np.std(values) if values else 0,
                    'scores': values
                } for metric, values in scores.items()
            }
            
        except Exception as e:
            return {'error': f'Error en validación cruzada: {e}'}
    
    def _calculate_performance_metrics(self, model_name: str, data: pd.DataFrame) -> dict:
        """Calcula métricas adicionales de rendimiento."""
        try:
            model_path = self._get_model_path(model_name)
            
            return {
                'tamaño_modelo_mb': model_path.stat().st_size / (1024 * 1024) if model_path.exists() else 0,
                'complejidad': self._estimate_model_complexity(model_name),
                'interpretabilidad': self._estimate_interpretability(model_name),
                'robustez_outliers': self._estimate_robustness(model_name),
                'tiempo_entrenamiento_estimado': self._estimate_training_time(model_name, len(data))
            }
            
        except Exception as e:
            return {'error': f'Error calculando métricas de rendimiento: {e}'}
    
    def _analyze_results(self, comparison_results: dict) -> dict:
        """Analiza resultados y genera recomendaciones."""
        try:
            modelos_evaluados = comparison_results['modelos_evaluados']
            valid_models = {k: v for k, v in modelos_evaluados.items() 
                          if v.get('evaluado', False) and 'error' not in v}
            
            # Inicializar metricas_resumen con valores por defecto
            comparison_results['metricas_resumen'] = {
                'modelos_evaluados': len(valid_models),
                'mejor_r2': 0.0,
                'mejor_mape': 100.0,
                'promedio_interpretabilidad': 0.0
            }
            
            if not valid_models:
                comparison_results['recomendaciones'].append(
                    "No se pudo evaluar ningún modelo exitosamente"
                )
                return comparison_results
            
            # Ranking basado en múltiples criterios
            ranking = []
            
            for model_name, results in valid_models.items():
                metrics = results.get('metricas_validacion', {})
                performance = results.get('metricas_rendimiento', {})
                
                # Calcular score combinado (ponderado)
                r2_score = metrics.get('r2', {}).get('mean', 0)
                mape_score = metrics.get('mape', {}).get('mean', 100)  # Menor es mejor
                interpretability = performance.get('interpretabilidad', 0)
                robustness = performance.get('robustez_outliers', 0)
                
                # Score combinado (normalizado)
                combined_score = (
                    r2_score * 0.4 +  # 40% precisión
                    (100 - min(mape_score, 100)) / 100 * 0.3 +  # 30% error relativo
                    interpretability * 0.2 +  # 20% interpretabilidad
                    robustness * 0.1  # 10% robustez
                )
                
                ranking.append({
                    'modelo': model_name,
                    'score_combinado': combined_score,
                    'r2': r2_score,
                    'mape': mape_score,
                    'interpretabilidad': interpretability,
                    'robustez': robustness
                })
            
            # Ordenar por score combinado
            ranking.sort(key=lambda x: x['score_combinado'], reverse=True)
            comparison_results['ranking_modelos'] = ranking
            
            # Identificar mejor modelo
            if ranking:
                comparison_results['mejor_modelo'] = ranking[0]['modelo']
                
                # Generar recomendaciones
                best_model = ranking[0]
                recommendations = []
                
                if best_model['r2'] > 0.8:
                    recommendations.append("Excelente precisión de predicción")
                elif best_model['r2'] > 0.6:
                    recommendations.append("Buena precisión de predicción")
                else:
                    recommendations.append("Precisión moderada - considerar más datos o features")
                
                if best_model['mape'] < 10:
                    recommendations.append("Error porcentual muy bajo")
                elif best_model['mape'] < 20:
                    recommendations.append("Error porcentual aceptable")
                else:
                    recommendations.append("Error porcentual alto - revisar calidad de datos")
                
                if best_model['interpretabilidad'] > 0.7:
                    recommendations.append("Modelo fácil de interpretar")
                else:
                    recommendations.append("Modelo complejo - documentar decisiones importantes")
                
                comparison_results['recomendaciones'] = recommendations
            
            # Actualizar resumen de métricas con datos reales
            if ranking:
                comparison_results['metricas_resumen']['mejor_r2'] = float(max([r['r2'] for r in ranking]))
                comparison_results['metricas_resumen']['mejor_mape'] = float(min([r['mape'] for r in ranking]))
                comparison_results['metricas_resumen']['promedio_interpretabilidad'] = float(np.mean([r['interpretabilidad'] for r in ranking]))
            
            return comparison_results
            
        except Exception as e:
            comparison_results['recomendaciones'].append(f"Error en análisis: {e}")
            return comparison_results
    
    # Métrica helpers
    def _calculate_mae(self, y_true, y_pred):
        return mean_absolute_error(y_true, y_pred) if SKLEARN_AVAILABLE else 0
    
    def _calculate_rmse(self, y_true, y_pred):
        return np.sqrt(mean_squared_error(y_true, y_pred)) if SKLEARN_AVAILABLE else 0
    
    def _calculate_r2(self, y_true, y_pred):
        return r2_score(y_true, y_pred) if SKLEARN_AVAILABLE else 0
    
    def _calculate_mape(self, y_true, y_pred):
        return np.mean(np.abs((y_true - y_pred) / (y_true + 1e-10))) * 100
    
    # Utility methods
    def _get_model_path(self, model_name: str) -> Path:
        """Obtiene la ruta del modelo."""
        if 'linear' in model_name:
            return self.models_path / "linear" / f"producto_{self.producto_id}.pkl"
        elif 'polynomial' in model_name:
            grado = '2' if 'polynomial_2' in model_name else '3' if 'polynomial_3' in model_name else '2'
            return self.models_path / "polynomial" / f"producto_{self.producto_id}_grado_{grado}.pkl"
        else:
            return self.models_path / "other" / f"{model_name}_{self.producto_id}.pkl"
    
    def _is_model_outdated(self, model_path: Path, max_age_days: int = 30) -> bool:
        """Verifica si el modelo es muy antiguo."""
        try:
            if not model_path.exists():
                return True
            
            model_age = datetime.now().timestamp() - model_path.stat().st_mtime
            return model_age > (max_age_days * 24 * 3600)
            
        except Exception:
            return True
    
    def _load_model(self, model_name: str):
        """Carga un modelo entrenado."""
        try:
            if not SKLEARN_AVAILABLE:
                return None
                
            model_path = self._get_model_path(model_name)
            if model_path.exists():
                return joblib.load(model_path)
            return None
            
        except Exception as e:
            print(f"Error cargando modelo {model_name}: {e}")
            return None
    
    def _estimate_model_complexity(self, model_name: str) -> float:
        """Estima la complejidad del modelo (0-1)."""
        complexity_map = {
            'linear': 0.2,
            'polynomial_2': 0.5,
            'polynomial_3': 0.7,
            'polynomial_auto': 0.8,
            'random_forest': 0.6,
            'gradient_boosting': 0.8
        }
        
        for key, complexity in complexity_map.items():
            if key in model_name:
                return complexity
        return 0.5
    
    def _estimate_interpretability(self, model_name: str) -> float:
        """Estima la interpretabilidad del modelo (0-1)."""
        interpretability_map = {
            'linear': 0.9,
            'polynomial_2': 0.7,
            'polynomial_3': 0.5,
            'polynomial_auto': 0.4,
            'random_forest': 0.3,
            'gradient_boosting': 0.2
        }
        
        for key, score in interpretability_map.items():
            if key in model_name:
                return score
        return 0.5
    
    def _estimate_robustness(self, model_name: str) -> float:
        """Estima la robustez a outliers (0-1)."""
        robustness_map = {
            'linear': 0.3,
            'polynomial': 0.2,
            'ridge': 0.7,
            'random_forest': 0.8,
            'gradient_boosting': 0.6
        }
        
        for key, score in robustness_map.items():
            if key in model_name:
                return score
        return 0.5
    
    def _estimate_training_time(self, model_name: str, data_size: int) -> float:
        """Estima tiempo de entrenamiento en segundos."""
        base_times = {
            'linear': 0.1,
            'polynomial_2': 0.5,
            'polynomial_3': 2.0,
            'polynomial_auto': 5.0,
            'random_forest': 1.0,
            'gradient_boosting': 3.0
        }
        
        base_time = 1.0
        for key, time in base_times.items():
            if key in model_name:
                base_time = time
                break
        
        # Escalar por tamaño de datos
        size_factor = max(1.0, data_size / 1000)
        return base_time * size_factor
    
    def _save_comparison_results(self, results: dict):
        """Guarda los resultados de comparación."""
        try:
            filename = f"comparison_{self.producto_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.comparison_results_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            # También guardar como "latest"
            latest_filepath = self.comparison_results_path / f"comparison_{self.producto_id}_latest.json"
            with open(latest_filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error guardando resultados de comparación: {e}")

class AutoModelSelector:
    """Selector automático de mejor modelo basado en métricas y contexto."""
    
    def __init__(self, producto_id: int):
        self.producto_id = producto_id
        self.comparator = ModelComparatorMejorado(producto_id)
        self._last_comparison = None
        self._best_model_cache = None
    
    def get_best_model(self, data: pd.DataFrame = None, force_recompare: bool = False) -> Optional[str]:
        """
        Obtiene el mejor modelo para el producto.
        
        Args:
            data: Datos para evaluación (opcional)
            force_recompare: Forzar nueva comparación
            
        Returns:
            Nombre del mejor modelo o None si no hay modelos válidos
        """
        try:
            # Si no se fuerza recomparacion y tenemos caché, usar caché
            if not force_recompare and self._best_model_cache:
                return self._best_model_cache
            
            # Si no hay datos, intentar cargar resultados anteriores
            if data is None or data.empty:
                latest_results = self._load_latest_comparison()
                if latest_results and 'mejor_modelo' in latest_results:
                    self._best_model_cache = latest_results['mejor_modelo']
                    return self._best_model_cache
                return None
            
            # Realizar nueva comparación
            comparison_results = self.comparator.compare_all_models(data)
            self._last_comparison = comparison_results
            
            best_model = comparison_results.get('mejor_modelo')
            if best_model:
                self._best_model_cache = best_model
            
            return best_model
            
        except Exception as e:
            print(f"Error seleccionando mejor modelo: {e}")
            return None
    
    def get_model_path(self, model_name: str = None) -> Optional[Path]:
        """Obtiene la ruta del mejor modelo o modelo específico."""
        if model_name is None:
            model_name = self._best_model_cache or self.get_best_model()
        
        if not model_name:
            return None
            
        return self.comparator._get_model_path(model_name)
    
    def _load_latest_comparison(self) -> Optional[dict]:
        """Carga los últimos resultados de comparación."""
        try:
            latest_path = self.comparator.comparison_results_path / f"comparison_{self.producto_id}_latest.json"
            if latest_path.exists():
                import json
                with open(latest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error cargando última comparación: {e}")
        return None
