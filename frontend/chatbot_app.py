"""
Chatbot Frontend Integrado - Sistema Inteligente sin Ollama
==========================================================

Interfaz de chatbot inteligente integrada al flujo principal
que se conecta al backend y usa la base de datos real.
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any, List


class ChatbotFrontend:
    """Chatbot inteligente integrado al sistema principal"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.session_id = self._get_session_id()
        
        # Inicializar estado de la sesión
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = []
        if 'chatbot_ready' not in st.session_state:
            st.session_state.chatbot_ready = False
        if 'products_cache' not in st.session_state:
            st.session_state.products_cache = []
        if 'show_product_selector' not in st.session_state:
            st.session_state.show_product_selector = False
    
    def _get_session_id(self) -> str:
        """Obtener o crear ID de sesión"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return st.session_state.session_id
    
    def get_products_list(self) -> List[Dict[str, Any]]:
        """Obtener lista de productos del backend"""
        try:
            response = requests.get(f"{self.backend_url}/api/products", timeout=5)
            if response.status_code == 200:
                products = response.json()
                st.session_state.products_cache = products
                return products
            else:
                return st.session_state.products_cache
        except Exception:
            return st.session_state.products_cache
    
    def render_product_selector(self):
        """Renderizar selector interactivo de productos mejorado"""
        st.markdown("### 🎯 Selector Inteligente de Productos")
        
        products = self.get_products_list()
        
        if not products:
            st.warning("⚠️ No se pudieron cargar los productos. Verifica que el backend esté funcionando.")
            if st.button("🔄 Recargar Productos"):
                st.rerun()
            return
        
        # Crear opciones para el selectbox con más información
        product_options = {}
        for product in products:
            product_id = product.get('id', '?')
            product_name = product.get('nombre', f'Producto {product_id}')
            price = product.get('precio_base', 0)
            category = product.get('categoria', {}).get('nombre', 'Sin categoría') if isinstance(product.get('categoria'), dict) else 'Sin categoría'
            
            option_text = f"{product_name} - ${price:.2f} | {category} (ID: {product_id})"
            product_options[option_text] = product
        
        # Selector principal
        selected_option = st.selectbox(
            "🔍 Selecciona un producto:",
            options=list(product_options.keys()),
            key="product_selector",
            help="Elige un producto para analizar, predecir o comparar modelos"
        )
        
        if selected_option:
            selected_product = product_options[selected_option]
            product_id = selected_product.get('id')
            product_name = selected_product.get('nombre', f'Producto {product_id}')
            
            # Mostrar información del producto seleccionado
            with st.expander(f"📋 Información de {product_name}", expanded=False):
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.metric("💰 Precio Base", f"${selected_product.get('precio_base', 0):.2f}")
                    st.write(f"🏷️ **Categoría:** {selected_product.get('categoria', {}).get('nombre', 'Sin categoría') if isinstance(selected_product.get('categoria'), dict) else 'Sin categoría'}")
                with col_info2:
                    st.metric("🆔 ID Producto", product_id)
                    st.write(f"📝 **Descripción:** {selected_product.get('descripcion', 'Sin descripción')}")
            
            st.markdown("---")
            
            # Opciones de análisis organizadas en pestañas
            tab1, tab2, tab3 = st.tabs(["🤖 Machine Learning", "📊 Análisis", "📦 Inventario"])
            
            with tab1:
                st.markdown("**🔮 Predicciones y Modelos**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("� Predecir Demanda", key="predict_btn", use_container_width=True):
                        command = f"predecir producto {product_id}"
                        self._send_quick_command(command)
                        st.session_state.show_product_selector = False
                        st.rerun()
                
                with col2:
                    if st.button("🔍 Comparar Modelos", key="compare_btn", use_container_width=True):
                        command = f"comparar modelos para producto {product_id}"
                        self._send_quick_command(command)
                        st.session_state.show_product_selector = False
                        st.rerun()
                
                with col3:
                    if st.button("🏆 Mejor Modelo", key="best_model_btn", use_container_width=True):
                        command = f"cuál modelo es mejor para producto {product_id}"
                        self._send_quick_command(command)
                        st.session_state.show_product_selector = False
                        st.rerun()
            
            with tab2:
                st.markdown("**📊 Análisis de Negocio**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📈 Tendencias", key="trends_btn", use_container_width=True):
                        command = f"analizar tendencias producto {product_id}"
                        self._send_quick_command(command)
                        st.session_state.show_product_selector = False
                        st.rerun()
                
                with col2:
                    if st.button("💰 Análisis Ventas", key="sales_analysis_btn", use_container_width=True):
                        command = f"ventas producto {product_id}"
                        self._send_quick_command(command)
                        st.session_state.show_product_selector = False
                        st.rerun()
                
                with col3:
                    if st.button("📊 Estadísticas", key="stats_btn", use_container_width=True):
                        command = f"estadísticas producto {product_id}"
                        self._send_quick_command(command)
                        st.session_state.show_product_selector = False
                        st.rerun()
            
            with tab3:
                st.markdown("**📦 Gestión de Inventario**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("📦 Ver Inventario", key="inventory_btn", use_container_width=True):
                        command = f"inventario producto {product_id}"
                        self._send_quick_command(command)
                        st.session_state.show_product_selector = False
                        st.rerun()
                
                with col2:
                    if st.button("⚠️ Alertas Stock", key="alerts_btn", use_container_width=True):
                        command = f"alertas stock producto {product_id}"
                        self._send_quick_command(command)
                        st.session_state.show_product_selector = False
                        st.rerun()
                
                with col3:
                    if st.button("📋 Recomendaciones", key="recommendations_btn", use_container_width=True):
                        command = f"recomendar para producto {product_id}"
                        self._send_quick_command(command)
                        st.session_state.show_product_selector = False
                        st.rerun()
            
            st.markdown("---")
            
            # Botones de acción general
            col_gen1, col_gen2, col_gen3 = st.columns(3)
            
            with col_gen1:
                if st.button("� Comparar Todos los Modelos", key="compare_all_btn", use_container_width=True):
                    command = "comparar todos los modelos"
                    self._send_quick_command(command)
                    st.session_state.show_product_selector = False
                    st.rerun()
            
            with col_gen2:
                if st.button("📊 Análisis General", key="general_analysis_btn", use_container_width=True):
                    command = "análisis general de negocio"
                    self._send_quick_command(command)
                    st.session_state.show_product_selector = False
                    st.rerun()
            
            with col_gen3:
                if st.button("❌ Cerrar Selector", key="cancel_btn", use_container_width=True):
                    st.session_state.show_product_selector = False
                    st.rerun()
        
        else:
            st.info("👆 Selecciona un producto para ver las opciones disponibles")
    
    def detect_prediction_intent(self, message: str) -> bool:
        """Detectar si el usuario quiere hacer una predicción"""
        prediction_keywords = [
            'predic', 'demanda', 'pronóstico', 'forecast', 'estimar', 
            'proyectar', 'cuánto vender', 'futuro', 'próximos días',
            'ventas futuras', 'qué esperar', 'modelo', 'machine learning',
            'ml', 'algoritmo', 'comparar modelo', 'mejor modelo'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in prediction_keywords)
    
    def detect_model_comparison_intent(self, message: str) -> bool:
        """Detectar si el usuario quiere comparar modelos"""
        comparison_keywords = [
            'comparar modelo', 'mejor modelo', 'cuál modelo', 'qué modelo',
            'evaluar modelo', 'modelo más preciso', 'comparación', 'algoritmo',
            'machine learning', 'ml', 'linear', 'polynomial', 'precisión'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in comparison_keywords)
    
    def detect_needs_product_selection(self, message: str) -> bool:
        """Detectar si el mensaje necesita selección de producto"""
        # Si ya menciona un ID específico, no necesita selector
        import re
        if re.search(r'producto\s+\d+', message.lower()):
            return False
        
        needs_product_keywords = [
            'predic', 'inventario de producto', 'stock de producto',
            'ventas de producto', 'análisis producto', 'modelo para producto',
            'comparar modelo', 'mejor modelo', 'tendencia producto'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in needs_product_keywords)
    
    def suggest_product_selection(self, message: str) -> str:
        """Sugerir selección de producto cuando sea necesario"""
        if self.detect_needs_product_selection(message):
            return ("🎯 **Tu consulta necesita un producto específico**\n\n"
                   "Para darte una respuesta precisa, necesito saber sobre qué producto quieres información. "
                   "Puedes:\n\n"
                   "1️⃣ Usar el **Selector Interactivo** (aparece abajo)\n"
                   "2️⃣ Especificar el ID: `predecir producto 1`\n"
                   "3️⃣ Mencionar el nombre: `análisis de Laptop Gaming`\n\n"
                   "💡 **Ejemplo:** `comparar modelos para producto 2`")
        return ""

    def check_backend_connection(self) -> bool:
        """Verificar conexión con el backend"""
        try:
            response = requests.get(f"{self.backend_url}/api/chatbot/health", timeout=3)
            return response.status_code == 200
        except Exception:
            return False
    
    def send_message_to_backend(self, message: str) -> Dict[str, Any]:
        """Enviar mensaje al backend"""
        try:
            payload = {
                "content": message,
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.backend_url}/api/chatbot/message",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "response": f"Error del servidor: {response.status_code}",
                    "fallback": True
                }
                
        except requests.RequestException as e:
            return {
                "success": False,
                "response": self._get_fallback_response(message),
                "fallback": True,
                "error": str(e)
            }
    
    def _get_fallback_response(self, message: str) -> str:
        """Respuesta de fallback cuando el backend no está disponible"""
        message_lower = message.lower()
        
        # Respuestas básicas sin backend
        if any(word in message_lower for word in ['hola', 'hello', 'buenos', 'buenas']):
            return """🤖 **¡Hola!** 

Soy tu asistente de MicroAnalytics (modo offline).

⚠️ **Nota:** El backend no está disponible, pero puedo ayudarte con información básica.

📋 **Para usar todas las funciones:**
1. Asegúrate de que el backend esté ejecutándose
2. Ejecuta: `uvicorn backend.app:app --reload`
3. Recarga esta página

💡 **Comandos que funcionarán cuando el backend esté activo:**
• "inventario producto 1"
• "predecir producto 1" 
• "ventas del mes"
• "productos disponibles" """

        elif any(word in message_lower for word in ['ayuda', 'help', 'comando']):
            return """🤖 **Comandos Disponibles (cuando el backend esté activo):**

📊 **Predicciones:**
• `predecir producto 1` - Predice demanda futura
• `demanda producto X próximos 30 días`

📦 **Inventario:**
• `inventario producto 1` - Ver stock
• `productos disponibles` - Lista productos

💰 **Ventas:**
• `ventas del mes` - Reporte mensual
• `cómo va mi negocio` - Análisis general

🔧 **Estado actual:** Backend desconectado
Para usar el chatbot completo, inicia el backend con:
```
uvicorn backend.app:app --reload
```"""

        elif 'predic' in message_lower or 'demanda' in message_lower:
            return """📊 **Predicción de Demanda** (Demo)

