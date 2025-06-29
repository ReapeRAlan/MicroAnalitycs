"""
Frontend para Ollama - Interfaz de Chat para Predicción de Demanda
================================================================

Aplicación Streamlit que proporciona una interfaz de usuario moderna
para interactuar con el sistema de predicción de demanda a través de Ollama.
"""

import streamlit as st
import asyncio
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importaciones básicas sin Ollama por ahora
try:
    from chatbot.communication_schema import (
        PredictionScope, ModelType, RequestType
    )
    OLLAMA_AVAILABLE = True
except ImportError as e:
    print(f"Ollama integration not available: {e}")
    OLLAMA_AVAILABLE = False
    # Definir enums básicos como fallback
    class PredictionScope:
        SINGLE_PRODUCT = "single_product"
        CATEGORY = "category" 
        BUSINESS = "business"
        MARKET = "market"
    
    class ModelType:
        AUTO_SELECT = "auto_select"
        LINEAR = "linear"
        POLYNOMIAL = "polynomial"


# Configuración de la página
# st.set_page_config(
#     page_title="MicroAnalytics - Chat de Predicción",
#     page_icon="🤖",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# CSS optimizado para máxima legibilidad y contraste
st.markdown("""
<style>
/* Reset y base */
.main {
    padding-top: 1rem;
}

/* Estilos base para mensajes del chat con contraste máximo */
.stChatMessage {
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
    font-size: 16px;
    line-height: 1.7;
    border: 2px solid transparent;
}

.user-message {
    background-color: #ffffff !important;
    border: 3px solid #1976d2 !important;
    color: #0d47a1 !important;
    font-weight: 600;
    box-shadow: 0 3px 10px rgba(25, 118, 210, 0.2);
}

.user-message strong {
    color: #0d47a1 !important;
    font-weight: 700;
}

.assistant-message {
    background-color: #ffffff !important;
    border: 3px solid #7b1fa2 !important;
    color: #212121 !important;
    box-shadow: 0 4px 15px rgba(123, 31, 162, 0.15);
}

/* Forzar color negro en todos los elementos del asistente */
.assistant-message,
.assistant-message *,
.assistant-message p,
.assistant-message div,
.assistant-message span,
.assistant-message li,
.assistant-message td,
.assistant-message th {
    color: #000000 !important;
    font-weight: 500 !important;
}

/* Títulos con contraste extremo */
.assistant-message h1,
.assistant-message h2,
.assistant-message h3,
.assistant-message h4,
.assistant-message h5,
.assistant-message h6 {
    color: #000000 !important;
    font-weight: 800 !important;
    margin: 20px 0 15px 0 !important;
    text-shadow: none !important;
    background-color: #e8eaf6 !important;
    padding: 8px 12px !important;
    border-radius: 6px !important;
    border-left: 4px solid #3f51b5 !important;
}

/* Texto enfatizado negro sólido */
.assistant-message strong,
.assistant-message b {
    color: #000000 !important;
    font-weight: 800 !important;
    background-color: #fff3e0 !important;
    padding: 2px 4px !important;
    border-radius: 3px !important;
}

/* Enlaces completamente visibles */
.assistant-message a {
    color: #000000 !important;
    text-decoration: underline !important;
    font-weight: 700 !important;
    background-color: #e3f2fd !important;
    padding: 2px 4px !important;
    border-radius: 3px !important;
}

/* Indicadores de confianza con contraste extremo */
.confidence-high { 
    color: #000000 !important; 
    font-weight: 900 !important;
    background-color: #c8e6c9 !important;
    padding: 6px 12px !important;
    border-radius: 6px !important;
    border: 3px solid #2e7d32 !important;
    text-shadow: none !important;
}

.confidence-medium { 
    color: #000000 !important; 
    font-weight: 900 !important;
    background-color: #ffe0b2 !important;
    padding: 6px 12px !important;
    border-radius: 6px !important;
    border: 3px solid #f57c00 !important;
    text-shadow: none !important;
}

.confidence-low { 
    color: #000000 !important; 
    font-weight: 900 !important;
    background-color: #ffcdd2 !important;
    padding: 6px 12px !important;
    border-radius: 6px !important;
    border: 3px solid #d32f2f !important;
    text-shadow: none !important;
}

/* Listas completamente negras */
.assistant-message ul,
.assistant-message ol {
    color: #000000 !important;
    margin: 15px 0 !important;
}

.assistant-message ul li,
.assistant-message ol li {
    color: #000000 !important;
    font-weight: 600 !important;
    margin: 8px 0 !important;
    padding-left: 10px !important;
}

.assistant-message ul li::marker,
.assistant-message ol li::marker {
    color: #000000 !important;
}

/* Código completamente visible */
.assistant-message code,
.assistant-message pre {
    background-color: #f5f5f5 !important;
    color: #000000 !important;
    border: 2px solid #666666 !important;
    border-radius: 4px !important;
    padding: 8px !important;
    font-weight: 600 !important;
}

/* Forzar estilos en todos los elementos de Streamlit */
div[data-testid="stMarkdown"],
div[data-testid="stMarkdown"] *,
.stMarkdown,
.stMarkdown *,
.st-emotion-cache-acwcvw,
.st-emotion-cache-acwcvw *,
.st-emotion-cache-1sdpuyj,
.st-emotion-cache-1sdpuyj * {
    color: #000000 !important;
    font-weight: 500 !important;
}

/* Selectores específicos para elementos problemáticos */
.assistant-message div[data-testid="stMarkdown"] p,
.assistant-message div[data-testid="stMarkdown"] div,
.assistant-message div[data-testid="stMarkdown"] span,
.assistant-message div[data-testid="stMarkdown"] li,
.assistant-message .stMarkdown p,
.assistant-message .stMarkdown div,
.assistant-message .stMarkdown span,
.assistant-message .stMarkdown li {
    color: #000000 !important;
    font-weight: 500 !important;
}

/* Sidebar mejorado */
.sidebar-section {
    margin-bottom: 30px;
    padding: 20px;
    background-color: #ffffff;
    border-radius: 10px;
    border: 2px solid #e0e0e0;
    color: #000000 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.sidebar-section * {
    color: #000000 !important;
}

/* Forzar todo a negro como último recurso */
.assistant-message [class*="st-emotion"],
.assistant-message [class*="e1rzn78k"],
.assistant-message [class*="erovr38"] {
    color: #000000 !important;
}

/* Asegurar que elementos específicos sean negros */
div.stChatMessage.assistant-message * {
    color: #000000 !important;
}

/* Override para cualquier clase que Streamlit pueda agregar */
.assistant-message [class] {
    color: #000000 !important;
}

/* Modo oscuro deshabilitado para máximo contraste */
@media (prefers-color-scheme: dark) {
    .assistant-message,
    .assistant-message * {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
}
</style>
""", unsafe_allow_html=True)


