"""
Sistema de integración con Ollama para el chatbot
Conecta con Ollama ejecutándose en Google Colab a través de ngrok
"""
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime
import logging
from pydantic import BaseModel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaConfig(BaseModel):
    """Configuración para Ollama"""
    base_url: str = "https://645c-34-169-9-109.ngrok-free.app"
    model_name: str = "llama3.2"  # o el modelo que tengas en Ollama
    timeout: int = 120
    max_tokens: int = 1000
    temperature: float = 0.7
    system_prompt: str = """Eres un asistente de análisis de datos especializado en micronegocios y predicción de demanda. 
    Tienes acceso a un sistema de machine learning que puede:
    - Predecir demanda de productos
    - Comparar modelos de ML
    - Analizar inventarios
    - Generar reportes
    
    Responde de manera clara, concisa y orientada a acción. Cuando sea apropiado, sugiere usar los modelos de ML disponibles."""

class OllamaClient:
    """Cliente para interactuar con Ollama"""
    
    def __init__(self, config: OllamaConfig = None):
        self.config = config or OllamaConfig()
        self.conversation_context = {}
    
    async def check_connection(self) -> bool:
        """Verifica si Ollama está disponible"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error conectando con Ollama: {e}")
            return False
    
    async def list_models(self) -> List[str]:
        """Lista los modelos disponibles en Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["name"] for model in data.get("models", [])]
                    return []
        except Exception as e:
            logger.error(f"Error obteniendo modelos: {e}")
            return []
    
    async def generate_response(
        self, 
        prompt: str, 
        session_id: str = None,
        include_ml_context: bool = True,
        stream: bool = False
    ) -> str:
        """Genera una respuesta usando Ollama"""
        try:
            # Construir el prompt con contexto
            full_prompt = self._build_prompt(prompt, session_id, include_ml_context)
            
            payload = {
                "model": self.config.model_name,
                "prompt": full_prompt,
                "system": self.config.system_prompt,
                "stream": stream,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.base_url}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Guardar contexto de conversación
                        if session_id:
                            self._update_conversation_context(session_id, prompt, response_data.get('response', ''))
                        
                        return response_data.get('response', 'No hay respuesta disponible.')
                    else:
                        logger.error(f"Error en Ollama: {response.status} - {await response.text()}")
                        return "Lo siento, hay un problema con el servicio de chat. Intenta de nuevo."
                
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return "Disculpa, no pude procesar tu mensaje en este momento."
    
    async def stream_response(
        self, 
        prompt: str, 
        session_id: str = None
    ) -> AsyncGenerator[str, None]:
        """Genera respuesta en streaming"""
        try:
            full_prompt = self._build_prompt(prompt, session_id, True)
            
            payload = {
                "model": self.config.model_name,
                "prompt": full_prompt,
                "system": self.config.system_prompt,
                "stream": True,
                "options": {
                    "temperature": self.config.temperature,
                    "num_predict": self.config.max_tokens
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.base_url}/api/generate",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    if response.status == 200:
                        async for line in response.content:
                            if line:
                                try:
                                    data = json.loads(line.decode('utf-8'))
                                    if 'response' in data:
                                        yield data['response']
                                    if data.get('done', False):
                                        break
                                except json.JSONDecodeError:
                                    continue
                    else:
                        yield "Error en el servicio de chat."
                        
        except Exception as e:
            logger.error(f"Error en stream: {e}")
            yield "Error en la conexión."
    
    def _build_prompt(self, user_prompt: str, session_id: str = None, include_ml_context: bool = True) -> str:
        """Construye el prompt completo con contexto"""
        prompt_parts = []
        
        # Contexto de ML si está habilitado
        if include_ml_context:
            ml_context = """
            Contexto: Tienes acceso a un sistema de ML con las siguientes capacidades:
            
            1. PREDICCIÓN DE DEMANDA:
               - Predice ventas futuras de productos específicos
               - Usa múltiples modelos (lineal, polinómico)
               - Comando: predict_demand(producto_id, dias)
            
            2. COMPARACIÓN DE MODELOS:
               - Evalúa rendimiento de diferentes modelos
               - Proporciona métricas de precisión
               - Comando: compare_models(producto_id)
            
            3. ANÁLISIS DE INVENTARIO:
               - Estado actual de stock
               - Recomendaciones de reposición
               - Comando: inventory_status(producto_id)
            
            4. ANÁLISIS DE TENDENCIAS:
               - Patrones de venta históricos
               - Estacionalidad y tendencias
               - Comando: analyze_trends(producto_id, periodo)
            
            Cuando el usuario pregunte algo que requiera estos análisis, menciona que puedes ejecutar el análisis correspondiente.
            """
            prompt_parts.append(ml_context)
        
        # Contexto de conversación previa
        if session_id and session_id in self.conversation_context:
            context = self.conversation_context[session_id]
            if context["messages"]:
                recent_messages = context["messages"][-3:]  # Últimos 3 intercambios
                conversation_history = "\n".join([
                    f"Usuario: {msg['user']}\nAsistente: {msg['assistant']}"
                    for msg in recent_messages
                ])
                prompt_parts.append(f"Conversación previa:\n{conversation_history}")
        
        # Prompt del usuario
        prompt_parts.append(f"Usuario: {user_prompt}")
        prompt_parts.append("Asistente:")
        
        return "\n\n".join(prompt_parts)
    
    def _update_conversation_context(self, session_id: str, user_message: str, assistant_response: str):
        """Actualiza el contexto de la conversación"""
        if session_id not in self.conversation_context:
            self.conversation_context[session_id] = {
                "created_at": datetime.now(),
                "messages": []
            }
        
        self.conversation_context[session_id]["messages"].append({
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.now()
        })
        
        # Mantener solo los últimos 10 intercambios
        if len(self.conversation_context[session_id]["messages"]) > 10:
            self.conversation_context[session_id]["messages"] = \
                self.conversation_context[session_id]["messages"][-10:]
    
    def update_ollama_url(self, new_url: str):
        """Actualiza la URL de Ollama (para cuando cambie el túnel ngrok)"""
        self.config.base_url = new_url
        logger.info(f"URL de Ollama actualizada a: {new_url}")

class OllamaManager:
    """Manager para múltiples instancias y configuraciones de Ollama"""
    
    def __init__(self):
        self.clients = {}
        self.default_config = OllamaConfig()
    
    def get_client(self, config_name: str = "default") -> OllamaClient:
        """Obtiene un cliente de Ollama"""
        if config_name not in self.clients:
            self.clients[config_name] = OllamaClient(self.default_config)
        return self.clients[config_name]
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica el estado de todos los clientes"""
        results = {}
        for name, client in self.clients.items():
            try:
                is_healthy = await client.check_connection()
                models = await client.list_models() if is_healthy else []
                results[name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "url": client.config.base_url,
                    "models": models,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        return results
    
    def update_url(self, new_url: str, config_name: str = "default"):
        """Actualiza la URL para un cliente específico"""
        if config_name in self.clients:
            self.clients[config_name].update_ollama_url(new_url)
        else:
            # Crear nuevo cliente con la nueva URL
            new_config = OllamaConfig(base_url=new_url)
            self.clients[config_name] = OllamaClient(new_config)

# Instancia global del manager
ollama_manager = OllamaManager()

# Funciones de utilidad
async def get_ollama_response(prompt: str, session_id: str = None) -> str:
    """Función de conveniencia para obtener respuesta de Ollama"""
    client = ollama_manager.get_client()
    async with client:
        return await client.generate_response(prompt, session_id)

async def stream_ollama_response(prompt: str, session_id: str = None):
    """Función de conveniencia para streaming"""
    client = ollama_manager.get_client()
    async with client:
        async for chunk in client.stream_response(prompt, session_id):
            yield chunk

async def check_ollama_status() -> Dict[str, Any]:
    """Verifica el estado de Ollama"""
    return await ollama_manager.health_check()
