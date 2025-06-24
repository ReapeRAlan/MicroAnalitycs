"""
Esquema de comunicación entre el chatbot y el backend para ejecutar modelos ML
"""
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class PredictionScope(str, Enum):
    """Alcance de la predicción"""
    SINGLE_PRODUCT = "single_product"
    CATEGORY = "category"
    BUSINESS = "business"
    MARKET = "market"

class ModelType(str, Enum):
    """Tipos de modelos disponibles"""
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"
    AUTO_SELECT = "auto_select"
    COMPARISON = "comparison"

class RequestType(str, Enum):
    """Tipos de peticiones disponibles"""
    PREDICTION = "prediction"
    MODEL_COMPARISON = "model_comparison" 
    CACHE_STATS = "cache_stats"
    HEALTH_CHECK = "health_check"
    SCRAPING_ANALYSIS = "scraping_analysis"

class ChatMessageType(str, Enum):
    """Tipos de mensajes en el chat"""
    USER_QUERY = "user_query"
    ASSISTANT_RESPONSE = "assistant_response"
    MODEL_REQUEST = "model_request"
    MODEL_RESPONSE = "model_response"
    ERROR = "error"
    SYSTEM = "system"

class ModelAction(str, Enum):
    """Acciones que puede ejecutar el modelo"""
    PREDICT_DEMAND = "predict_demand"
    COMPARE_MODELS = "compare_models"
    ANALYZE_TRENDS = "analyze_trends"
    GET_INVENTORY_STATUS = "get_inventory_status"
    PRICE_OPTIMIZATION = "price_optimization"
    FORECAST_SALES = "forecast_sales"
    GENERATE_REPORT = "generate_report"

class ChatMessage(BaseModel):
    """Mensaje base del chat"""
    id: str = Field(..., description="ID único del mensaje")
    type: ChatMessageType = Field(..., description="Tipo de mensaje")
    content: str = Field(..., description="Contenido del mensaje")
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = Field(None, description="ID del usuario")
    session_id: str = Field(..., description="ID de la sesión de chat")
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ModelRequest(BaseModel):
    """Solicitud para ejecutar un modelo ML"""
    action: ModelAction = Field(..., description="Acción a ejecutar")
    producto_id: Optional[int] = Field(None, description="ID del producto")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parámetros específicos")
    context: Optional[str] = Field(None, description="Contexto de la consulta")
    user_intent: Optional[str] = Field(None, description="Intención del usuario")

class ModelResponse(BaseModel):
    """Respuesta del modelo ML"""
    success: bool = Field(..., description="Si la ejecución fue exitosa")
    action: ModelAction = Field(..., description="Acción ejecutada")
    data: Dict[str, Any] = Field(default_factory=dict, description="Datos de respuesta")
    message: str = Field(..., description="Mensaje descriptivo")
    execution_time: float = Field(..., description="Tiempo de ejecución en segundos")
    confidence: Optional[float] = Field(None, description="Nivel de confianza del resultado")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones")

