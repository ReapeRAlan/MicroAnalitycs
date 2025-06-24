"""
Rutas REST para predicciones de demanda usando modelos de ML
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import sys
import os

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from models.predict import predict_demanda, ModelPredictor
from backend.base import get_db

router = APIRouter()

# Modelos Pydantic para request/response
class PredictionRequest(BaseModel):
    producto_id: int
    dias_adelante: int = 7
    include_confidence: bool = True
    use_cache: bool = True

class PredictionResponse(BaseModel):
    producto_id: int
    dias_adelante: int
    predicciones: List[float]
    mejor_modelo: Optional[str] = None
    confianza: Optional[float] = None
    metadata: Dict[str, Any] = {}

class ModelComparisonResponse(BaseModel):
    producto_id: int
    mejor_modelo: Optional[str]
    ranking_modelos: List[Dict[str, Any]]
    metricas_resumen: Dict[str, Any]
    recomendaciones: List[str]

@router.post("/predict/demanda", response_model=PredictionResponse)
async def predecir_demanda(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predice la demanda para un producto específico.
    
    Args:
        request: Datos de la solicitud de predicción
        db: Sesión de base de datos
        
    Returns:
        Predicciones de demanda para los próximos días
    """
    try:
        if request.producto_id <= 0:
            raise HTTPException(status_code=400, detail="ID de producto debe ser positivo")
        
        if request.dias_adelante <= 0 or request.dias_adelante > 365:
            raise HTTPException(status_code=400, detail="Días adelante debe estar entre 1 y 365")
        
        # Crear predictor
        predictor = ModelPredictor(request.producto_id)
        
        # Obtener predicciones con todos los modelos
        result = predictor.predict_all_models(
            dias_adelante=request.dias_adelante,
            include_confidence=request.include_confidence,
            use_cache=request.use_cache
        )
        
        if not result or 'best_prediction' not in result:
            raise HTTPException(
                status_code=404, 
                detail=f"No se pudieron generar predicciones para producto {request.producto_id}"
            )
        
        best_prediction = result['best_prediction']
        
        response = PredictionResponse(
            producto_id=request.producto_id,
            dias_adelante=request.dias_adelante,
            predicciones=best_prediction.get('prediction', []),
            mejor_modelo=best_prediction.get('model'),
            confianza=best_prediction.get('confidence'),
            metadata=result.get('metadata', {})
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")

@router.get("/predict/demanda/{producto_id}", response_model=PredictionResponse)
async def predecir_demanda_simple(
    producto_id: int,
    dias_adelante: int = Query(default=7, ge=1, le=365),
    usar_cache: bool = Query(default=True),
    db: Session = Depends(get_db)
):
    """
    Endpoint simple para predicción de demanda.
    
    Args:
        producto_id: ID del producto
        dias_adelante: Número de días a predecir (1-365)
        usar_cache: Si usar caché para acelerar la predicción
        db: Sesión de base de datos
        
    Returns:
        Predicciones de demanda
    """
    try:
        # Usar función simple para compatibilidad
        predicciones = predict_demanda(producto_id, dias_adelante)
        
        if not predicciones:
            raise HTTPException(
                status_code=404,
                detail=f"No se pudieron generar predicciones para producto {producto_id}"
            )
        
        response = PredictionResponse(
            producto_id=producto_id,
            dias_adelante=dias_adelante,
            predicciones=predicciones,
            metadata={
                'timestamp': None,
                'method': 'simple',
                'cached': usar_cache
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")

@router.get("/predict/models/comparison/{producto_id}", response_model=ModelComparisonResponse)
async def comparar_modelos(
    producto_id: int,
    forzar_reentrenamiento: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    """
    Compara todos los modelos disponibles para un producto.
    
    Args:
        producto_id: ID del producto
        forzar_reentrenamiento: Si forzar reentrenamiento de modelos
        db: Sesión de base de datos
        
    Returns:
        Resultados de comparación de modelos
    """
    try:
        from models.utils.model_comparison import ModelComparatorMejorado
        from models.utils.data_processing import obtener_datos_enriquecidos
        
        # Obtener datos para evaluación
        data = obtener_datos_enriquecidos(producto_id)
        
        if data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No hay datos suficientes para producto {producto_id}"
            )
        
        # Crear comparador y ejecutar comparación
        comparator = ModelComparatorMejorado(producto_id)
        results = comparator.compare_all_models(data, retrain_if_needed=forzar_reentrenamiento)
        
        response = ModelComparisonResponse(
            producto_id=producto_id,
            mejor_modelo=results.get('mejor_modelo'),
            ranking_modelos=results.get('ranking_modelos', []),
            metricas_resumen=results.get('metricas_resumen', {}),
            recomendaciones=results.get('recomendaciones', [])
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en comparación: {str(e)}")

@router.get("/predict/cache/stats/{producto_id}")
async def obtener_stats_cache(
    producto_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas del caché para un producto.
    
    Args:
        producto_id: ID del producto
        db: Sesión de base de datos
        
    Returns:
        Estadísticas del caché
    """
    try:
        predictor = ModelPredictor(producto_id)
        stats = predictor.get_cache_stats()
        
        return {
            'producto_id': producto_id,
            'cache_stats': stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo stats: {str(e)}")

@router.delete("/predict/cache/{producto_id}")
async def limpiar_cache(
    producto_id: int,
    db: Session = Depends(get_db)
):
    """
    Limpia el caché para un producto específico.
    
    Args:
        producto_id: ID del producto
        db: Sesión de base de datos
        
    Returns:
        Confirmación de limpieza
    """
    try:
        predictor = ModelPredictor(producto_id)
        predictor.clear_cache()
        
        return {
            'message': f'Caché limpiado para producto {producto_id}',
            'producto_id': producto_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error limpiando caché: {str(e)}")

@router.get("/predict/health")
async def health_check():
    """
    Verifica el estado del servicio de predicciones.
    
    Returns:
        Estado del servicio
    """
    try:
        from models.utils.model_cache import model_cache
        
        cache_stats = model_cache.get_cache_stats()
        
        return {
            'status': 'healthy',
            'service': 'prediction_service',
            'cache_available': True,
            'total_cached_models': cache_stats.get('total_models', 0),
            'total_cached_predictions': cache_stats.get('total_predictions', 0)
        }
        
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }
