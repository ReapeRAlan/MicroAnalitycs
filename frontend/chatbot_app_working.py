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
            'algoritmo mejor', 'ml accuracy'
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
        if any(phrase in user_input_lower for phrase in ['comparar modelos', 'qué modelo', 'cuál modelo', 'mejor modelo']):
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
            'qué piensas'
        ]
        
        user_lower = user_input.lower()
        return any(pattern in user_lower for pattern in follow_up_patterns)

    def _get_contextual_response(self, user_input: str) -> str:
        """Generar respuesta contextual basada en resultados anteriores"""
        last_action = st.session_state.tool_results.get('last_action')
        last_results = st.session_state.tool_results.get('last_results')
        
        if not last_action or not last_results:
            return self._get_intelligent_fallback(user_input)
        
        user_lower = user_input.lower()
        
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

    def _generate_category_analysis(self, category: str, user_input: str) -> str:
        """Generar análisis de tendencias para una categoría específica"""
        import numpy as np
        
        # Generar datos simulados para la categoría
        np.random.seed(hash(category) % 1000)
        
        # Simular tendencias de los últimos 6 meses
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio']
        base_sales = np.random.randint(1000, 5000)
        
        # Generar tendencia (creciente, decreciente o estable)
        trend_type = np.random.choice(['creciente', 'decreciente', 'estable'])
        
        sales_data = []
        for i in range(6):
            if trend_type == 'creciente':
                variation = 1 + (i * 0.1) + np.random.uniform(-0.05, 0.05)
            elif trend_type == 'decreciente':
                variation = 1 - (i * 0.08) + np.random.uniform(-0.05, 0.05)
            else:  # estable
                variation = 1 + np.random.uniform(-0.1, 0.1)
            
            sales_data.append(int(base_sales * variation))
        
        # Calcular estadísticas
        avg_sales = np.mean(sales_data)
        growth_rate = ((sales_data[-1] - sales_data[0]) / sales_data[0]) * 100
        
        trend_color = "#1b5e20" if growth_rate > 5 else "#d32f2f" if growth_rate < -5 else "#f57c00"
        trend_bg = "#e8f5e8" if growth_rate > 5 else "#ffebee" if growth_rate < -5 else "#fff3e0"
        
        interpretation = f"""
        <div style="background-color: #ffffff; padding: 20px; border-radius: 12px; border: 2px solid #e0e0e0; color: #000000;">
        
        ## 📈 Análisis de Tendencias: {category.title()}
        
        **Consulta analizada:** "{user_input}"
        
        ### 📊 Resumen Ejecutivo
        
        <div style="background-color: {trend_bg}; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid {trend_color.replace('#', '').replace('1b5e20', '#4caf50').replace('d32f2f', '#f44336').replace('f57c00', '#ff9800')};">
        <strong style="color: {trend_color};">Tendencia General: {trend_type.title()}</strong><br>
        <strong style="color: #000000;">Crecimiento: {growth_rate:+.1f}%</strong><br>
        <strong style="color: #000000;">Ventas Promedio: {avg_sales:,.0f} unidades/mes</strong>
        </div>
        
        ### 📅 Datos Históricos (Últimos 6 Meses)
        
        """
        
        for i, (month, sales) in enumerate(zip(months, sales_data)):
            change = ""
            if i > 0:
                change_pct = ((sales - sales_data[i-1]) / sales_data[i-1]) * 100
                change_color = "#1b5e20" if change_pct > 0 else "#d32f2f"
                change = f" <span style='color: {change_color}; font-weight: bold;'>({change_pct:+.1f}%)</span>"
            
            interpretation += f"- **{month}**: <span style='color: #000000; font-weight: bold;'>{sales:,} unidades</span>{change}\n"
        
        interpretation += f"""
        
        ### 🔍 Insights Clave
        
        """
        
        if trend_type == 'creciente':
            interpretation += f"""
        - 📈 **Crecimiento sostenido**: La categoría {category} muestra una tendencia positiva
        - 🎯 **Oportunidad**: Considera aumentar inventario gradualmente
        - 💡 **Estrategia**: Aprovecha el momentum con campañas de marketing
        """
        elif trend_type == 'decreciente':
            interpretation += f"""
        - 📉 **Declive observado**: La categoría {category} está perdiendo tracción
        - ⚠️ **Alerta**: Revisa estrategias de precio y promoción
        - 🔄 **Acción**: Considera diversificar o renovar productos
        """
        else:
            interpretation += f"""
        - 📊 **Estabilidad**: La categoría {category} mantiene ventas consistentes
        - 🎯 **Oportunidad**: Mercado maduro ideal para optimización
        - 💡 **Estrategia**: Enfócate en eficiencia y márgenes
        """
        
        interpretation += f"""
        
        ### 💡 Recomendaciones Específicas
        
        <div style="background-color: #f3e5f5; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #9c27b0; color: #4a148c; font-weight: 600;">
        🎯 **Próximos pasos:** Usa predicciones específicas por producto para planificar inventario
        </div>
        
        <div style="background-color: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; border: 2px solid #2196f3; color: #0d47a1; font-weight: 600;">
        📊 **Tip:** Pregunta "¿Cuál será la demanda del producto X en los próximos 30 días?" para análisis específico
        </div>
        
        </div>
        """
        
        return interpretation

    def _handle_general_chat(self, user_input: str) -> str:
        """Manejar chat general con Ollama"""
        try:
            # Si hay cliente Ollama disponible, usar IA para responder
            if self.ollama_client:
                # Crear contexto sobre las herramientas disponibles
                system_context = """
                Eres un asistente especializado en predicción de demanda y análisis de micronegocios.
                
                HERRAMIENTAS DISPONIBLES:
                1. Predicción de demanda: Puedo predecir la demanda futura de productos específicos
                2. Comparación de modelos: Puedo comparar diferentes modelos de ML para encontrar el más preciso
                3. Análisis de tendencias: Puedo analizar patrones en los datos históricos
                4. Reportes de inventario: Puedo generar reportes sobre estado del inventario
                
                IMPORTANTE: 
                - Si el usuario pregunta sobre predicciones, demanda, ventas futuras o productos específicos, sugiere usar las herramientas de predicción
                - Si pregunta sobre modelos o precisión, sugiere comparar modelos
                - Para conversación general, responde de manera amigable y útil
                - Siempre ofrece ayuda específica relacionada con el negocio
                
                Responde de manera conversacional y útil. Si detectas que necesitan usar alguna herramienta específica, guíalos hacia esa funcionalidad.
                """
                
                # Usar asyncio para la llamada a Ollama
                try:
                    response = asyncio.run(self._get_ollama_response(user_input, system_context))
                    return response
                except Exception as e:
                    logger.warning(f"Error con Ollama: {e}")
                    return self._get_intelligent_fallback(user_input)
            else:
                return self._get_intelligent_fallback(user_input)
                
        except Exception as e:
            return f"Disculpa, hubo un error procesando tu mensaje. ¿Podrías reformular tu pregunta?"

    async def _get_ollama_response(self, user_input: str, system_context: str) -> str:
        """Obtener respuesta de Ollama de manera asíncrona"""
        try:
            if not self.ollama_client:
                return self._get_intelligent_fallback(user_input)
            
            # Preparar el contexto de conversación
            conversation_context = self._build_conversation_context()
            
            # Crear el prompt completo
            full_prompt = f"""
            {system_context}
            
            CONTEXTO DE CONVERSACIÓN:
            {conversation_context}
            
            USUARIO: {user_input}
            
            ASISTENTE: """
            
            # Llamar a Ollama con los parámetros correctos
            response = await self.ollama_client.generate_response(
                prompt=full_prompt,
                session_id=self.session_id,
                include_ml_context=True,
                stream=False
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error en respuesta de Ollama: {e}")
            return self._get_intelligent_fallback(user_input)

    def _build_conversation_context(self) -> str:
        """Construir contexto de conversación enriquecido para Mistral"""
        if not st.session_state.messages:
            return "Esta es una nueva conversación."
        
        # Tomar los últimos 5 mensajes para contexto más rico
        recent_messages = st.session_state.messages[-5:] if len(st.session_state.messages) > 5 else st.session_state.messages
        
        context_parts = []
        
        # Construir contexto basado en mensajes
        for msg in recent_messages:
            role = "Usuario" if msg['role'] == 'user' else "Asistente"
            content = msg['content']
            
            # Limitar longitud del contenido para contexto
            content_summary = content[:200] + "..." if len(content) > 200 else content
            context_parts.append(f"{role}: {content_summary}")
        
        context = "\n".join(context_parts)
        
        # Agregar información sobre resultados recientes de herramientas
        tool_results = st.session_state.tool_results
        
        if (tool_results['recent_predictions'] or 
            tool_results['recent_comparisons'] or 
            tool_results['recent_analysis']):
            
            context += "\n\n=== RESULTADOS RECIENTES DE HERRAMIENTAS ==="
            
            # Predicciones recientes
            if tool_results['recent_predictions']:
                context += "\n\nPREDICCIONES REALIZADAS:"
                for pred in tool_results['recent_predictions'][-2:]:  # Últimas 2
                    context += f"\n- Producto {pred['producto_id']}: {pred['prediccion_promedio']:.1f} unidades, modelo {pred['modelo_usado']}, confianza {pred['confianza']:.1%}, tendencia {pred['tendencia']}"
            
            # Comparaciones recientes
            if tool_results['recent_comparisons']:
                context += "\n\nCOMPARACIONES DE MODELOS:"
                for comp in tool_results['recent_comparisons'][-1:]:  # Última comparación
                    context += f"\n- Modelo ganador: {comp['mejor_modelo']}"
                    context += f"\n- Conclusión: {comp['conclusion']}"
            
            # Análisis recientes
            if tool_results['recent_analysis']:
                context += "\n\nANÁLISIS REALIZADOS:"
                for analysis in tool_results['recent_analysis'][-1:]:
                    context += f"\n- Tipo: {analysis['tipo_analisis']} para {analysis['categoria']}"
            
            # Información sobre la última acción
            if tool_results['last_action']:
                context += f"\n\nÚLTIMA ACCIÓN: {tool_results['last_action']}"
        
        return context

    def _get_intelligent_fallback(self, user_input: str) -> str:
        """Respuesta inteligente de fallback basada en análisis del input"""
        user_input_lower = user_input.lower()
        
        # Saludos y conversación general
        if any(word in user_input_lower for word in ['hola', 'buenos', 'buenas', 'hey', 'hi']):
            return """¡Hola! 👋 Soy tu asistente de análisis de demanda para micronegocios. 

Puedo ayudarte con:
- 📊 **Predicciones de demanda** para productos específicos
- 🔍 **Comparación de modelos** para encontrar el más preciso
- 📈 **Análisis de tendencias** en tus datos de ventas
- 📋 **Reportes de inventario** y recomendaciones

¿En qué puedo ayudarte hoy?"""

        # Preguntas sobre capacidades
        elif any(word in user_input_lower for word in ['qué puedes', 'que haces', 'ayuda', 'help', 'capacidades']):
            return """🤖 **Mis Capacidades:**

**📊 Predicción de Demanda:**
- Predigo ventas futuras de productos específicos
- Uso múltiples modelos de ML para mayor precisión
- Proporciono intervalos de confianza

**🔍 Análisis Avanzado:**
- Comparo diferentes modelos para encontrar el más preciso
- Identifico tendencias y patrones estacionales
- Genero insights accionables para tu negocio

💡 **Ejemplos de lo que puedes preguntarme:**
- "¿Cuál será la demanda del producto 1 en los próximos 30 días?"
- "¿Qué modelo es más preciso para mis productos?"
- "Analiza las tendencias de ventas del último mes"

¿Qué te gustaría explorar?"""

        # Agradecimientos
        elif any(word in user_input_lower for word in ['gracias', 'thanks', 'thank you']):
            return """¡De nada! 😊 

Estoy aquí para ayudarte con el análisis de tu negocio. ¿Hay algo más en lo que pueda asistirte?

Recuerda que puedo:
- 📊 Generar predicciones de demanda
- 🔍 Comparar modelos de ML
- 📈 Analizar tendencias de ventas"""

        # Respuesta por defecto más inteligente
        else:
            # Detectar si menciona productos o números
            if any(word in user_input_lower for word in ['producto', 'item', 'artículo']) or any(char.isdigit() for char in user_input):
                return """Parece que mencionas productos específicos. 

Para ayudarte mejor, puedo:
- 📊 **Predecir demanda** de un producto específico
- 🔍 **Comparar modelos** para encontrar el más preciso
- 📈 **Analizar tendencias** de categorías

¿Podrías especificar qué tipo de análisis necesitas?

**Ejemplo:** "Predice la demanda del producto 1 para los próximos 30 días" """

            else:
                return """No estoy seguro de cómo ayudarte con esa consulta específica, pero puedo asistirte con:

🎯 **Análisis de Demanda:**
- Predicciones para productos específicos
- Comparación de modelos de ML
- Análisis de tendencias y patrones

💡 **Prueba preguntándome:**
- "¿Qué modelo es más preciso?"
- "Predice la demanda del producto X"
- "Analiza las tendencias de ventas"

¿En qué puedo ayudarte?"""

    def render_chat_input(self):
        """Renderizar input del chat"""
        try:
            # Input del usuario
            user_input = st.chat_input("Escribe tu consulta sobre predicción de demanda...")
            
            if user_input:
                # Agregar mensaje del usuario
                st.session_state.messages.append({
                    "role": "user",
                    "content": user_input,
                    "timestamp": datetime.now()
                })
                
                # Procesar mensaje y obtener respuesta
                response = self._process_user_message(user_input)
                
                # Agregar respuesta del asistente
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now()
                })
                
                st.rerun()
                
        except Exception as e:
            st.error(f"Error en chat input: {str(e)}")
            logger.error(f"Error en render_chat_input(): {e}")

    def run(self):
        """Ejecutar la aplicación principal"""
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

        try:
            self.render_sidebar()
            
            # Título principal
            st.title("🤖 MicroAnalytics - Chat de Predicción")
            st.markdown("*Análisis inteligente de demanda para micronegocios*")
            
            # Mostrar historial de chat
            for message in st.session_state.messages:
                self._render_message(message)
            
            # Input del usuario
            self.render_chat_input()
            
        except Exception as e:
            st.error(f"Error en la aplicación: {str(e)}")
            logger.error(f"Error en run(): {e}")


def main():
    """Función principal"""
    try:
        # Configurar logging
        logging.basicConfig(level=logging.INFO)
        
        # Crear y ejecutar la aplicación
        app = ChatbotFrontend()
        app.run()
        
    except Exception as e:
        st.error(f"Error crítico: {str(e)}")
        logger.error(f"Error crítico en main(): {e}")


if __name__ == "__main__":
    main()