⚠️ **Backend requerido** para predicciones reales.

🎯 **Lo que podrás hacer cuando el backend esté activo:**
• Predicciones basadas en datos reales de tu negocio
• Análisis de tendencias inteligentes
• Recomendaciones personalizadas de inventario
• Comparación de modelos de ML

🚀 **Para activar:** `uvicorn backend.app:app --reload`"""

        elif 'inventario' in message_lower or 'stock' in message_lower:
            return """📦 **Consulta de Inventario** (Demo)

⚠️ **Backend requerido** para datos reales de inventario.

📋 **Funciones disponibles con backend activo:**
• Stock en tiempo real por producto
• Alertas de stock bajo
• Valorización de inventario
• Recomendaciones de reabastecimiento

🚀 **Para activar:** `uvicorn backend.app:app --reload`"""

        else:
            return """🤖 **Chatbot en Modo Offline**

⚠️ **El backend no está disponible**

🔧 **Para usar todas las funciones:**
1. Abre una terminal en la carpeta del proyecto
2. Ejecuta: `uvicorn backend.app:app --reload`
3. Recarga esta página

✨ **Funciones que estarán disponibles:**
• Predicciones de demanda inteligentes
• Consultas de inventario en tiempo real
• Reportes de ventas automáticos
• Análisis de negocio personalizado

