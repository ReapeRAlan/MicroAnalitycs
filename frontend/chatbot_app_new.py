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
    
    def _get_session_id(self) -> str:
        """Obtener o crear ID de sesión"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return st.session_state.session_id
    
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
        
        # Contenedor para mensajes
        chat_container = st.container()
        
        with chat_container:
            # Mostrar historial de mensajes
            for message in st.session_state.chat_messages:
                self._render_message(message)
        
        # Input para nuevos mensajes
        user_input = st.chat_input("Escribe tu consulta (ej: 'inventario producto 1', 'predecir producto 1', 'ayuda')...")
        
        if user_input:
            # Agregar mensaje del usuario
            user_message = {
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now()
            }
            st.session_state.chat_messages.append(user_message)
            
            # Procesar mensaje y obtener respuesta
            with st.spinner("Procesando mensaje..."):
                if backend_status:
                    response_data = self.send_message_to_backend(user_input)
                    response_content = response_data.get('response', 'Error procesando mensaje')
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
        
        if st.sidebar.button("📊 Inventario general"):
            self._send_quick_command("inventario general")
        
        if st.sidebar.button("💰 Ventas del mes"):
            self._send_quick_command("ventas del mes")
        
        if st.sidebar.button("📈 Análisis de negocio"):
            self._send_quick_command("cómo va mi negocio")
        
        if st.sidebar.button("❓ Ayuda"):
            self._send_quick_command("ayuda")
        
        st.sidebar.markdown("---")
        
        # Ejemplos de comandos
        st.sidebar.subheader("💡 Ejemplos de Comandos")
        st.sidebar.markdown("""
        **Predicciones:**
        • `predecir producto 1`
        • `demanda producto 2 próximos 15 días`
        
        **Inventario:**
        • `inventario producto 1`
        • `stock bajo`
        
        **Ventas:**
        • `ventas del mes`
        • `reporte de ventas`
        
        **General:**
        • `productos disponibles`
        • `proveedores`
        • `categorías`
        """)
        
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

Soy tu asistente especializado en análisis de negocio. Puedo ayudarte con:

📊 **Predicciones de demanda** - "predecir producto 1"
📦 **Consultas de inventario** - "inventario producto 1"  
💰 **Reportes de ventas** - "ventas del mes"
📈 **Análisis de negocio** - "cómo va mi negocio"

💡 **Tip:** Puedo entender comandos en lenguaje natural. ¡Pregúntame lo que necesites!

**🚀 Ejemplos para comenzar:**
• "¿Qué productos tengo disponibles?"
• "¿Cómo está mi inventario?"
• "Predice las ventas del producto 1"
• "Muestra el reporte de ventas"

Para ver todos los comandos disponibles, escribe `ayuda` o usa los botones de la barra lateral.""",
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
