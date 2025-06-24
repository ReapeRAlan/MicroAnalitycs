"""
Sistema de manejo de errores personalizado para MicroAnalytics
"""
from typing import Any, Optional, Callable
from functools import wraps
import traceback
from .logger import model_logger

class MicroAnalyticsError(Exception):
    """Excepción base para errores del sistema"""
    pass

class DataValidationError(MicroAnalyticsError):
    """Error en validación de datos"""
    pass

class ModelTrainingError(MicroAnalyticsError):
    """Error en entrenamiento de modelos"""
    pass

class PredictionError(MicroAnalyticsError):
    """Error en predicciones"""
    pass

class DatabaseError(MicroAnalyticsError):
    """Error de base de datos"""
    pass

def handle_errors(error_type: type = Exception, 
                 default_return: Any = None,
                 log_error: bool = True):
    """
    Decorador para manejo de errores con logging automático
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_type as e:
                if log_error:
                    context = f"Función: {func.__name__}, Args: {args[:2]}"  # Limitar args para logging
                    model_logger.log_error(e, context)
                
                # Re-lanzar errores críticos
                if isinstance(e, (DatabaseError, DataValidationError)):
                    raise e
                
                return default_return
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, 
                default_return: Any = None, 
                context: str = "") -> Any:
    """
    Ejecuta una función de manera segura con manejo de errores
    """
    try:
        return func(*args)
    except Exception as e:
        model_logger.log_error(e, context)
        return default_return

class ErrorContext:
    """Context manager para manejo de errores con contexto"""
    
    def __init__(self, operation: str, critical: bool = False):
        self.operation = operation
        self.critical = critical
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            model_logger.log_error(exc_val, f"Operación: {self.operation}")
            
            if self.critical:
                # Para operaciones críticas, re-lanzar el error
                return False
            else:
                # Para operaciones no críticas, suprimir el error
                return True
        return False

def validate_input(validation_func: Callable, error_message: str = "Datos de entrada inválidos"):
    """
    Decorador para validar inputs de funciones
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not validation_func(*args, **kwargs):
                raise DataValidationError(error_message)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Funciones de validación comunes
def validate_producto_id(producto_id: int, *args, **kwargs) -> bool:
    """Valida que el ID del producto sea válido"""
    return isinstance(producto_id, int) and producto_id > 0

def validate_prediction_input(dias_adelante: int, *args, **kwargs) -> bool:
    """Valida input para predicciones"""
    return isinstance(dias_adelante, int) and 1 <= dias_adelante <= 365