💡 **Tip:** El chatbot usa tu base de datos real para respuestas precisas."""
    
    def render_chat_interface(self):
        """Renderizar la interfaz principal del chat"""
        # Título con clase especial para mantener color blanco
        st.markdown('<h1 class="chat-title">🤖 Asistente Inteligente de MicroAnalytics</h1>', unsafe_allow_html=True)
        
        # Verificar estado del backend
        backend_status = self.check_backend_connection()
        
        if backend_status:
            st.success("✅ Chatbot conectado al backend - Todas las funciones disponibles")
        else:
            st.warning("⚠️ Backend desconectado - Funciones limitadas. Ejecuta: `uvicorn backend.app:app --reload`")
        
        # Mostrar selector de productos si está activado
        if st.session_state.show_product_selector and backend_status:
            self.render_product_selector()
            st.markdown("---")
        
        # Contenedor para mensajes
        chat_container = st.container()
        
        with chat_container:
            # Mostrar historial de mensajes
            for message in st.session_state.chat_messages:
                self._render_message(message)
        
        # Input para nuevos mensajes
        user_input = st.chat_input("Escribe tu consulta o usa 'predicción' para abrir el selector...")
        
        if user_input:
            # Detectar si quiere hacer una predicción y no especifica producto
            if self.detect_prediction_intent(user_input) and not any(char.isdigit() for char in user_input):
                st.session_state.show_product_selector = True
                
                # Agregar mensaje del usuario
                user_message = {
                    "role": "user", 
                    "content": user_input,
                    "timestamp": datetime.now()
                }
                st.session_state.chat_messages.append(user_message)
                
                # Respuesta del asistente
                assistant_message = {
                    "role": "assistant",
                    "content": """🎯 **¡Perfecto! Te ayudo con la predicción.**

He activado el **Selector Inteligente de Productos** arriba para que puedas:

📊 **Seleccionar fácilmente** el producto que te interesa
🔍 **Ver información detallada** (nombre, precio, ID)
📈 **Generar predicción** con un solo click
📦 **Consultar inventario** del producto seleccionado
🤖 **Comparar modelos ML** para mayor precisión

