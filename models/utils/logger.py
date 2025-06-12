"""
Sistema de logging para el proyecto MicroAnalytics
"""
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

class ModelLogger:
    """Logger especializado para modelos de ML"""
    
    def __init__(self, name: str = "MicroAnalytics"):
        self.logger = logging.getLogger(name)
        self.setup_logger()
    
    def setup_logger(self):
        """Configura el sistema de logging"""
        if not self.logger.handlers:
            # Crear directorio de logs
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # Configurar formato
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Handler para archivo
            file_handler = logging.FileHandler(
                log_dir / f"microanalytics_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            
            # Handler para consola
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.WARNING)
            
            # Agregar handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)
    
    def log_prediction(self, producto_id: int, modelo: str, 
                      prediccion: Any, confianza: Optional[float] = None):
        """Log de predicciones realizadas"""
        msg = f"PREDICCION - Producto: {producto_id}, Modelo: {modelo}, "
        msg += f"Resultado: {prediccion}"
        if confianza:
            msg += f", Confianza: {confianza:.2%}"
        self.logger.info(msg)
    
    def log_model_training(self, producto_id: int, modelo: str, metricas: Dict[str, Any]):
        """Log de entrenamiento de modelos"""
        msg = f"ENTRENAMIENTO - Producto: {producto_id}, Modelo: {modelo}, "
        msg += f"Métricas: {metricas}"
        self.logger.info(msg)
    
    def log_error(self, error: Exception, context: str = ""):
        """Log de errores con contexto"""
        msg = f"ERROR - {context}: {str(error)}"
        self.logger.error(msg, exc_info=True)
    
    def log_data_quality(self, producto_id: int, issues: Dict[str, Any]):
        """Log de problemas de calidad de datos"""
        msg = f"CALIDAD_DATOS - Producto: {producto_id}, Problemas: {issues}"
        self.logger.warning(msg)
    
    def log_performance(self, producto_id: int, modelo: str, tiempo_ejecucion: float):
        """Log de rendimiento"""
        msg = f"PERFORMANCE - Producto: {producto_id}, Modelo: {modelo}, "
        msg += f"Tiempo: {tiempo_ejecucion:.2f}s"
        self.logger.info(msg)

# Instancia global del logger
model_logger = ModelLogger()