class ChatContext(BaseModel):
    """Contexto de la conversación"""
    session_id: str = Field(..., description="ID de la sesión")
    user_id: Optional[str] = Field(None, description="ID del usuario")
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    current_topic: Optional[str] = Field(None, description="Tema actual de conversación")
    active_filters: Dict[str, Any] = Field(default_factory=dict)
    last_model_action: Optional[ModelAction] = Field(None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class IntentClassification(BaseModel):
    """Clasificación de intención del usuario"""
    intent: str = Field(..., description="Intención detectada")
    confidence: float = Field(..., description="Confianza de la clasificación")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Entidades extraídas")
    requires_model: bool = Field(..., description="Si requiere ejecutar un modelo")
    suggested_action: Optional[ModelAction] = Field(None)

class ChatbotResponse(BaseModel):
    """Respuesta completa del chatbot"""
    message: str = Field(..., description="Mensaje de respuesta")
    type: ChatMessageType = Field(default=ChatMessageType.ASSISTANT_RESPONSE)
    model_results: Optional[ModelResponse] = Field(None, description="Resultados de modelo si aplica")
    suggestions: List[str] = Field(default_factory=list, description="Sugerencias para el usuario")
    quick_actions: List[Dict[str, str]] = Field(default_factory=list, description="Acciones rápidas")
    requires_confirmation: bool = Field(default=False, description="Si requiere confirmación del usuario")
    
class ErrorResponse(BaseModel):
    """Respuesta de error"""
    error_code: str = Field(..., description="Código de error")
    error_message: str = Field(..., description="Mensaje de error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalles adicionales")
    suggestions: List[str] = Field(default_factory=list, description="Sugerencias para resolver")

# Esquema de comunicación específico
class ChatCommunicationProtocol:
    """Protocolo de comunicación entre chatbot y backend"""
    
    @staticmethod
    def create_model_request(user_message: str, session_id: str, context: ChatContext) -> ModelRequest:
        """Crea una solicitud de modelo basada en el mensaje del usuario"""
        # Aquí iría la lógica de procesamiento de lenguaje natural
        # Por ahora, implementamos una versión simplificada
        
        # Detección de intenciones básicas
        if "predic" in user_message.lower() or "demanda" in user_message.lower():
            return ModelRequest(
                action=ModelAction.PREDICT_DEMAND,
                parameters={"dias_adelante": 7},
                context=user_message,
                user_intent="prediction"
            )
        elif "compar" in user_message.lower() or "modelo" in user_message.lower():
            return ModelRequest(
                action=ModelAction.COMPARE_MODELS,
                parameters={},
                context=user_message,
                user_intent="comparison"
            )
        elif "inventario" in user_message.lower() or "stock" in user_message.lower():
            return ModelRequest(
                action=ModelAction.GET_INVENTORY_STATUS,
                parameters={},
                context=user_message,
                user_intent="inventory"
            )
        else:
            return ModelRequest(
                action=ModelAction.GENERATE_REPORT,
                parameters={"type": "general"},
                context=user_message,
                user_intent="general"
            )
    
    @staticmethod
    def format_model_response(model_response: ModelResponse, user_intent: str) -> ChatbotResponse:
        """Formatea la respuesta del modelo para el chatbot"""
        if model_response.success:
            if model_response.action == ModelAction.PREDICT_DEMAND:
                predictions = model_response.data.get('predicciones', [])
                message = f"📈 Predicción de demanda:\n"
                message += f"• Promedio próximos días: {sum(predictions)/len(predictions):.1f} unidades\n"
                message += f"• Modelo usado: {model_response.data.get('mejor_modelo', 'N/A')}\n"
                message += f"• Confianza: {model_response.confidence*100:.1f}%"
                
                suggestions = [
                    "¿Quieres ver la comparación de modelos?",
                    "¿Te interesa analizar las tendencias?",
                    "¿Necesitas optimizar el inventario?"
                ]
                
            elif model_response.action == ModelAction.COMPARE_MODELS:
                best_model = model_response.data.get('mejor_modelo', 'N/A')
                r2_score = model_response.data.get('mejor_r2', 0)
                message = f"🔍 Comparación de modelos:\n"
                message += f"• Mejor modelo: {best_model}\n"
                message += f"• Precisión (R²): {r2_score:.3f}\n"
                message += f"• Tiempo de ejecución: {model_response.execution_time:.2f}s"
                
                suggestions = [
                    "¿Quieres hacer una predicción con este modelo?",
                    "¿Te gustaría ver más detalles técnicos?",
                    "¿Necesitas entrenar un nuevo modelo?"
                ]
                
            else:
                message = model_response.message
                suggestions = model_response.recommendations
            
            return ChatbotResponse(
                message=message,
                model_results=model_response,
                suggestions=suggestions,
                quick_actions=[
                    {"text": "Nueva predicción", "action": "predict"},
                    {"text": "Comparar modelos", "action": "compare"},
                    {"text": "Ver inventario", "action": "inventory"}
                ]
            )
        else:
            return ChatbotResponse(
                message=f"❌ Error al ejecutar {model_response.action}: {model_response.message}",
                type=ChatMessageType.ERROR,
                suggestions=[
                    "Intenta reformular tu pregunta",
                    "Verifica los parámetros ingresados",
                    "Contacta al administrador si persiste el error"
                ]
            )

# Utilidades para el procesamiento
class MessageProcessor:
    """Procesador de mensajes del chat"""
    
    @staticmethod
    def extract_entities(message: str) -> Dict[str, Any]:
        """Extrae entidades del mensaje (producto_id, fechas, etc.)"""
        import re
        entities = {}
        
        # Extraer IDs de producto
        product_ids = re.findall(r'producto\s*(\d+)|id\s*(\d+)', message.lower())
        if product_ids:
            entities['producto_id'] = int(product_ids[0][0] or product_ids[0][1])
        
        # Extraer números de días
        days = re.findall(r'(\d+)\s*días?', message.lower())
        if days:
            entities['dias'] = int(days[0])
        
        # Extraer rangos de fechas
        dates = re.findall(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}', message)
        if dates:
            entities['fechas'] = dates
        
        return entities
    
    @staticmethod
    def classify_intent(message: str) -> IntentClassification:
        """Clasifica la intención del mensaje"""
        message_lower = message.lower()
        
        # Palabras clave para diferentes intenciones
        prediction_keywords = ['predic', 'demanda', 'forecast', 'estima', 'proyecc']
        comparison_keywords = ['compar', 'modelo', 'mejor', 'evalua', 'rendimiento']
        inventory_keywords = ['inventario', 'stock', 'almacen', 'existencia']
        analysis_keywords = ['analiz', 'tendencia', 'reporte', 'estadistica']
        
        # Calcular scores
        prediction_score = sum(1 for keyword in prediction_keywords if keyword in message_lower)
        comparison_score = sum(1 for keyword in comparison_keywords if keyword in message_lower)
        inventory_score = sum(1 for keyword in inventory_keywords if keyword in message_lower)
        analysis_score = sum(1 for keyword in analysis_keywords if keyword in message_lower)
        
        scores = {
            'prediction': prediction_score,
            'comparison': comparison_score,
            'inventory': inventory_score,
            'analysis': analysis_score
        }
        
        # Determinar intención principal
        max_intent = max(scores, key=scores.get)
        max_score = scores[max_intent]
        
        if max_score == 0:
            return IntentClassification(
                intent="general",
                confidence=0.5,
                entities=MessageProcessor.extract_entities(message),
                requires_model=False
            )
        
        confidence = min(max_score / len(message.split()) * 5, 1.0)  # Normalizar confianza
        
        # Mapear intenciones a acciones
        intent_to_action = {
            'prediction': ModelAction.PREDICT_DEMAND,
            'comparison': ModelAction.COMPARE_MODELS,
            'inventory': ModelAction.GET_INVENTORY_STATUS,
            'analysis': ModelAction.ANALYZE_TRENDS
        }
        
        return IntentClassification(
            intent=max_intent,
            confidence=confidence,
            entities=MessageProcessor.extract_entities(message),
            requires_model=True,
            suggested_action=intent_to_action.get(max_intent)
        )
