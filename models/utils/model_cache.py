"""
Sistema de caché de modelos mejorado para MicroAnalytics
"""
import os
import pickle
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import hashlib
import gzip

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

class ModelCacheMejorado:
    """Sistema de caché mejorado para modelos de ML con versionado y compresión"""
    
    def __init__(self, base_path: str = "models/cache"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Subdirectorios
        self.models_cache = self.base_path / "models"
        self.predictions_cache = self.base_path / "predictions"
        self.metadata_cache = self.base_path / "metadata"
        
        for dir_path in [self.models_cache, self.predictions_cache, self.metadata_cache]:
            dir_path.mkdir(exist_ok=True)
        
        # Configuración
        self.max_cache_age_days = 30
        self.max_cache_size_mb = 500
        self.compression_level = 6
        
    def cache_model(self, model, producto_id: int, model_type: str, 
                   version: Optional[str] = None, metadata: Optional[Dict] = None) -> Optional[str]:
        """
        Cachea un modelo entrenado con metadata.
        
        Args:
            model: Modelo entrenado
            producto_id: ID del producto
            model_type: Tipo de modelo (linear, polynomial, etc.)
            version: Versión del modelo (auto-generada si no se especifica)
            metadata: Metadata adicional
            
        Returns:
            str: ID del caché generado
        """
        try:
            # Generar versión si no se especifica
            if version is None:
                version = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Generar ID de caché
            cache_id = self._generate_cache_id(producto_id, model_type, version)
            
            # Preparar metadata
            model_metadata = {
                'cache_id': cache_id,
                'producto_id': producto_id,
                'model_type': model_type,
                'version': version,
                'timestamp': datetime.now().isoformat(),
                'size_bytes': 0,
                'compression': 'gzip',
                'format': 'joblib' if JOBLIB_AVAILABLE else 'pickle'
            }
            
            if metadata:
                model_metadata.update(metadata)
            
            # Serializar y comprimir modelo
            model_path = self.models_cache / f"{cache_id}.pkl.gz"
            
            if JOBLIB_AVAILABLE:
                # Usar joblib si está disponible
                with gzip.open(model_path, 'wb', compresslevel=self.compression_level) as f:
                    joblib.dump(model, f)
            else:
                # Fallback a pickle
                with gzip.open(model_path, 'wb', compresslevel=self.compression_level) as f:
                    pickle.dump(model, f)
            
            # Actualizar size
            model_metadata['size_bytes'] = model_path.stat().st_size
            
            # Guardar metadata
            metadata_path = self.metadata_cache / f"{cache_id}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(model_metadata, f, ensure_ascii=False, indent=2)
            
            # Limpiar caché viejo si es necesario
            self._cleanup_old_cache()
            
            print(f"Modelo cacheado: {cache_id}")
            return cache_id
            
        except Exception as e:
            print(f"Error cacheando modelo: {e}")
            return None
    def load_model(self, cache_id: Optional[str] = None, producto_id: Optional[int] = None,
                  model_type: Optional[str] = None, latest: bool = False):
        """
        Carga un modelo del caché.
        
        Args:
            cache_id: ID específico del caché
            producto_id: ID del producto (buscar por producto)
            model_type: Tipo de modelo
            latest: Si True, carga la versión más reciente
            
        Returns:
            Tuple[model, metadata] o (None, None) si no se encuentra
        """
        try:
            target_cache_id = cache_id
            
            # Buscar por producto y tipo si no se especifica cache_id
            if not target_cache_id and producto_id and model_type:
                target_cache_id = self._find_cache_id(producto_id, model_type, latest)
            
            if not target_cache_id:
                return None, None
            
            # Cargar metadata
            metadata_path = self.metadata_cache / f"{target_cache_id}.json"
            if not metadata_path.exists():
                return None, None
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Verificar si el caché es válido
            if self._is_cache_expired(metadata):
                print(f"Caché expirado: {target_cache_id}")
                return None, None
            
            # Cargar modelo
            model_path = self.models_cache / f"{target_cache_id}.pkl.gz"
            if not model_path.exists():
                return None, None
            
            if metadata.get('format') == 'joblib' and JOBLIB_AVAILABLE:
                with gzip.open(model_path, 'rb') as f:
                    model = joblib.load(f)
            else:
                with gzip.open(model_path, 'rb') as f:
                    model = pickle.load(f)
            
            print(f"Modelo cargado desde caché: {target_cache_id}")
            return model, metadata
            
        except Exception as e:
            print(f"Error cargando modelo del caché: {e}")
            return None, None
    
    def cache_prediction(self, prediction: Any, producto_id: int, 
                        input_hash: str, model_cache_id: Optional[str] = None) -> Optional[str]:
        """
        Cachea una predicción para evitar recálculos.
        
        Args:
            prediction: Resultado de la predicción
            producto_id: ID del producto
            input_hash: Hash de los datos de entrada
            model_cache_id: ID del modelo usado
            
        Returns:
            str: ID del caché de predicción
        """
        try:
            # Generar ID de predicción
            pred_id = f"pred_{producto_id}_{input_hash[:8]}_{datetime.now().strftime('%Y%m%d')}"
            
            # Metadata de predicción
            pred_metadata = {
                'prediction_id': pred_id,
                'producto_id': producto_id,
                'input_hash': input_hash,
                'model_cache_id': model_cache_id,
                'timestamp': datetime.now().isoformat(),
                'prediction_type': type(prediction).__name__
            }
            
            # Guardar predicción
            pred_path = self.predictions_cache / f"{pred_id}.pkl.gz"
            with gzip.open(pred_path, 'wb', compresslevel=self.compression_level) as f:
                pickle.dump(prediction, f)
            
            # Guardar metadata
            metadata_path = self.predictions_cache / f"{pred_id}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(pred_metadata, f, ensure_ascii=False, indent=2)
            
            return pred_id
            
        except Exception as e:
            print(f"Error cacheando predicción: {e}")
            return None
    
    def load_prediction(self, producto_id: int, input_hash: str, 
                       max_age_hours: int = 24):
        """
        Carga una predicción cacheada si existe y es válida.
        
        Args:
            producto_id: ID del producto
            input_hash: Hash de los datos de entrada
            max_age_hours: Edad máxima en horas
            
        Returns:
            Predicción o None si no existe/es inválida
        """
        try:
            # Buscar predicciones para el producto
            pattern = f"pred_{producto_id}_{input_hash[:8]}_*"
            matching_files = list(self.predictions_cache.glob(f"{pattern}.json"))
            
            if not matching_files:
                return None
            
            # Buscar la más reciente válida
            for metadata_path in sorted(matching_files, reverse=True):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Verificar edad
                timestamp = datetime.fromisoformat(metadata['timestamp'])
                age = datetime.now() - timestamp
                
                if age.total_seconds() / 3600 <= max_age_hours:
                    # Cargar predicción
                    pred_id = metadata['prediction_id']
                    pred_path = self.predictions_cache / f"{pred_id}.pkl.gz"
                    
                    if pred_path.exists():
                        with gzip.open(pred_path, 'rb') as f:
                            prediction = pickle.load(f)
                        
                        print(f"Predicción cargada desde caché: {pred_id}")
                        return prediction
            
            return None
            
        except Exception as e:
            print(f"Error cargando predicción del caché: {e}")
            return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del caché."""
        try:
            stats = {
                'models': {
                    'count': 0,
                    'total_size_mb': 0,
                    'oldest': None,
                    'newest': None
                },
                'predictions': {
                    'count': 0,
                    'total_size_mb': 0,
                    'oldest': None,
                    'newest': None
                },
                'cache_health': 'good'
            }
            
            # Estadísticas de modelos
            model_files = list(self.models_cache.glob("*.pkl.gz"))
            if model_files:
                stats['models']['count'] = len(model_files)
                total_size = sum(f.stat().st_size for f in model_files)
                stats['models']['total_size_mb'] = total_size / (1024 * 1024)
                
                # Fechas
                timestamps = []
                for f in model_files:
                    metadata_path = self.metadata_cache / f"{f.stem.replace('.pkl', '')}.json"
                    if metadata_path.exists():
                        with open(metadata_path, 'r') as mf:
                            metadata = json.load(mf)
                            timestamps.append(metadata.get('timestamp'))
                
                if timestamps:
                    timestamps.sort()
                    stats['models']['oldest'] = timestamps[0]
                    stats['models']['newest'] = timestamps[-1]
            
            # Estadísticas de predicciones
            pred_files = list(self.predictions_cache.glob("*.pkl.gz"))
            if pred_files:
                stats['predictions']['count'] = len(pred_files)
                total_size = sum(f.stat().st_size for f in pred_files)
                stats['predictions']['total_size_mb'] = total_size / (1024 * 1024)
            
            # Salud del caché
            total_size_mb = stats['models']['total_size_mb'] + stats['predictions']['total_size_mb']
            if total_size_mb > self.max_cache_size_mb:
                stats['cache_health'] = 'needs_cleanup'
            elif total_size_mb > self.max_cache_size_mb * 0.8:
                stats['cache_health'] = 'warning'
            
            return stats
            
        except Exception as e:
            return {'error': f'Error obteniendo estadísticas: {e}'}
    
    def cleanup_cache(self, force: bool = False) -> Dict[str, Any]:
        """
        Limpia el caché eliminando elementos viejos o inválidos.
        
        Args:
            force: Si True, fuerza limpieza agresiva
            
        Returns:
            Dict con estadísticas de limpieza
        """
        try:
            removed_models = 0
            removed_predictions = 0
            freed_space_mb = 0
            
            cutoff_date = datetime.now() - timedelta(days=self.max_cache_age_days)
            
            # Limpiar modelos viejos
            for metadata_path in self.metadata_cache.glob("*.json"):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    # Verificar si es muy viejo
                    timestamp = datetime.fromisoformat(metadata['timestamp'])
                    
                    if timestamp < cutoff_date or force:
                        cache_id = metadata['cache_id']
                        model_path = self.models_cache / f"{cache_id}.pkl.gz"
                        
                        # Obtener tamaño antes de eliminar
                        if model_path.exists():
                            freed_space_mb += model_path.stat().st_size / (1024 * 1024)
                            model_path.unlink()
                        
                        metadata_path.unlink()
                        removed_models += 1
                        
                except Exception as e:
                    print(f"Error limpiando modelo: {e}")
                    continue
            
            # Limpiar predicciones viejas
            cutoff_pred = datetime.now() - timedelta(hours=48)  # Predicciones más corto tiempo
            
            for pred_metadata_path in self.predictions_cache.glob("*.json"):
                try:
                    with open(pred_metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    timestamp = datetime.fromisoformat(metadata['timestamp'])
                    
                    if timestamp < cutoff_pred or force:
                        pred_id = metadata['prediction_id']
                        pred_path = self.predictions_cache / f"{pred_id}.pkl.gz"
                        
                        if pred_path.exists():
                            freed_space_mb += pred_path.stat().st_size / (1024 * 1024)
                            pred_path.unlink()
                        
                        pred_metadata_path.unlink()
                        removed_predictions += 1
                        
                except Exception as e:
                    print(f"Error limpiando predicción: {e}")
                    continue
            
            return {
                'removed_models': removed_models,
                'removed_predictions': removed_predictions,
                'freed_space_mb': round(freed_space_mb, 2)
            }
            
        except Exception as e:
            return {'error': f'Error en limpieza: {e}'}
    
    # Métodos helper privados
    def _generate_cache_id(self, producto_id: int, model_type: str, version: str) -> str:
        """Genera un ID único para el caché."""
        base_string = f"{producto_id}_{model_type}_{version}"
        hash_obj = hashlib.md5(base_string.encode())
        return f"{model_type}_{producto_id}_{version}_{hash_obj.hexdigest()[:8]}"
    
    def _find_cache_id(self, producto_id: int, model_type: str, latest: bool = False) -> Optional[str]:
        """Encuentra el cache_id para un producto y tipo de modelo."""
        pattern = f"{model_type}_{producto_id}_*"
        matching_files = list(self.metadata_cache.glob(f"{pattern}.json"))
        
        if not matching_files:
            return None
        
        if latest:
            # Buscar el más reciente
            newest_file = None
            newest_time = None
            
            for metadata_path in matching_files:
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    timestamp = datetime.fromisoformat(metadata['timestamp'])
                    
                    if newest_time is None or timestamp > newest_time:
                        newest_time = timestamp
                        newest_file = metadata['cache_id']
                        
                except Exception:
                    continue
            
            return newest_file
        else:
            # Retornar el primero encontrado
            try:
                with open(matching_files[0], 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                return metadata['cache_id']
            except Exception:
                return None
    
    def _is_cache_expired(self, metadata: Dict) -> bool:
        """Verifica si un caché ha expirado."""
        try:
            timestamp = datetime.fromisoformat(metadata['timestamp'])
            age = datetime.now() - timestamp
            return age.days > self.max_cache_age_days
        except Exception:
            return True
    
    def _cleanup_old_cache(self):
        """Limpieza automática de caché viejo."""
        try:
            stats = self.get_cache_stats()
            
            if stats.get('cache_health') == 'needs_cleanup':
                self.cleanup_cache()
                
        except Exception as e:
            print(f"Error en limpieza automática: {e}")

# Instancia global del caché
model_cache = ModelCacheMejorado()