class ChatbotFrontend:
    """Clase principal para el frontend del chatbot"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"  # URL del backend FastAPI
        self.session_id = self._get_session_id()
        self.ollama_client = None
        self.interpreter = None
        
        # Inicializar estado de la sesión
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'prediction_history' not in st.session_state:
            st.session_state.prediction_history = []
        if 'current_context' not in st.session_state:
            st.session_state.current_context = {}
        if 'tool_results' not in st.session_state:
            st.session_state.tool_results = {
                'recent_predictions': [],
                'recent_comparisons': [],
                'recent_analysis': [],
                'last_action': None,
                'last_results': None
            }
    
    def _get_session_id(self) -> str:
        """Obtener o crear ID de sesión"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return st.session_state.session_id
    
    async def _init_ollama_client(self):
        """Inicializar cliente de Ollama con detección automática de modelos"""
        if not OLLAMA_AVAILABLE:
            logger.warning("Ollama integration no disponible")
            return False
            
        if self.ollama_client is None:
            try:
                from chatbot.ollama_integration import OllamaClient, OllamaConfig
                
                # URL fija de Ollama
                ollama_url = "https://3200-34-168-28-225.ngrok-free.app"
                
                # Crear configuración temporal para detectar modelos
                temp_config = OllamaConfig(
                    base_url=ollama_url,
                    model_name="llama3.2",  # Modelo por defecto
                    timeout=30,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                # Crear cliente temporal
                temp_client = OllamaClient(temp_config)
                
                # Detectar modelos disponibles
                available_models = await self._detect_available_models(temp_client, ollama_url)
                
                if not available_models:
                    logger.warning("No se pudieron detectar modelos en Ollama")
                    return False
                
                # Seleccionar el mejor modelo
                best_model = self._select_best_model(available_models)
                logger.info(f"Usando modelo: {best_model} de {available_models}")
                
                # Crear configuración final
                final_config = OllamaConfig(
                    base_url=ollama_url,
                    model_name=best_model,
                    timeout=120,
                    max_tokens=1000,
                    temperature=0.7
                )
                
                # Crear cliente final
                self.ollama_client = OllamaClient(final_config)
                
                # Verificar conexión final
                if await self.ollama_client.check_connection():
                    logger.info(f"Ollama conectado exitosamente con modelo {best_model}")
                    st.session_state.ollama_connected = True
                    st.session_state.ollama_model_used = best_model
                    return True
                else:
                    logger.warning("No se pudo conectar con Ollama")
                    self.ollama_client = None
                    return False
                    
            except ImportError as e:
                logger.error(f"Error importando Ollama (posiblemente falta aiohttp): {e}")
                return False
            except Exception as e:
                logger.error(f"Error inicializando Ollama: {e}")
                self.ollama_client = None
                return False
        
        return True

    async def _detect_available_models(self, client, base_url):
        """Detectar modelos disponibles en Ollama"""
        try:
            # Intentar importar aiohttp
            try:
                import aiohttp
            except ImportError:
                logger.error("aiohttp no está disponible. Instálalo con: pip install aiohttp")
                return []
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "ngrok-skip-browser-warning": "true",
                    "Content-Type": "application/json"
                }
                
                async with session.get(
                    f"{base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10),
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model.get('name', '').split(':')[0] for model in data.get('models', [])]
                        models = [m for m in models if m]  # Filtrar nombres vacíos
                        logger.info(f"Modelos detectados: {models}")
                        return models
                    else:
                        logger.warning(f"Error al obtener modelos: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error detectando modelos: {e}")
            # Fallback con modelos comunes
            return ['llama3.2', 'llama3.1', 'llama3']

    def _select_best_model(self, available_models):
        """Seleccionar el mejor modelo basado en prioridad"""
        # Prioridad de modelos (del mejor al menos preferido)
        priority_models = [
            'llama3.2',
            'llama3.1', 
            'llama3',
            'llama2',
            'codellama',
            'mistral',
            'gemma',
            'phi',
            'qwen'
        ]
        
        # Buscar el primer modelo de la lista de prioridad que esté disponible
        for preferred in priority_models:
            for available in available_models:
                if preferred.lower() in available.lower():
                    return available
        
        # Si no se encuentra ninguno preferido, usar el primero disponible
        if available_models:
            return available_models[0]
        
        # Fallback
        return "llama3.2"
    
    def render_sidebar(self):
        """Renderizar barra lateral con configuraciones"""
        st.sidebar.header("🤖 Configuración del Chat")
        
        with st.sidebar.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.subheader("🔗 Estado de Ollama")
            
            # Estado de conexión
            if st.session_state.get('ollama_connected', False):
                st.success(f"✅ Conectado - Modelo: {st.session_state.get('ollama_model_used', 'N/A')}")
            else:
                st.warning("⚠️ No conectado")
            
            # URL de Ollama (fija)
            st.info("🌐 URL: https://3200-34-168-28-225.ngrok-free.app")
            
            # Botón para reconectar
            if st.button("🔄 Reconectar Ollama"):
                self.ollama_client = None
                st.session_state.ollama_connected = False
                try:
                    connected = asyncio.run(self._init_ollama_client())
                    if connected:
                        st.success("✅ Reconectado exitosamente")
                        st.rerun()
                    else:
                        st.error("❌ Error al reconectar")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Configuración de predicciones
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.subheader("📊 Configuración de Predicciones")
            
            # Días para predicción
            prediction_days = st.slider(
                "Días a predecir",
                min_value=7,
                max_value=90,
                value=st.session_state.get('prediction_days', 30),
                step=7,
                help="Número de días hacia el futuro para las predicciones"
            )
            st.session_state.prediction_days = prediction_days
            
            # Incluir intervalos de confianza
            include_confidence = st.checkbox(
                "Incluir intervalos de confianza",
                value=st.session_state.get('include_confidence', True),
                help="Mostrar rangos de confianza en las predicciones"
            )
            st.session_state.include_confidence = include_confidence
            
            # Usar caché
            use_cache = st.checkbox(
                "Usar caché de modelos",
                value=st.session_state.get('use_cache', True),
                help="Acelerar predicciones usando modelos en caché"
            )
            st.session_state.use_cache = use_cache
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Historial de predicciones
        st.sidebar.header("� Historial")
        
        with st.sidebar.container():
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            
            # Alcance de predicción
            scope_options = {
                "Producto único": PredictionScope.SINGLE_PRODUCT,
                "Categoría": PredictionScope.CATEGORY,
                "Negocio": PredictionScope.BUSINESS,
                "Mercado": PredictionScope.MARKET
            }
            
            selected_scope = st.selectbox(
                "Alcance",
                options=list(scope_options.keys()),
                help="Alcance de la predicción"
            )
            st.session_state.prediction_scope = scope_options[selected_scope]
            
            # Días de predicción
            prediction_days = st.slider(
                "Días a predecir",
                min_value=1,
                max_value=365,
                value=30,
                help="Número de días hacia el futuro"
            )
            st.session_state.prediction_days = prediction_days
            
            # Tipo de modelo
            model_options = {
                "Auto-selección": ModelType.AUTO_SELECT,
                "Lineal": ModelType.LINEAR,
                "Polinomial": ModelType.POLYNOMIAL
            }
            
            selected_model_type = st.selectbox(
                "Tipo de modelo",
                options=list(model_options.keys()),
                help="Modelo de ML a utilizar"
            )
            st.session_state.model_type = model_options[selected_model_type]
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Historial de predicciones
        st.sidebar.header("📈 Historial")
        
        if st.session_state.prediction_history:
            for i, pred in enumerate(st.session_state.prediction_history[-5:]):
                with st.sidebar.expander(f"Predicción {i+1}"):
                    st.write(f"**Fecha:** {pred['timestamp']}")
                    st.write(f"**Confianza:** {pred['confidence']:.1%}")
                    st.write(f"**Modelo:** {pred['model']}")
        else:
            st.sidebar.info("No hay predicciones aún")
        
        # Limpiar historial
        if st.sidebar.button("🗑️ Limpiar Chat"):
            st.session_state.messages = []
            st.session_state.prediction_history = []
            st.rerun()
    
    def render_chat_interface(self):
        """Renderizar interfaz principal de chat"""
        st.header("🤖 Asistente de Predicción de Demanda")
        st.markdown("Pregunta sobre predicciones, análisis de tendencias y insights de tu negocio.")
        
        # Contenedor para mensajes
        chat_container = st.container()
        
        with chat_container:
            # Mostrar historial de mensajes
            for message in st.session_state.messages:
                self._render_message(message)
        
        # Input para nuevos mensajes
        user_input = st.chat_input("Escribe tu pregunta sobre predicción de demanda...")
        
        if user_input:
            # Agregar mensaje del usuario
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now()
            })
            
            # Procesar mensaje
            with st.spinner("Analizando y generando respuesta..."):
                response = self._process_user_message(user_input)
            
            # Agregar respuesta del asistente
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now()
            })
            
            st.rerun()
    
    def _render_message(self, message: Dict[str, Any]):
        """Renderizar un mensaje individual"""
        timestamp = message['timestamp'].strftime("%H:%M")
        
        if message['role'] == 'user':
            st.markdown(f"""
            <div class="stChatMessage user-message">
                <strong>Tú ({timestamp}):</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="stChatMessage assistant-message">
                <strong>Asistente ({timestamp}):</strong> {message['content']}
            </div>
            """, unsafe_allow_html=True)
            
            # Si hay datos de predicción, mostrar visualización
            if 'prediction_data' in message:
                self._render_prediction_visualization(message['prediction_data'])
    
    def _render_prediction_visualization(self, prediction_data: Dict[str, Any]):
        """Renderizar visualización de predicción"""
        try:
            if not prediction_data or 'predicciones' not in prediction_data:
                return
            
            # Crear gráfico simple con Plotly
            import plotly.graph_objects as go
            
            predicciones = prediction_data.get('predicciones', [])
            if not predicciones:
                return
                
            dias = list(range(1, len(predicciones) + 1))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dias,
                y=predicciones,
                mode='lines+markers',
                name='Predicción',
                line=dict(color='#1976d2', width=3),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title=f"Predicción para Producto {prediction_data.get('producto_id', 'N/A')}",
                xaxis_title="Días",
                yaxis_title="Demanda",
                height=400,
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.warning(f"Error renderizando visualización: {e}")

    def _process_user_message(self, user_input: str) -> str:
        """Procesar mensaje del usuario y generar respuesta"""
        
        # Intentar inicializar Ollama si no está disponible
        if not self.ollama_client and OLLAMA_AVAILABLE:
            try:
                # Usar asyncio.run para la inicialización
                asyncio.run(self._init_ollama_client())
            except Exception as e:
                logger.warning(f"No se pudo inicializar Ollama: {e}")
        
        # PRIMERO: Detectar si es una pregunta de seguimiento
        if self._detect_follow_up_question(user_input):
            logger.info(f"Pregunta de seguimiento detectada: {user_input}")
            return self._get_contextual_response(user_input)
        
        # SEGUNDO: Detectar intención del usuario para nuevas consultas
        intent = self._detect_intent(user_input)
        
        logger.info(f"Intent detectado: {intent} para input: {user_input}")
        
        # Manejar según la intención
        if intent == 'prediction':
            return self._handle_prediction_request(user_input)
        elif intent == 'comparison':
            return self._handle_model_comparison(user_input)
        elif intent == 'analysis':
            return self._handle_analysis_request(user_input)
        else:  # general
            return self._handle_general_chat(user_input)
    
    def _detect_intent(self, user_input: str) -> str:
        """Detectar la intención del usuario de manera más inteligente"""
        user_input_lower = user_input.lower()
        
        # Palabras clave más específicas para cada intención
        prediction_keywords = [
            'predecir', 'predicción', 'pronóstico', 'demanda', 'ventas futuras', 'futuro',
            'próximos', 'días', 'semanas', 'meses', 'cuánto', 'cuántos',
            'producto', 'cuál será', 'cuanto voy a vender', 'proyección',
            'estimación', 'forecast', 'prever', 'proyectar'
        ]
        
        # Palabras específicas para comparación (más restrictivas)
        comparison_keywords = [
            'comparar modelos', 'mejor modelo', 'qué modelo', 'cuál modelo',
            'modelo más preciso', 'modelo más exacto', 'accuracy', 'precisión del modelo',
            'performance modelo', 'rendimiento modelo', 'evaluar modelos',
            'algoritmo mejor', 'ml accuracy', 'que modelo es mejor', 'cual modelo es mejor',
            'modelo mejor', 'mejores modelos', 'compara modelos'
        ]
        
        # Palabras para análisis de tendencias
        analysis_keywords = [
            'analizar tendencia', 'tendencia de ventas', 'patrón', 'insight',
            'estudiar', 'examinar tendencia', 'revisar tendencia', 'investigar patrón',
            'reportar tendencia', 'reporte', 'análisis histórico', 'comportamiento',
            'categoría', 'análisis de categoría'
        ]
        
        # Conversación general
        general_keywords = [
            'hola', 'buenos', 'buenas', 'hey', 'hi', 'hello', 'qué haces',
            'que haces', 'gracias', 'thanks', 'ayuda', 'help', 'qué puedes',
            'capacidades', 'como funciona', 'cómo funciona'
        ]
        
        # Detección específica por frases exactas (mayor prioridad)
        comparison_phrases = [
            'comparar modelos', 'qué modelo', 'cuál modelo', 'mejor modelo',
            'que modelo es mejor', 'cual modelo es mejor', 'modelo mejor',
            'mejores modelos', 'compara modelos'
        ]
        
        if any(phrase in user_input_lower for phrase in comparison_phrases):
            return 'comparison'
        
        if any(phrase in user_input_lower for phrase in ['analizar tendencia', 'tendencia de', 'análisis de']):
            return 'analysis'
        
        # Buscar con números de producto (indica predicción)
        import re
        if re.search(r'producto\s+\d+', user_input_lower) or re.search(r'\d+\s+días?', user_input_lower):
            return 'prediction'
        
        if re.search(r'demanda.*producto', user_input_lower) or re.search(r'cuál será.*demanda', user_input_lower):
            return 'prediction'
        
        # Contar coincidencias por categoría
        prediction_count = sum(1 for keyword in prediction_keywords if keyword in user_input_lower)
        comparison_count = sum(1 for keyword in comparison_keywords if keyword in user_input_lower)
        analysis_count = sum(1 for keyword in analysis_keywords if keyword in user_input_lower)
        general_count = sum(1 for keyword in general_keywords if keyword in user_input_lower)
        
        # Decidir basado en la mayor cantidad de coincidencias
        counts = {
            'prediction': prediction_count,
            'comparison': comparison_count,
            'analysis': analysis_count,
            'general': general_count
        }
        
        max_count = max(counts.values())
        if max_count == 0:
            return 'general'  # Si no hay coincidencias claras, asumir conversación general
        
        # Retornar la intención con más coincidencias
        for intent, count in counts.items():
            if count == max_count:
                return intent
        
        return 'general'
    
    def _extract_product_id(self, user_input: str) -> int:
        """Extraer ID de producto del input del usuario"""
        import re
        
        # Buscar patrones como "producto 1", "producto X", etc.
        product_match = re.search(r'producto\s+(\d+)', user_input.lower())
        if product_match:
            return int(product_match.group(1))
        
        # Buscar números directos en el texto
        number_match = re.search(r'\b(\d+)\b', user_input)
        if number_match:
            return int(number_match.group(1))
        
        # Si no encuentra un ID específico, usar un ID por defecto basado en contexto
        user_lower = user_input.lower()
        if 'ropa' in user_lower or 'textil' in user_lower:
            return 1
        elif 'electronica' in user_lower or 'computadora' in user_lower:
            return 2
        elif 'comida' in user_lower or 'alimento' in user_lower:
            return 3
        elif 'hogar' in user_lower or 'casa' in user_lower:
            return 4
        elif 'deporte' in user_lower or 'fitness' in user_lower:
            return 5
        else:
            return 1  # ID por defecto

    def _save_tool_result(self, tool_type: str, result_data: Dict[str, Any], user_input: str):
        """Guardar resultados de herramientas para contexto futuro"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if tool_type == 'prediction':
            prediction_summary = {
                'timestamp': timestamp,
                'user_query': user_input,
                'producto_id': result_data.get('producto_id', 'N/A'),
                'prediccion_promedio': result_data.get('predicciones', [0])[-1] if result_data.get('predicciones') else 0,
                'modelo_usado': result_data.get('mejor_modelo', 'N/A'),
                'confianza': result_data.get('confianza', 0),
                'tendencia': result_data.get('trend_type', 'N/A'),
                'raw_data': result_data
            }
            st.session_state.tool_results['recent_predictions'].append(prediction_summary)
            # Mantener solo las últimas 3
            if len(st.session_state.tool_results['recent_predictions']) > 3:
                st.session_state.tool_results['recent_predictions'].pop(0)
        
        elif tool_type == 'comparison':
            comparison_summary = {
                'timestamp': timestamp,
                'user_query': user_input,
                'mejor_modelo': result_data.get('best_model', 'Random Forest'),
                'r2_scores': result_data.get('r2_scores', {}),
                'conclusion': result_data.get('conclusion', 'Comparación realizada'),
                'raw_data': result_data
            }
            st.session_state.tool_results['recent_comparisons'].append(comparison_summary)
            # Mantener solo las últimas 2
            if len(st.session_state.tool_results['recent_comparisons']) > 2:
                st.session_state.tool_results['recent_comparisons'].pop(0)
        
        elif tool_type == 'analysis':
            analysis_summary = {
                'timestamp': timestamp,
                'user_query': user_input,
                'tipo_analisis': result_data.get('analysis_type', 'general'),
                'categoria': result_data.get('category', 'N/A'),
                'insights': result_data.get('insights', []),
                'raw_data': result_data
            }
            st.session_state.tool_results['recent_analysis'].append(analysis_summary)
            # Mantener solo las últimas 2
            if len(st.session_state.tool_results['recent_analysis']) > 2:
                st.session_state.tool_results['recent_analysis'].pop(0)
        
        # Actualizar último resultado
        st.session_state.tool_results['last_action'] = tool_type
        st.session_state.tool_results['last_results'] = result_data

    def _detect_follow_up_question(self, user_input: str) -> bool:
        """Detectar si es una pregunta de seguimiento sobre resultados anteriores"""
        follow_up_patterns = [
            'qué puedes decir al respecto',
            'qué opinas sobre esto',
            'qué significa esto',
            'explícame esto',
            'analiza esto',
            'interpreta esto',
            'qué conclusiones',
            'qué recomendaciones',
            'basándote en esto',
            'sobre estos resultados',
            'sobre esta información',
            'que me dices de',
            'cómo interpretas',
            'qué piensas',
            'ejecuta el comando',
            'ejecuta eso',
            'hazlo',
            'ejecutalo',
            'realiza el comando',
            'corre el comando',
            'ejecuta para ver',
            'muestra el resultado',
            'dame los resultados'
        ]
        
        user_lower = user_input.lower()
        return any(pattern in user_lower for pattern in follow_up_patterns)

    def _get_contextual_response(self, user_input: str) -> str:
        """Generar respuesta contextual basada en resultados anteriores"""
        last_action = st.session_state.tool_results.get('last_action')
        last_results = st.session_state.tool_results.get('last_results')
        
        user_lower = user_input.lower()
        
        # Si el usuario pide ejecutar algo y no hay contexto previo, ejecutar herramienta apropiada
        if any(cmd in user_lower for cmd in ['ejecuta', 'ejecutalo', 'hazlo', 'muestra', 'realiza']):
            # Determinar qué ejecutar basado en el contexto de mensajes anteriores
            recent_messages = st.session_state.messages[-3:] if len(st.session_state.messages) >= 3 else st.session_state.messages
            
            for msg in reversed(recent_messages):
                if msg['role'] == 'user':
                    # Si el mensaje anterior mencionaba comparación
                    if any(word in msg['content'].lower() for word in ['modelo', 'comparar', 'mejor', 'preciso']):
                        return self._handle_model_comparison(f"comparar modelos para {msg['content']}")
                    # Si mencionaba análisis de categoría
                    elif any(word in msg['content'].lower() for word in ['ropa', 'tendencia', 'espera', 'categoria']):
                        return self._handle_analysis_request(msg['content'])
                    # Si mencionaba predicción
                    elif any(word in msg['content'].lower() for word in ['predic', 'demanda', 'futuro', 'venta']):
                        return self._handle_prediction_request(msg['content'])
        
        # Si hay contexto previo, analizarlo
        if not last_action or not last_results:
            return self._get_intelligent_fallback(user_input)
        
        if last_action == 'comparison':
            return self._analyze_model_comparison_context(user_input, last_results)
        elif last_action == 'prediction':
            return self._analyze_prediction_context(user_input, last_results)
        elif last_action == 'analysis':
            return self._analyze_analysis_context(user_input, last_results)
        
        return self._get_intelligent_fallback(user_input)

    def _analyze_model_comparison_context(self, user_input: str, comparison_data: Dict) -> str:
        """Analizar y explicar resultados de comparación de modelos"""
        try:
            # Obtener el último resultado de comparación
            recent_comp = st.session_state.tool_results['recent_comparisons'][-1] if st.session_state.tool_results['recent_comparisons'] else None
            
            if not recent_comp:
                return "No encontré resultados de comparación recientes para analizar."
            
            response = f"""
            <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #7b1fa2; color: #000000;">
            
            ## 🤔 Análisis de la Comparación de Modelos
            
            **Basándome en tu pregunta:** "{user_input}"
            
            ### 🎯 Interpretación de Resultados
            
            <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #4caf50; color: #1b5e20; font-weight: 600;">
            🏆 **Modelo Ganador:** {recent_comp['mejor_modelo']}
            </div>
            
            ### 📊 ¿Qué significan estos números?
            
            **R² Score (Coeficiente de Determinación):**
            - 📈 Mide qué tan bien el modelo explica la variabilidad de tus datos
            - 🎯 Rango: 0.0 (terrible) a 1.0 (perfecto)
            - ✅ **Mayor R² = Mejor predicción**
            
            **MSE (Error Cuadrático Medio):**
            - 📉 Promedio de errores al cuadrado
            - 🎯 **Menor MSE = Mejor precisión**
            
            **MAE (Error Absoluto Medio):**
            - 📊 Error promedio sin elevar al cuadrado
            - 🎯 **Menor MAE = Predicciones más cercanas**
            
            ### 💡 Recomendaciones Prácticas
            
            <div style="background-color: #f3e5f5; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #9c27b0; color: #4a148c; font-weight: 600;">
            🚀 **Para tu negocio:** El {recent_comp['mejor_modelo']} te dará las predicciones más confiables
            </div>
            
            **Próximos pasos sugeridos:**
            1. 📊 Usa el {recent_comp['mejor_modelo']} para predicciones futuras
            2. 🔄 Re-evalúa mensualmente con nuevos datos
            3. 📈 Monitora la precisión en la práctica
            
            ### 🤖 ¿Quieres que realice algún análisis específico?
            
            Puedo ayudarte con:
            - 📊 Predicción de demanda usando el mejor modelo
            - 📈 Análisis de tendencias específicas
            - 🎯 Recomendaciones personalizadas para tu inventario
            
            </div>
            """
            
            return response
            
        except Exception as e:
            return f"Error analizando la comparación: {str(e)}"

    def _analyze_prediction_context(self, user_input: str, prediction_data: Dict) -> str:
        """Analizar y explicar resultados de predicción"""
        try:
            recent_pred = st.session_state.tool_results['recent_predictions'][-1] if st.session_state.tool_results['recent_predictions'] else None
            
            if not recent_pred:
                return "No encontré predicciones recientes para analizar."
            
            response = f"""
            <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #1976d2; color: #000000;">
            
            ## 📊 Análisis de tu Predicción de Demanda
            
            **Respondiendo a:** "{user_input}"
            
            ### 🎯 Resumen de Resultados
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #1976d2; color: #0d47a1; font-weight: 600;">
            📦 **Producto {recent_pred['producto_id']}:** {recent_pred['prediccion_promedio']:.1f} unidades promedio
            </div>
            
            ### 🔍 Interpretación Detallada
            
            **Confianza del Modelo:**
            - 🎯 **{recent_pred['confianza']:.1%}** de confianza en la predicción
            - 🤖 Modelo usado: **{recent_pred['modelo_usado']}**
            - 📈 Tendencia detectada: **{recent_pred['tendencia']}**
            
            ### 💡 ¿Qué significa para tu negocio?
            
            **Planificación de Inventario:**
            """
            
            # Agregar recomendaciones basadas en la predicción
            prediccion = recent_pred['prediccion_promedio']
            if prediccion > 100:
                response += """
            <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #ff9800; color: #e65100; font-weight: 600;">
            🔥 **Alta demanda proyectada** - Considera aumentar tu inventario
            </div>
            """
            elif prediccion > 50:
                response += """
            <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #4caf50; color: #1b5e20; font-weight: 600;">
            ✅ **Demanda moderada** - Mantén niveles de stock normales
            </div>
            """
            else:
                response += """
            <div style="background-color: #fce4ec; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #e91e63; color: #880e4f; font-weight: 600;">
            📉 **Demanda baja** - Evalúa promociones o reducir inventario
            </div>
            """
            
            response += f"""
            ### 📋 Acciones Recomendadas
            
            1. 📊 **Stock óptimo:** {prediccion * 1.2:.0f} unidades (20% buffer)
            2. 🔄 **Punto de reorden:** {prediccion * 0.3:.0f} unidades
            3. 📅 **Próxima revisión:** En 1 semana
            
            ### 🤖 ¿Te ayudo con algo más?
            
            Puedo ayudarte a:
            - 🔍 Comparar con otros productos
            - 📈 Analizar tendencias históricas
            - 💰 Calcular rentabilidad proyectada
            
            </div>
            """
            
            return response
            
        except Exception as e:
            return f"Error analizando la predicción: {str(e)}"

    def _analyze_analysis_context(self, user_input: str, analysis_data: Dict) -> str:
        """Analizar y explicar resultados de análisis general"""
        try:
            recent_analysis = st.session_state.tool_results['recent_analysis'][-1] if st.session_state.tool_results['recent_analysis'] else None
            
            if not recent_analysis:
                return "No encontré análisis recientes para interpretar."
            
            response = f"""
            <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #ff9800; color: #000000;">
            
            ## 📈 Interpretación del Análisis
            
            **Tu consulta:** "{user_input}"
            
            ### 🎯 Resumen del Análisis Realizado
            
            <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #ff9800; color: #e65100; font-weight: 600;">
            📊 **Tipo:** {recent_analysis['tipo_analisis']} | **Categoría:** {recent_analysis['categoria']}
            </div>
            
            ### 💡 Insights Clave
            """
            
            for insight in recent_analysis.get('insights', [])[:3]:  # Mostrar máximo 3
                response += f"""
            - 🎯 {insight}
            """
            
            response += """
            
            ### 🚀 Próximos Pasos Sugeridos
            
            1. 📊 Monitorear tendencias identificadas
            2. 🔄 Ajustar estrategias según insights
            3. 📈 Revisar resultados en 2 semanas
            
            ### 🤖 ¿Necesitas más detalles?
            
            Puedo profundizar en:
            - 📊 Análisis específicos por producto
            - 🔍 Comparaciones detalladas
            - 💡 Recomendaciones personalizadas
            
            </div>
            """
            
            return response
            
        except Exception as e:
            return f"Error analizando el análisis: {str(e)}"

    def _handle_prediction_request(self, user_input: str) -> str:
        """Manejar solicitud de predicción"""
        try:
            # Extraer parámetros de la sesión
            product_id = self._extract_product_id(user_input)
            
            # Crear petición (formato compatible con backend)
            request_data = {
                "producto_id": product_id,
                "dias_adelante": st.session_state.get('prediction_days', 30),
                "include_confidence": True,
                "use_cache": True
            }
            
            # Intentar llamar al backend
            try:
                response = requests.post(
                    f"{self.backend_url}/api/predict/demanda",
                    json=request_data,
                    timeout=5  # Timeout corto para demo
                )
                
                if response.status_code == 200:
                    prediction_data = response.json()
                    
                    # Guardar en historial
                    st.session_state.prediction_history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "confidence": prediction_data.get('confianza', 0),
                        "model": prediction_data.get('mejor_modelo', 'unknown'),
                        "data": prediction_data
                    })
                    
                    # Guardar resultado para contexto futuro
                    self._save_tool_result('prediction', prediction_data, user_input)
                    
                    # Generar respuesta interpretativa
                    return self._generate_prediction_interpretation(prediction_data, user_input)
                else:
                    # Backend responde pero hay error, usar datos simulados
                    return self._generate_demo_prediction(product_id, user_input)
                    
            except (requests.RequestException, requests.Timeout):
                # Backend no disponible, usar datos simulados
                return self._generate_demo_prediction(product_id, user_input)
                
        except Exception as e:
            return f"Error procesando predicción: {str(e)}"
    
    def _generate_demo_prediction(self, product_id: int, user_input: str) -> str:
        """Generar predicción de demostración cuando el backend no está disponible"""
        import numpy as np
        import hashlib
        
        # Usar hash del input para generar datos únicos pero consistentes
        seed_value = int(hashlib.md5(f"{product_id}_{user_input}".encode()).hexdigest()[:8], 16) % 10000
        np.random.seed(seed_value)
        
        days = st.session_state.get('prediction_days', 30)
        
        # Crear predicción simulada más variada
        base_demand = 30 + (product_id % 20) * 5 + np.random.randint(-10, 20)
        
        # Diferentes tipos de tendencia basados en el producto
        trend_types = ['creciente', 'decreciente', 'estacional', 'estable']
        trend_type = trend_types[product_id % 4]
        
        predicted_values = []
        for i in range(days):
            if trend_type == 'creciente':
                trend_value = base_demand + (i * 0.5) + np.random.normal(0, 2)
            elif trend_type == 'decreciente':
                trend_value = base_demand - (i * 0.3) + np.random.normal(0, 2)
            elif trend_type == 'estacional':
                # Patrón semanal
                seasonal = 15 * np.sin(2 * np.pi * i / 7) + 5 * np.cos(2 * np.pi * i / 14)
                trend_value = base_demand + seasonal + np.random.normal(0, 3)
            else:  # estable
                trend_value = base_demand + np.random.normal(0, 4)
            
            value = max(1, int(trend_value))
            predicted_values.append(value)
        
        # Calcular métricas más realistas
        avg_demand = np.mean(predicted_values)
        trend = trend_type
        
        # Confidence basada en tipo de tendencia
        confidence_base = {
            'estable': 0.85,
            'creciente': 0.78,
            'decreciente': 0.72,
            'estacional': 0.68
        }
        
        confidence = confidence_base[trend_type] + np.random.uniform(-0.08, 0.08)
        confidence = max(0.6, min(0.95, confidence))
        
        # Seleccionar modelo basado en tendencia
        model_selection = {
            'estable': 'linear',
            'creciente': 'linear', 
            'decreciente': 'polynomial',
            'estacional': 'random_forest'
        }
        
        selected_model = model_selection[trend_type]
        
        prediction_data = {
            'predicciones': predicted_values,
            'confianza': confidence,
            'mejor_modelo': selected_model,
            'dias_adelante': days,
            'producto_id': product_id,
            'trend_type': trend_type
        }
        
        # Guardar resultados en el contexto de herramientas
        self._save_tool_result('prediction', prediction_data, user_input)
        
        # Guardar en historial
        st.session_state.prediction_history.append({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "confidence": confidence,
            "model": selected_model,
            "trend": trend_type,
            "data": prediction_data
        })
        
        # Agregar nota de demostración
        demo_note = "📍 **Modo Demo**: Datos simulados (backend en desarrollo)"
        interpretation = self._generate_prediction_interpretation(prediction_data, user_input)
        
        return f"{demo_note}\n\n{interpretation}"

    def _generate_prediction_interpretation(self, prediction_data: Dict[str, Any], user_input: str) -> str:
        """Generar interpretación detallada de la predicción"""
        try:
            product_id = prediction_data.get('producto_id', 'N/A')
            predictions = prediction_data.get('predicciones', [])
            confidence = prediction_data.get('confianza', 0)
            model = prediction_data.get('mejor_modelo', 'unknown')
            trend_type = prediction_data.get('trend_type', 'unknown')
            days = prediction_data.get('dias_adelante', 30)
            
            if not predictions:
                return "No se pudieron generar predicciones para este producto."
            
            avg_demand = sum(predictions) / len(predictions)
            max_demand = max(predictions)
            min_demand = min(predictions)
            
            # Determinar tendencia visual
            if len(predictions) >= 7:
                early_avg = sum(predictions[:7]) / 7
                late_avg = sum(predictions[-7:]) / 7
                trend_direction = "creciente" if late_avg > early_avg * 1.1 else "decreciente" if late_avg < early_avg * 0.9 else "estable"
            else:
                trend_direction = trend_type
            
            response = f"""
            <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #1976d2; color: #000000;">
            
            ## 📊 Predicción de Demanda - Producto {product_id}
            
            **Consulta:** "{user_input}"
            
            ### 🎯 Resumen Ejecutivo
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #1976d2; color: #0d47a1; font-weight: 600;">
            📦 **Demanda promedio**: {avg_demand:.1f} unidades diarias
            </div>
            
            ### 📈 Métricas Clave
            
            - 🎯 **Confianza del modelo**: {confidence:.1%}
            - 🤖 **Modelo utilizado**: {model.title()}
            - 📊 **Período analizado**: {days} días
            - 📈 **Tendencia**: {trend_direction.title()}
            - 📊 **Rango**: {min_demand:.0f} - {max_demand:.0f} unidades
            
            ### 💡 Interpretación de Resultados
            
            """
            
            # Recomendaciones basadas en la demanda promedio
            if avg_demand > 100:
                response += """
            <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #ff9800; color: #e65100; font-weight: 600;">
            🔥 **Alta Demanda Proyectada** - Este producto muestra excelente potencial de ventas
            </div>
            
            **Estrategia recomendada:**
            - 📈 **Aumentar inventario** inmediatamente
            - 🎯 **Stock objetivo**: {int(avg_demand * 1.5):.0f} unidades diarias
            - 🔄 **Punto de reorden**: {int(avg_demand * 0.7):.0f} unidades
            """
            elif avg_demand > 50:
                response += """
            <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #4caf50; color: #1b5e20; font-weight: 600;">
            ✅ **Demanda Moderada** - Mantén niveles de stock normales
            </div>
            
            **Estrategia recomendada:**
            - 📊 **Mantener niveles actuales** de inventario
            - 🎯 **Stock objetivo**: {int(avg_demand * 1.3):.0f} unidades diarias
            - 🔄 **Punto de reorden**: {int(avg_demand * 0.5):.0f} unidades
            """
            else:
                response += """
            <div style="background-color: #fce4ec; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #e91e63; color: #880e4f; font-weight: 600;">
            📉 **Demanda Baja** - Evalúa promociones o reducir inventario
            </div>
            
            **Estrategia recomendada:**
            - 🎯 **Evaluar promociones** o descuentos
            - 📦 **Reducir inventario** gradualmente
            - 🔍 **Investigar** factores que afectan la demanda
            """
            
            # Recomendaciones basadas en tendencia
            if trend_direction == "creciente":
                response += """
            - 📈 **Tendencia creciente**: Prepárate para mayor demanda
            - 🚀 **Oportunidad**: Considera expandir la línea de productos similares
            """
            elif trend_direction == "decreciente":
                response += """
            - 📉 **Tendencia decreciente**: Ajusta estrategias de marketing
            - 🔄 **Acción**: Evalúa factores estacionales o competencia
            """
            else:
                response += """
            - 📊 **Tendencia estable**: Demanda predecible y confiable
            - ✅ **Ventaja**: Fácil planificación de inventario
            """
            
            response += f"""
            
            ### 📋 Plan de Acción Recomendado
            
            1. **📊 Monitoreo semanal** de las ventas reales vs predicción
            2. **🔄 Ajuste de inventario** según la tendencia observada
            3. **📅 Revisión en 2 semanas** para evaluar precisión del modelo
            4. **🎯 Optimización** basada en los resultados obtenidos
            
            ### 🤖 ¿Necesitas más análisis?
            
            Puedo ayudarte con:
            - 🔍 **Comparar con otros productos** de tu inventario
            - 📈 **Analizar tendencias** por categoría
            - 💰 **Calcular rentabilidad** proyectada
            
            </div>
            """
            
            return response
            
        except Exception as e:
            return f"Error generando interpretación de predicción: {str(e)}"

    def _generate_comparison_interpretation(self, comparison_data: Dict[str, Any], user_input: str) -> str:
        """Generar interpretación detallada de la comparación de modelos"""
        try:
            response = f"""
            <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #7b1fa2; color: #000000;">
            
            ## 🔍 Análisis Detallado de Comparación de Modelos
            
            **Consulta:** "{user_input}"
            
            ### 🏆 Resultado de la Comparación
            
            Basándome en los datos de rendimiento, he evaluado los siguientes modelos de Machine Learning:
            
            """
            
            # Si hay datos específicos de comparación, usarlos
            if comparison_data and 'models' in comparison_data:
                for model_name, metrics in comparison_data['models'].items():
                    response += f"""
            **🤖 {model_name.title()}:**
            - R² Score: {metrics.get('r2', 0):.3f}
            - MSE: {metrics.get('mse', 0):.3f}  
            - MAE: {metrics.get('mae', 0):.3f}
            """
            
            response += """
            
            ### 📊 ¿Qué significan estas métricas?
            
            **R² Score (Coeficiente de Determinación):**
            - 📈 Mide qué tan bien explica el modelo la variabilidad de tus datos
            - 🎯 Rango: 0.0 (malo) a 1.0 (perfecto)
            - ✅ **Mayor R² = Mejor capacidad predictiva**
            
            **MSE (Error Cuadrático Medio):**
            - 📉 Penaliza más los errores grandes
            - 🎯 **Menor MSE = Mayor precisión**
            
            **MAE (Error Absoluto Medio):**
            - 📊 Error promedio en términos absolutos
            - 🎯 **Menor MAE = Predicciones más cercanas**
            
            ### 💡 Recomendación para tu Negocio
            
            <div style="background-color: #f3e5f5; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #9c27b0; color: #4a148c; font-weight: 600;">
            🚀 **Usa el modelo con mayor R²** para tus predicciones futuras
            </div>
            
            ### 🎯 Guía de Selección por Caso de Uso
            
            - **Linear**: ⚡ Ideal para tendencias simples y respuesta rápida
            - **Polynomial**: 🔄 Mejor para patrones con curvas y estacionalidad
            - **Random Forest**: 🎯 Máxima precisión para datos complejos
            
            ### 📋 Próximos Pasos Sugeridos
            
            1. **📊 Implementar** el modelo recomendado en tus predicciones
            2. **🔄 Monitorear** la precisión en datos reales durante 2 semanas
            3. **📈 Re-evaluar** mensualmente con datos nuevos
            4. **🎯 Ajustar** si la precisión baja del 80%
            
            </div>
            """
            
            return response
            
        except Exception as e:
            return f"Error generando interpretación de comparación: {str(e)}"

    def _handle_model_comparison(self, user_input: str) -> str:
        """Manejar comparación de modelos con fallback inteligente"""
        try:
            # Intentar obtener comparación del backend
            comparison_id = f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            response = requests.get(
                f"{self.backend_url}/api/predict/models/comparison/{comparison_id}",
                timeout=5  # Timeout corto
            )
            
            if response.status_code == 200:
                comparison_data = response.json()
                
                # Guardar resultado para contexto futuro
                self._save_tool_result('comparison', comparison_data, user_input)
                
                return self._generate_comparison_interpretation(comparison_data, user_input)
            else:
                # Si falla el backend, generar comparación simulada
                return self._generate_demo_comparison(user_input)
                
        except Exception as e:
            logger.warning(f"Error en comparación del backend: {e}")
            return self._generate_demo_comparison(user_input)

    def _generate_demo_comparison(self, user_input: str) -> str:
        """Generar comparación de modelos simulada"""
        import numpy as np
        
        # Datos simulados de comparación
        models_comparison = {
            'linear': {
                'mse': np.random.uniform(0.15, 0.25),
                'r2': np.random.uniform(0.75, 0.85),
                'mae': np.random.uniform(0.12, 0.18),
                'speed': 'Muy rápido',
                'complexity': 'Baja'
            },
            'polynomial': {
                'mse': np.random.uniform(0.10, 0.20),
                'r2': np.random.uniform(0.80, 0.90),
                'mae': np.random.uniform(0.08, 0.15),
                'speed': 'Moderado',
                'complexity': 'Media'
            },
            'random_forest': {
                'mse': np.random.uniform(0.08, 0.15),
                'r2': np.random.uniform(0.85, 0.95),
                'mae': np.random.uniform(0.06, 0.12),
                'speed': 'Lento',
                'complexity': 'Alta'
            }
        }
        
        # Encontrar el mejor modelo por R²
        best_model = max(models_comparison.keys(), key=lambda k: models_comparison[k]['r2'])
        
        # Guardar resultados en el contexto
        comparison_result = {
            'best_model': best_model.replace('_', ' ').title(),
            'r2_scores': {k: v['r2'] for k, v in models_comparison.items()},
            'models_data': models_comparison,
            'conclusion': f"{best_model.replace('_', ' ').title()} es el más preciso"
        }
        self._save_tool_result('comparison', comparison_result, user_input)
        
        interpretation = f"""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #e0e0e0; color: #000000;">
        
        ## 🔍 Comparación de Modelos de ML
        
        **Basándome en tu consulta:** "{user_input}"
        
        ### 🏆 Modelo Recomendado: **{best_model.replace('_', ' ').title()}**
        
        ### 📊 Resultados Detallados
        
        """
        
        for model, metrics in models_comparison.items():
            model_name = model.replace('_', ' ').title()
            r2_color = "#1b5e20" if metrics['r2'] > 0.85 else "#f57c00" if metrics['r2'] > 0.75 else "#d32f2f"
            
            interpretation += f"""
        **🤖 {model_name}:**
        - **R² Score**: <span style="color: {r2_color}; font-weight: bold; background-color: #f5f5f5; padding: 2px 6px; border-radius: 4px;">{metrics['r2']:.3f}</span>
        - **MSE**: <span style="color: #000000; font-weight: bold;">{metrics['mse']:.3f}</span>
        - **MAE**: <span style="color: #000000; font-weight: bold;">{metrics['mae']:.3f}</span>
        - **Velocidad**: <span style="color: #4a148c; font-weight: bold;">{metrics['speed']}</span>
        - **Complejidad**: <span style="color: #4a148c; font-weight: bold;">{metrics['complexity']}</span>
        
        """
        
        interpretation += f"""
        ### 💡 Recomendaciones
        
        <div style="background-color: #e8f5e8; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #4caf50; color: #1b5e20; font-weight: 600;">
        🎯 **Mejor opción:** {best_model.replace('_', ' ').title()} con R² de {models_comparison[best_model]['r2']:.3f}
        </div>
        
        <div style="background-color: #f3e5f5; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #9c27b0; color: #4a148c; font-weight: 600;">
        📈 **Criterio de selección:** Mayor R² indica mejor capacidad predictiva
        </div>
        
        ### 📋 Guía de Selección:
        - **Linear**: Ideal para tendencias simples y predicciones rápidas
        - **Polynomial**: Mejor para patrones más complejos
        - **Random Forest**: Máxima precisión para datos complejos
        
        </div>
        """
        
        return interpretation
    
    def _handle_analysis_request(self, user_input: str) -> str:
        """Manejar solicitud de análisis con capacidades mejoradas"""
        
        # Extraer información de la consulta
        category = self._extract_category_from_input(user_input)
        
        if category:
            return self._generate_category_analysis(category, user_input)
        else:
            return self._generate_general_analysis(user_input)
    
    def _extract_category_from_input(self, user_input: str) -> str:
        """Extraer categoría de producto del input del usuario"""
        user_input_lower = user_input.lower()
        
        categories = {
            'electronica': ['electronica', 'electronics', 'computadora', 'telefono', 'gadget'],
            'ropa': ['ropa', 'clothing', 'vestimenta', 'textil', 'fashion'],
            'comida': ['comida', 'food', 'alimento', 'bebida', 'restaurant'],
            'hogar': ['hogar', 'casa', 'home', 'domestico'],
            'deportes': ['deporte', 'sport', 'fitness', 'ejercicio'],
            'salud': ['salud', 'health', 'medicina', 'farmacia'],
            'belleza': ['belleza', 'beauty', 'cosmético', 'cuidado personal']
        }
        
        for category, keywords in categories.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return category
        
        return 'general'

    def _generate_category_analysis(self, category: str, user_input: str) -> str:
        """Generar análisis específico por categoría"""
        import numpy as np
        
        # Generar datos simulados para la categoría
        np.random.seed(hash(category) % 1000)
        
        # Simular tendencias de los últimos 6 meses
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio']
        base_sales = 1000 + hash(category) % 500
        
        monthly_data = []
        for i, month in enumerate(months):
            # Tendencia creciente con variación
            trend_factor = 1 + (i * 0.1) + np.random.uniform(-0.05, 0.05)
            sales = int(base_sales * trend_factor)
            monthly_data.append({'month': month, 'sales': sales})
        
        # Calcular insights
        total_sales = sum(data['sales'] for data in monthly_data)
        avg_growth = (monthly_data[-1]['sales'] - monthly_data[0]['sales']) / monthly_data[0]['sales'] * 100
        
        response = f"""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #ff9800; color: #000000;">
        
        ## 📈 Análisis de Tendencias - Categoría: {category.title()}
        
        **📍 Modo Demo**: Datos simulados para demostración
        
        ### 📊 Resumen Ejecutivo
        
        <div style="background-color: #fff3e0; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #ff9800; color: #e65100; font-weight: 600;">
        📈 **Crecimiento promedio:** {avg_growth:.1f}% en los últimos 6 meses
        </div>
        
        ### 📅 Tendencias Mensuales Recientes
        
        """
        
        for data in monthly_data[-3:]:  # Últimos 3 meses
            response += f"- **{data['month']}**: {data['sales']:,} unidades vendidas\n"
        
        response += f"""
        
        ### 💡 Insights Clave para {category.title()}
        
        - 🎯 **Demanda estacional**: {category.title()} muestra patrones predecibles
        - 📊 **Volumen total**: {total_sales:,} unidades en 6 meses  
        - 🔄 **Estrategia**: {"📈 Aumentar inventario - tendencia creciente" if avg_growth > 5 else "📊 Mantener niveles actuales - demanda estable"}
        - 💰 **Oportunidad**: {"Alto potencial de crecimiento" if avg_growth > 10 else "Mercado estable y confiable"}
        
        ### 🚀 Recomendaciones Específicas
        
        1. **📊 Stock óptimo**: {int(monthly_data[-1]['sales'] * 1.3):,} unidades (30% buffer)
        2. **🎯 Punto de reorden**: {int(monthly_data[-1]['sales'] * 0.4):,} unidades  
        3. **📅 Próxima revisión**: En 2 semanas
        4. **� Monitoreo**: Tendencias semanales por subcategoría
        
        ### 🤖 ¿Necesitas algo más específico?
        
        Puedo ayudarte con:
        - 📊 **Predicción específica**: "Predice la demanda para el producto X"
        - � **Comparar modelos**: "¿Qué modelo es más preciso?"
        - 📈 **Análisis detallado**: "Analiza otra categoría"
        
        </div>
        """
        
        # Guardar en contexto
        analysis_data = {
            'analysis_type': 'category_trends',
            'category': category,
            'insights': [
                f"Crecimiento del {avg_growth:.1f}% en 6 meses",
                f"Volumen total: {total_sales:,} unidades",
                "Patrones estacionales detectados"
            ]
        }
        self._save_tool_result('analysis', analysis_data, user_input)
        
        return response

    def _generate_general_analysis(self, user_input: str) -> str:
        """Generar análisis general cuando no se detecta categoría específica"""
        
        response = f"""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #9c27b0; color: #000000;">
        
        ## 🔍 Análisis General de Tendencias
        
        **Tu consulta:** "{user_input}"
        
        ### 📊 Insights Disponibles
        
        Para brindarte un análisis más específico, puedo ayudarte con:
        
        **Por Categoría:**
        - 👕 Ropa y Fashion
        - 💻 Electrónicos
        - 🍕 Alimentos y Bebidas
        - 🏠 Hogar y Decoración
        - 💪 Deportes y Fitness
        
        **Por Producto:**
        - 📊 Predicciones específicas
        - 📈 Análisis de tendencias históricas
        - 🔍 Comparación con competencia
        
        ### 💡 Recomendación
        
        <div style="background-color: #f3e5f5; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #9c27b0; color: #4a148c; font-weight: 600;">
        🎯 **Especifica una categoría** para obtener insights más detallados
        </div>
        
        **Ejemplos de consultas más específicas:**
        - "Analiza las tendencias de ropa"
        - "¿Cómo está el mercado de electrónicos?"
        - "Tendencias en comida rápida"
        
        </div>
        """
        
        return response

    def _extract_category_from_input(self, user_input: str) -> str:
        """Extraer categoría del input del usuario"""
        user_input_lower = user_input.lower()
        
        categories = {
            'electrónicos': ['electronico', 'electronica', 'electronic', 'tecnologia'],
            'ropa': ['ropa', 'vestimenta', 'clothing', 'textil'],
            'alimentación': ['alimento', 'comida', 'food', 'bebida'],
            'hogar': ['hogar', 'casa', 'home', 'domestico'],
            'deportes': ['deporte', 'sport', 'fitness', 'ejercicio'],
            'salud': ['salud', 'health', 'medicina', 'farmacia'],
            'belleza': ['belleza', 'beauty', 'cosmetico', 'maquillaje']
        }
        
        for category, keywords in categories.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return category
        
        return None

    def _generate_category_analysis