💡 **Tip:** También puedes escribir directamente "predecir producto X" donde X es el número de ID.""",
                    "timestamp": datetime.now(),
                    "backend_used": backend_status
                }
                st.session_state.chat_messages.append(assistant_message)
                st.rerun()
            else:
                # Procesar mensaje normal
                self._process_normal_message(user_input, backend_status)
    
    def _process_normal_message(self, user_input: str, backend_status: bool):
        """Procesar mensaje normal del usuario con detección inteligente"""
        # Agregar mensaje del usuario
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now()
        }
        st.session_state.chat_messages.append(user_message)
        
        # Verificar si necesita selección de producto
        suggestion = self.suggest_product_selection(user_input)
        if suggestion:
            # Mostrar sugerencia y activar selector
            st.session_state.show_product_selector = True
            assistant_message = {
                "role": "assistant",
                "content": suggestion,
                "timestamp": datetime.now(),
                "backend_used": backend_status
            }
            st.session_state.chat_messages.append(assistant_message)
            st.rerun()
            return
        
        # Verificar si quiere comparación de modelos general
        if self.detect_model_comparison_intent(user_input) and 'todos' in user_input.lower():
            enhanced_command = "comparar todos los modelos"
            user_input = enhanced_command
        
        # Procesar mensaje y obtener respuesta
        with st.spinner("🤖 Analizando tu consulta..."):
            if backend_status:
                response_data = self.send_message_to_backend(user_input)
                response_content = response_data.get('response', 'Error procesando mensaje')
                
                # Si el backend no entendió algo específico, dar sugerencias
                if 'no entiendo' in response_content.lower() or 'error' in response_content.lower():
                    # Intentar mejorar el comando
                    if self.detect_prediction_intent(user_input):
                        response_content += "\n\n💡 **Sugerencia:** Usa el selector de productos (escribe `predicción`) o especifica: `predecir producto [ID]`"
                    elif self.detect_model_comparison_intent(user_input):
                        response_content += "\n\n💡 **Sugerencia:** Prueba: `comparar todos los modelos` o `mejor modelo para producto [ID]`"
                    
            else:
                response_content = self._get_fallback_response(user_input)
        
        # Agregar respuesta del asistente
        assistant_message = {
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now(),
            "backend_used": backend_status
        }
        st.session_state.chat_messages.append(assistant_message)
        
        st.rerun()
    
    def _render_message(self, message: Dict[str, Any]):
        """Renderizar un mensaje individual"""
        timestamp = message['timestamp'].strftime("%H:%M")
        
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.markdown(f"**Tú ({timestamp}):** {message['content']}")
        else:
            with st.chat_message("assistant"):
                backend_indicator = "🟢" if message.get('backend_used', False) else "🔴"
                st.markdown(f"**Asistente ({timestamp}) {backend_indicator}:**")
                st.markdown(message['content'])
    
    def render_sidebar(self):
        """Renderizar barra lateral con información y controles del chat"""
        st.sidebar.markdown("---")
        st.sidebar.subheader("🤖 Chat Inteligente")
        
        # Estado del sistema
        backend_status = self.check_backend_connection()
        
        st.sidebar.subheader("🔗 Estado del Sistema")
        if backend_status:
            st.sidebar.success("✅ Backend conectado")
            st.sidebar.info("🎯 Todas las funciones disponibles")
        else:
            st.sidebar.error("❌ Backend desconectado")
            st.sidebar.warning("⚠️ Funciones limitadas")
        
        st.sidebar.markdown("---")
        
        # Comandos rápidos
        st.sidebar.subheader("⚡ Comandos Rápidos")
        
        if st.sidebar.button("📦 Productos disponibles"):
            self._send_quick_command("productos disponibles")
        
        if st.sidebar.button("🎯 Selector de Productos"):
            st.session_state.show_product_selector = True
            st.rerun()
        
        if st.sidebar.button("📊 Inventario general"):
            self._send_quick_command("inventario general")
        
        if st.sidebar.button("💰 Ventas del mes"):
            self._send_quick_command("ventas del mes")
        
        if st.sidebar.button("🤖 Comparar Modelos ML"):
            self._send_quick_command("comparar todos los modelos")
        
        if st.sidebar.button("📈 Análisis de negocio"):
            self._send_quick_command("cómo va mi negocio")
        
        if st.sidebar.button("❓ Ayuda"):
            self._send_quick_command("ayuda")
        
        st.sidebar.markdown("---")
        
        # Ejemplos de comandos
        st.sidebar.subheader("💡 Ejemplos de Comandos")
        st.sidebar.markdown("""
        **🎯 Predicciones Inteligentes:**
        • `predicción` - Abre selector interactivo
        • `predecir producto 1`
        • `demanda producto 2 próximos 15 días`
        • `comparar modelos para producto 1`
        
        **📦 Inventario:**
        • `inventario producto 1`
        • `inventario general`
        • `productos con stock bajo`
        
        **💰 Ventas y Análisis:**
        • `ventas del mes`
        • `análisis de tendencias`
        • `cómo va mi negocio`
        
        **🤖 Modelos ML:**
        • `comparar todos los modelos`
        • `qué modelo es mejor`
        • `precisión de modelos`
        
        **📋 General:**
        • `productos disponibles`
        • `proveedores`
        • `categorías disponibles`
        """)
        
        st.sidebar.markdown("---")
        
        # Configuración avanzada
        st.sidebar.subheader("⚙️ Configuración")
        
        # Días para predicción
        prediction_days = st.sidebar.slider(
            "📅 Días a predecir",
            min_value=7,
            max_value=90,
            value=30,
            step=7,
            help="Número de días hacia el futuro para las predicciones"
        )
        
        # Guardar en session state
        st.session_state.prediction_days = prediction_days
        
        # Incluir intervalos de confianza
        include_confidence = st.sidebar.checkbox(
            "📊 Incluir intervalos de confianza",
            value=True,
            help="Mostrar rangos de confianza en las predicciones"
        )
        st.session_state.include_confidence = include_confidence
        
        st.sidebar.markdown("---")
        
        # Información de la sesión
        st.sidebar.subheader("ℹ️ Información del Chat")
        st.sidebar.text(f"Sesión: {self.session_id[:8]}...")
        st.sidebar.text(f"Mensajes: {len(st.session_state.chat_messages)}")
        
        # Limpiar chat
        if st.sidebar.button("🗑️ Limpiar Chat"):
            st.session_state.chat_messages = []
            st.rerun()
    
    def _send_quick_command(self, command: str):
        """Enviar comando rápido"""
        # Agregar comando como mensaje del usuario
        user_message = {
            "role": "user",
            "content": command,
            "timestamp": datetime.now()
        }
        st.session_state.chat_messages.append(user_message)
        
        # Procesar comando
        backend_status = self.check_backend_connection()
        
        if backend_status:
            response_data = self.send_message_to_backend(command)
            response_content = response_data.get('response', 'Error procesando comando')
        else:
            response_content = self._get_fallback_response(command)
        
        # Agregar respuesta
        assistant_message = {
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now(),
            "backend_used": backend_status
        }
        st.session_state.chat_messages.append(assistant_message)
        
        st.rerun()
    
    def run(self):
        """Ejecutar la aplicación integrada"""
        # Renderizar la barra lateral del chat
        self.render_sidebar()
        
        # Renderizar la interfaz del chat
        self.render_chat_interface()
        
        # Mensaje inicial si no hay mensajes
        if not st.session_state.chat_messages:
            welcome_message = {
                "role": "assistant",
                "content": """¡Bienvenido al Asistente Inteligente de MicroAnalytics! 🤖

Soy tu asistente especializado en análisis de negocio con IA. Puedo ayudarte con:

🎯 **NUEVO: Selector Inteligente de Productos**
• Escribe `predicción` para abrir el selector interactivo
• Selecciona productos fácilmente y genera predicciones con un click

📊 **Predicciones de Demanda Avanzadas**
• "predecir producto 1" - Predicción específica
• "comparar modelos para producto X" - Encuentra el mejor modelo ML
• "demanda próximos 30 días" - Análisis temporal

📦 **Gestión de Inventario Inteligente**
• "inventario producto 1" - Stock específico
• "inventario general" - Vista completa
• "productos con stock bajo" - Alertas automáticas

� **Análisis de Ventas y Negocio**
• "ventas del mes" - Reporte automático
• "cómo va mi negocio" - Análisis integral
• "análisis de tendencias" - Insights avanzados

🤖 **Machine Learning Integrado**
• "comparar todos los modelos" - Evaluación de precisión
• "qué modelo es mejor" - Recomendaciones automáticas

**🚀 Para comenzar rápidamente:**
1. 🎯 Escribe `predicción` para usar el selector
2. 📦 Escribe `productos disponibles` para ver tu catálogo
3. 💡 Escribe `ayuda` para ver todos los comandos

**💡 Tip Avanzado:** Ahora entiendo mejor el lenguaje natural. Puedes preguntarme cosas como "¿qué producto debería reabastecer?" o "¿cuál será mi mejor vendedor?"

¡Usa los botones de la barra lateral para acceso rápido!""",
                "timestamp": datetime.now(),
                "backend_used": self.check_backend_connection()
            }
            st.session_state.chat_messages.append(welcome_message)
            st.rerun()


def main():
    """Función principal para usar el chatbot de forma independiente"""
    try:
        # Configurar página si se ejecuta de forma independiente
        st.set_page_config(
            page_title="MicroAnalytics Chatbot",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        chatbot = ChatbotFrontend()
        chatbot.run()
    except Exception as e:
        st.error(f"Error en el chatbot: {str(e)}")
        st.info("Intenta recargar la página.")


if __name__ == "__main__":
    main()
