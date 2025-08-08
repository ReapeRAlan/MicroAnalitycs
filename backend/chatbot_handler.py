"""
Manejador de chatbot inteligente sin Ollama
Usa la base de datos para obtener información real y responde automáticamente
"""
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np

from backend.base import SessionLocal
from backend.models.product import Product
from backend.models.category import Category
from backend.models.inventory import Inventory
from backend.models.transaction import Transaction
from backend.models.supplier import Supplier


class ChatbotHandler:
    """Manejador principal del chatbot"""
    
    def __init__(self):
        self.session = SessionLocal()
        self.command_patterns = self._init_command_patterns()
        
    def _init_command_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Inicializar patrones de comandos"""
        return {
            'prediction': {
                'patterns': [
                    r'predic(?:ir|ción|e)?.*producto\s*(\d+)',
                    r'demanda.*producto\s*(\d+)',
                    r'cuánto.*venderé.*producto\s*(\d+)',
                    r'pronóstico.*producto\s*(\d+)',
                    r'producto\s*(\d+).*próximos?\s*(\d+)?\s*días?',
                    r'ventas futuras.*producto\s*(\d+)',
                    r'predicción.*producto\s*(\d+)',
                    r'predic(?:ir|ción|e)?\s*(\d+)',
                    r'estimar.*producto\s*(\d+)',
                    r'proyectar.*producto\s*(\d+)',
                    # Patrones más simples
                    r'predecir\s+producto\s+(\d+)',
                    r'predicción\s+producto\s+(\d+)',
                    r'producto\s+(\d+)\s+predicción',
                    r'producto\s+(\d+)\s+predecir',
                ],
                'handler': self._handle_prediction
            },
            'inventory': {
                'patterns': [
                    r'inventario(?:\s+del?\s+)?producto\s*(\d+)',
                    r'stock(?:\s+del?\s+)?producto\s*(\d+)',
                    r'cuánto(?:\s+tengo)?\s+(?:del?\s+)?producto\s*(\d+)',
                    r'existencias?(?:\s+del?\s+)?producto\s*(\d+)',
                    r'inventario\s+general',
                    r'stock\s+general',
                    r'inventario\s+completo',
                ],
                'handler': self._handle_inventory
            },
            'products': {
                'patterns': [
                    r'productos?\s+disponibles?',
                    r'lista(?:\s+de)?\s+productos?',
                    r'qué productos? tengo',
                    r'mostrar productos?',
                    r'catálogo',
                ],
                'handler': self._handle_products_list
            },
            'categories': {
                'patterns': [
                    r'categorías?\s+disponibles?',
                    r'lista(?:\s+de)?\s+categorías?',
                    r'qué categorías? tengo',
                    r'productos?\s+por\s+categoría',
                ],
                'handler': self._handle_categories
            },
            'sales': {
                'patterns': [
                    r'ventas?\s+del?\s+mes',
                    r'ventas?\s+recientes?',
                    r'últimas?\s+ventas?',
                    r'reporte\s+de\s+ventas?',
                    r'historial\s+de\s+ventas?',
                ],
                'handler': self._handle_sales_report
            },
            'suppliers': {
                'patterns': [
                    r'proveedores?',
                    r'suppliers?',
                    r'quiénes?\s+son\s+mis\s+proveedores?',
                    r'lista\s+de\s+proveedores?',
                ],
                'handler': self._handle_suppliers
            },
            'comparison': {
                'patterns': [
                    r'comparar\s+modelos?',
                    r'mejor\s+modelo',
                    r'qué\s+modelo\s+es\s+mejor',
                    r'cuál\s+modelo\s+es\s+más\s+preciso',
                    r'evaluar\s+modelos?',
                    r'rendimiento\s+de\s+modelos?',
                    r'precisión\s+de\s+modelos?',
                    r'comparar\s+todos\s+los\s+modelos?',
                    r'comparar\s+modelos?\s+para\s+producto\s*(\d+)',
                    r'análisis\s+de\s+modelos?',
                    # Patrones más simples
                    r'comparar\s+modelos\s+para\s+producto\s+(\d+)',
                    r'cuál\s+modelo\s+es\s+mejor\s+para\s+producto\s+(\d+)',
                    r'mejor\s+modelo\s+para\s+producto\s+(\d+)',
                    r'comparar\s+todos\s+los\s+modelos',
                    r'todos\s+los\s+modelos',
                ],
                'handler': self._handle_model_comparison
            },
            'analysis': {
                'patterns': [
                    r'analizar?\s+tendencias?',
                    r'análisis\s+de\s+(?:ventas?|datos?)',
                    r'insights?',
                    r'qué\s+me\s+recomiendas?',
                    r'cómo\s+va\s+(?:mi\s+)?negocio',
                ],
                'handler': self._handle_business_analysis
            },
            'analysis': {
                'patterns': [
                    r'analizar?\s+tendencias?',
                    r'análisis\s+de\s+(?:ventas?|datos?)',
                    r'insights?',
                    r'qué\s+me\s+recomiendas?',
                    r'cómo\s+va\s+(?:mi\s+)?negocio',
                ],
                'handler': self._handle_business_analysis
            },
            'help': {
                'patterns': [
                    r'ayuda',
                    r'help',
                    r'qué\s+puedes?\s+hacer',
                    r'comandos?\s+disponibles?',
                    r'cómo\s+funciona',
                ],
                'handler': self._handle_help
            }
        }
    
    async def process_message(self, message_data: Dict) -> Dict[str, Any]:
        """Procesar mensaje del usuario"""
        try:
            user_message = message_data.get('content', '').strip()
            
            if not user_message:
                return self._error_response("Mensaje vacío")
            
            # Detectar comando
            command, extracted_data = self._detect_command(user_message)
            
            if command:
                # Ejecutar comando específico
                response = await self.command_patterns[command]['handler'](user_message, extracted_data)
            else:
                # Respuesta general inteligente
                response = self._handle_general_conversation(user_message)
            
            return {
                "success": True,
                "response": response,
                "command_detected": command,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return self._error_response(f"Error procesando mensaje: {str(e)}")
        finally:
            self.session.close()
    
    def _detect_command(self, message: str) -> tuple[Optional[str], Dict[str, Any]]:
        """Detectar comando en el mensaje"""
        message_lower = message.lower()
        
        for command_name, command_data in self.command_patterns.items():
            for pattern in command_data['patterns']:
                try:
                    match = re.search(pattern, message_lower)
                    if match:
                        extracted_data = {
                            'groups': match.groups(),
                            'full_match': match.group(0)
                        }
                        return command_name, extracted_data
                except re.error:
                    continue
        
        return None, {}
    
    async def _handle_prediction(self, message: str, data: Dict) -> str:
        """Manejar predicciones de demanda"""
        try:
            # Extraer ID de producto
            groups = data.get('groups', ())
            product_id = int(groups[0]) if groups and groups[0] else 1
            
            # Extraer días (si se especifica)
            days = 30  # por defecto
            if len(groups) > 1 and groups[1]:
                days = int(groups[1])
            
            # Verificar que el producto existe
            product = self.session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return self._format_error_response(f"❌ Producto {product_id} no encontrado")
            
            # Obtener datos históricos de ventas
            sales_data = self._get_historical_sales(product_id)
            
            if not sales_data:
                return self._format_warning_response(
                    f"⚠️ No hay datos históricos suficientes para el producto {product_id}",
                    self._generate_demo_prediction(product, days)
                )
            
            # Generar predicción basada en datos reales
            prediction = self._calculate_smart_prediction(sales_data, days)
            
            return self._format_prediction_response(product, prediction, days)
            
        except Exception as e:
            return self._format_error_response(f"Error en predicción: {str(e)}")
    
    async def _handle_inventory(self, message: str, data: Dict) -> str:
        """Manejar consultas de inventario"""
        try:
            groups = data.get('groups', ())
            
            # Si no hay grupos o el grupo está vacío, es inventario general
            if not groups or not groups[0]:
                return await self._handle_general_inventory()
            
            product_id = int(groups[0])
            
            if product_id:
                # Inventario de producto específico
                product = self.session.query(Product).filter(Product.id == product_id).first()
                if not product:
                    return self._format_error_response(f"❌ Producto {product_id} no encontrado")
                
                inventory = self.session.query(Inventory).filter(Inventory.product_id == product_id).first()
                
                return self._format_inventory_response(product, inventory)
            else:
                # Inventario general
                return await self._handle_general_inventory()
                
        except Exception as e:
            return self._format_error_response(f"Error consultando inventario: {str(e)}")
    
    async def _handle_products_list(self, message: str, data: Dict) -> str:
        """Manejar lista de productos"""
        try:
            products = self.session.query(Product).limit(10).all()
            
            if not products:
                return self._format_warning_response("⚠️ No hay productos registrados")
            
            response = "📦 **Lista de Productos Disponibles:**\n\n"
            
            for product in products:
                category_name = product.categoria.nombre if product.categoria else "Sin categoría"
                response += f"• **{product.nombre}** (ID: {product.id})\n"
                response += f"  - Categoría: {category_name}\n"
                response += f"  - Precio: ${product.precio_base:.2f}\n\n"
            
            response += "💡 **Tip:** Usa 'inventario producto X' para ver stock específico"
            
            return response
            
        except Exception as e:
            return self._format_error_response(f"Error obteniendo productos: {str(e)}")
    
    async def _handle_categories(self, message: str, data: Dict) -> str:
        """Manejar consultas de categorías"""
        try:
            categories = self.session.query(Category).all()
            
            if not categories:
                return self._format_warning_response("⚠️ No hay categorías registradas")
            
            response = "📂 **Categorías Disponibles:**\n\n"
            
            for category in categories:
                product_count = self.session.query(Product).filter(Product.category_id == category.id).count()
                response += f"• **{category.nombre}** ({product_count} productos)\n"
                response += f"  - {category.descripcion}\n\n"
            
            return response
            
        except Exception as e:
            return self._format_error_response(f"Error obteniendo categorías: {str(e)}")
    
    async def _handle_sales_report(self, message: str, data: Dict) -> str:
        """Manejar reportes de ventas"""
        try:
            # Obtener ventas del último mes
            last_month = datetime.now() - timedelta(days=30)
            
            sales = self.session.query(Transaction).filter(
                Transaction.fecha >= last_month
            ).all()
            
            if not sales:
                return self._format_warning_response("⚠️ No hay ventas registradas en el último mes")
            
            # Calcular estadísticas
            total_sales = len(sales)
            total_revenue = sum(sale.total for sale in sales)
            avg_sale = total_revenue / total_sales if total_sales > 0 else 0
            
            response = f"""📊 **Reporte de Ventas (Últimos 30 días):**

💰 **Resumen Financiero:**
• Total de ventas: {total_sales} transacciones
• Ingresos totales: ${total_revenue:.2f}
• Venta promedio: ${avg_sale:.2f}

📈 **Tendencia:**
• Ventas por día: {total_sales/30:.1f} promedio
• {"📈 Tendencia positiva" if total_sales > 20 else "📊 Actividad normal" if total_sales > 10 else "📉 Actividad baja"}

💡 **Sugerencias:**
• {'Mantén el buen ritmo' if total_sales > 20 else 'Considera promociones para aumentar ventas'}
"""
            
            return response
            
        except Exception as e:
            return self._format_error_response(f"Error obteniendo reporte de ventas: {str(e)}")
    
    async def _handle_suppliers(self, message: str, data: Dict) -> str:
        """Manejar información de proveedores"""
        try:
            suppliers = self.session.query(Supplier).all()
            
            if not suppliers:
                return self._format_warning_response("⚠️ No hay proveedores registrados")
            
            response = "🏪 **Lista de Proveedores:**\n\n"
            
            for supplier in suppliers:
                response += f"• **{supplier.nombre}**\n"
                response += f"  - Contacto: {supplier.contacto}\n\n"
            
            return response
            
        except Exception as e:
            return self._format_error_response(f"Error obteniendo proveedores: {str(e)}")
    
    async def _handle_business_analysis(self, message: str, data: Dict) -> str:
        """Manejar análisis de negocio"""
        try:
            # Obtener métricas generales del negocio
            total_products = self.session.query(Product).count()
            total_categories = self.session.query(Category).count()
            total_suppliers = self.session.query(Supplier).count()
            
            # Ventas del último mes
            last_month = datetime.now() - timedelta(days=30)
            recent_sales = self.session.query(Transaction).filter(
                Transaction.fecha >= last_month
            ).count()
            
            # Productos con bajo stock
            low_stock = self.session.query(Inventory).filter(Inventory.stock_actual < 10).count()
            
            response = f"""📊 **Análisis del Negocio:**

📈 **Estado General:**
• Productos en catálogo: {total_products}
• Categorías activas: {total_categories}
• Proveedores: {total_suppliers}

💼 **Actividad Reciente (30 días):**
• Ventas realizadas: {recent_sales}
• Actividad: {"🟢 Alta" if recent_sales > 20 else "🟡 Media" if recent_sales > 10 else "🔴 Baja"}

⚠️ **Alertas:**
• Productos con bajo stock: {low_stock}
• {"🚨 Revisar inventario urgente" if low_stock > 5 else "✅ Niveles de stock normales"}

💡 **Recomendaciones:**
"""
            
            if recent_sales < 10:
                response += "• Considera estrategias de marketing para aumentar ventas\n"
            if low_stock > 3:
                response += "• Programa reabastecimiento de productos con bajo stock\n"
            if total_products < 20:
                response += "• Evalúa ampliar el catálogo de productos\n"
            
            response += "• Usa 'predecir producto X' para planificar inventario"
            
            return response
            
        except Exception as e:
            return self._format_error_response(f"Error en análisis: {str(e)}")
    
    async def _handle_help(self, message: str, data: Dict) -> str:
        """Manejar solicitudes de ayuda"""
        return """🤖 **Asistente de MicroAnalytics - Comandos Disponibles:**

📊 **Predicciones y Análisis:**
• `predecir producto 1` - Predice demanda futura
• `demanda producto 1 próximos 30 días` - Predicción específica
• `analizar tendencias` - Análisis general del negocio

📦 **Inventario y Productos:**
• `inventario producto 1` - Stock de producto específico
• `productos disponibles` - Lista todos los productos
• `categorías disponibles` - Muestra categorías

💰 **Ventas y Reportes:**
• `ventas del mes` - Reporte de ventas recientes
• `reporte de ventas` - Estadísticas detalladas

🏪 **Proveedores:**
• `proveedores` - Lista de proveedores registrados

❓ **Ayuda:**
• `ayuda` - Muestra esta lista de comandos

💡 **Ejemplos prácticos:**
• "¿Cuánto venderé del producto 1 en los próximos 15 días?"
• "¿Cuánto stock tengo del producto 2?"
• "¿Cómo va mi negocio?"
• "Muestra mis productos"

✨ **Tip:** Puedo entender preguntas en lenguaje natural. ¡Pregúntame lo que necesites!"""
    
    async def _handle_general_inventory(self) -> str:
        """Manejar inventario general"""
        try:
            inventories = self.session.query(Inventory).join(Product).limit(10).all()
            
            if not inventories:
                return self._format_warning_response("⚠️ No hay datos de inventario")
            
            response = "📦 **Estado General del Inventario:**\n\n"
            
            low_stock_items = []
            good_stock_items = []
            
            for inv in inventories:
                product = inv.producto
                if inv.stock_actual < 10:
                    low_stock_items.append(f"🔴 **{product.nombre}**: {inv.stock_actual} unidades")
                else:
                    good_stock_items.append(f"🟢 **{product.nombre}**: {inv.stock_actual} unidades")
            
            if low_stock_items:
                response += "⚠️ **Productos con Stock Bajo:**\n"
                response += "\n".join(low_stock_items[:5]) + "\n\n"
            
            if good_stock_items:
                response += "✅ **Productos con Stock Adecuado:**\n"
                response += "\n".join(good_stock_items[:5]) + "\n\n"
            
            response += "💡 **Tip:** Usa 'inventario producto X' para detalles específicos"
            
            return response
            
        except Exception as e:
            return self._format_error_response(f"Error obteniendo inventario: {str(e)}")
    
    def _handle_general_conversation(self, message: str) -> str:
        """Manejar conversación general"""
        message_lower = message.lower()
        
        # Saludos
        if any(greeting in message_lower for greeting in ['hola', 'hello', 'buenos', 'buenas']):
            return """¡Hola! 👋 Soy tu asistente de MicroAnalytics.

🚀 **¿En qué puedo ayudarte hoy?**

Puedo ayudarte con:
• 📊 Predicciones de demanda
• 📦 Consultas de inventario
• 💰 Reportes de ventas
• 📈 Análisis de negocio

💡 **Ejemplos:**
• "Predecir producto 1"
• "¿Cuánto stock tengo?"
• "Ventas del mes"

Escribe `ayuda` para ver todos los comandos disponibles."""

        # Agradecimientos
        elif any(thanks in message_lower for thanks in ['gracias', 'thanks', 'thank']):
            return "¡De nada! 😊 Estoy aquí para ayudarte con tu negocio. ¿Hay algo más en lo que pueda asistirte?"
        
        # Despedidas
        elif any(bye in message_lower for bye in ['adiós', 'bye', 'hasta luego']):
            return "¡Hasta luego! 👋 Que tengas un excelente día con tu negocio."
        
        # Respuesta por defecto inteligente
        else:
            return """🤔 No estoy seguro de cómo ayudarte con esa consulta específica.

✨ **Prueba preguntándome:**
• "¿Qué productos tengo disponibles?"
• "Predice las ventas del producto 1"
• "¿Cómo va mi inventario?"
• "Reporte de ventas"

O escribe `ayuda` para ver todos los comandos disponibles."""
    
    def _get_historical_sales(self, product_id: int) -> List[Dict]:
        """Obtener datos históricos de ventas para un producto"""
        try:
            # Query para obtener ventas por día del último mes
            query = text("""
                SELECT 
                    DATE(t.created_at) as sale_date,
                    COUNT(*) as transactions,
                    SUM(td.quantity) as total_quantity
                FROM transactions t
                JOIN transaction_details td ON t.id = td.transaction_id
                WHERE td.product_id = :product_id
                AND t.created_at >= DATE('now', '-30 days')
                GROUP BY DATE(t.created_at)
                ORDER BY sale_date
            """)
            
            result = self.session.execute(query, {"product_id": product_id}).fetchall()
            
            return [
                {
                    'date': row[0],
                    'transactions': row[1],
                    'quantity': row[2]
                }
                for row in result
            ]
            
        except Exception as e:
            print(f"Error obteniendo datos históricos: {e}")
            return []
    
    def _calculate_smart_prediction(self, sales_data: List[Dict], days: int) -> Dict[str, Any]:
        """Calcular predicción inteligente basada en datos reales"""
        if not sales_data:
            return self._generate_fallback_prediction(days)
        
        # Extraer cantidades diarias
        daily_quantities = [item['quantity'] for item in sales_data]
        
        # Calcular estadísticas
        avg_daily_sales = np.mean(daily_quantities)
        std_daily_sales = np.std(daily_quantities)
        trend = self._calculate_trend(daily_quantities)
        
        # Generar predicción con tendencia
        predictions = []
        for i in range(days):
            # Aplicar tendencia gradual
            trend_factor = 1 + (trend * i * 0.01)  # 1% por día según tendencia
            base_prediction = avg_daily_sales * trend_factor
            
            # Agregar variación realista
            variation = np.random.normal(0, std_daily_sales * 0.3)
            prediction = max(0, base_prediction + variation)
            predictions.append(round(prediction, 1))
        
        confidence = min(0.95, 0.6 + (len(sales_data) / 30) * 0.3)  # Más datos = más confianza
        
        return {
            'predictions': predictions,
            'confidence': confidence,
            'model': 'Smart Analysis',
            'trend': 'creciente' if trend > 0 else 'decreciente' if trend < 0 else 'estable',
            'avg_daily': avg_daily_sales,
            'historical_data_points': len(sales_data)
        }
    
    def _calculate_trend(self, data: List[float]) -> float:
        """Calcular tendencia de los datos"""
        if len(data) < 3:
            return 0
        
        # Usar regresión lineal simple
        x = np.arange(len(data))
        coeffs = np.polyfit(x, data, 1)
        return coeffs[0]  # Pendiente
    
    def _generate_fallback_prediction(self, days: int) -> Dict[str, Any]:
        """Generar predicción de fallback cuando no hay datos históricos"""
        # Predicción conservadora
        base_prediction = np.random.uniform(5, 25)
        predictions = []
        
        for i in range(days):
            # Variación pequeña día a día
            variation = np.random.uniform(-2, 2)
            prediction = max(1, base_prediction + variation)
            predictions.append(round(prediction, 1))
        
        return {
            'predictions': predictions,
            'confidence': 0.4,  # Baja confianza sin datos históricos
            'model': 'Fallback Estimation',
            'trend': 'estable',
            'avg_daily': base_prediction,
            'historical_data_points': 0
        }
    
    def _generate_demo_prediction(self, product: Product, days: int) -> str:
        """Generar predicción de demostración"""
        return f"""📊 **Predicción de Demanda (Demo):**

🏷️ **Producto:** {product.nombre}
📅 **Período:** Próximos {days} días
⚠️ **Nota:** Basado en estimación (sin datos históricos)

📈 **Estimación:**
• Demanda diaria esperada: 8-15 unidades
• Total período: {days * 12:.0f} unidades aprox.
• Recomendación: Mantener stock mínimo de 100 unidades

💡 **Sugerencia:** Para predicciones más precisas, necesitamos más datos de ventas históricas."""
    
    def _format_prediction_response(self, product: Product, prediction: Dict, days: int) -> str:
        """Formatear respuesta de predicción"""
        predictions = prediction['predictions']
        confidence = prediction['confidence']
        model = prediction['model']
        trend = prediction['trend']
        
        total_predicted = sum(predictions)
        avg_daily = total_predicted / days
        
        trend_emoji = {
            'creciente': '📈',
            'decreciente': '📉',
            'estable': '📊'
        }
        
        confidence_level = "Alta" if confidence > 0.8 else "Media" if confidence > 0.6 else "Baja"
        confidence_emoji = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
        
        response = f"""📊 **Predicción de Demanda:**

🏷️ **Producto:** {product.nombre} (ID: {product.id})
📅 **Período:** Próximos {days} días
🤖 **Modelo:** {model}

📈 **Resultados:**
• Demanda total estimada: **{total_predicted:.0f} unidades**
• Promedio diario: **{avg_daily:.1f} unidades**
• Tendencia: {trend_emoji.get(trend, '📊')} **{trend.title()}**

🎯 **Confianza:** {confidence_emoji} **{confidence_level} ({confidence:.1%})**

💡 **Recomendaciones:**
• Stock recomendado: **{total_predicted * 1.2:.0f} unidades** (20% buffer)
• Punto de reorden: **{avg_daily * 7:.0f} unidades** (1 semana)
• Próxima revisión: En 1 semana

📊 **Primeros 7 días:** {', '.join([f'{p:.0f}' for p in predictions[:7]])}"""
        
        return response
    
    def _format_inventory_response(self, product: Product, inventory: Optional[Inventory]) -> str:
        """Formatear respuesta de inventario"""
        if not inventory:
            return f"""📦 **Inventario - {product.nombre}:**

⚠️ **No hay registro de inventario para este producto**

🏷️ **Información del Producto:**
• Nombre: {product.nombre}
• Precio: ${product.precio_base:.2f}
• Categoría: {product.categoria.nombre if product.categoria else 'Sin categoría'}

💡 **Sugerencia:** Registra el inventario inicial para este producto."""
        
        # Determinar estado del stock
        if inventory.stock_actual == 0:
            status = "🔴 **Sin Stock**"
            recommendation = "🚨 **URGENTE:** Reabastecer inmediatamente"
        elif inventory.stock_actual < 10:
            status = "🟡 **Stock Bajo**"
            recommendation = "⚠️ **Alerta:** Considera reordenar pronto"
        elif inventory.stock_actual < 50:
            status = "🟢 **Stock Normal**"
            recommendation = "✅ **OK:** Niveles adecuados"
        else:
            status = "🟢 **Stock Alto**"
            recommendation = "✅ **Excelente:** Stock abundante"
        
        return f"""📦 **Inventario - {product.nombre}:**

📊 **Estado Actual:**
• Cantidad disponible: **{inventory.stock_actual} unidades**
• {status}

🏷️ **Información del Producto:**
• Precio unitario: ${product.precio_base:.2f}
• Valor total en stock: ${inventory.stock_actual * product.precio_base:.2f}
• Categoría: {product.categoria.nombre if product.categoria else 'Sin categoría'}

💡 **Recomendación:**
{recommendation}

📈 **Sugerencia:** Usa 'predecir producto {product.id}' para planificar reabastecimiento"""
    
    def _format_error_response(self, message: str) -> str:
        """Formatear respuesta de error"""
        return f"""❌ **Error:**

{message}

💡 **¿Necesitas ayuda?**
• Escribe `ayuda` para ver comandos disponibles
• Verifica que el ID del producto sea correcto
• Intenta reformular tu pregunta"""
    
    def _format_warning_response(self, warning: str, additional_info: str = "") -> str:
        """Formatear respuesta de advertencia"""
        response = f"⚠️ **Advertencia:**\n\n{warning}"
        if additional_info:
            response += f"\n\n{additional_info}"
        return response
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Respuesta de error estándar"""
        return {
            "success": False,
            "error": message,
            "response": self._format_error_response(message)
        }
    
    async def _handle_model_comparison(self, message: str, matches: list) -> Dict[str, Any]:
        """Manejar comandos de comparación de modelos"""
        try:
            import re
            
            # Buscar si se especifica un producto específico
            product_match = re.search(r'producto\s+(\d+)', message.lower())
            
            if product_match:
                # Comparación para un producto específico
                product_id = int(product_match.group(1))
                
                # Verificar que el producto existe
                product = self.session.query(Product).filter(Product.id == product_id).first()
                if not product:
                    return self._error_response(f"Producto con ID {product_id} no encontrado")
                
                try:
                    from models.predict import ModelPredictor
                    predictor = ModelPredictor(product_id)
                    comparison = predictor.compare_models()
                    
                    if comparison.get('success'):
                        best_model = comparison['best_model']
                        metrics = comparison['model_metrics'].get(best_model, {})
                        
                        response = f"🤖 **Comparación de Modelos para {product.nombre}**\n\n"
                        response += f"🏆 **Mejor Modelo:** {best_model}\n"
                        response += f"📊 **Precisión (MSE):** {metrics.get('mse', 'N/A')}\n\n"
                        
                        response += "📈 **Todos los Modelos:**\n"
                        for model_name, model_metrics in comparison['model_metrics'].items():
                            response += f"• **{model_name}:** MSE = {model_metrics.get('mse', 'N/A')}\n"
                        
                        response += f"\n💡 **Recomendación:** Usa 'predecir producto {product_id}' para generar predicciones con el mejor modelo."
                        
                        return {
                            "success": True,
                            "response": response,
                            "data": comparison
                        }
                    else:
                        return self._error_response(f"Error al comparar modelos para producto {product_id}: {comparison.get('error', 'Error desconocido')}")
                        
                except Exception as e:
                    return self._error_response(f"Error al comparar modelos para producto {product_id}: {str(e)}")
            
            else:
                # Comparación general para múltiples productos
                products = self.session.query(Product).limit(5).all()  # Limitar para evitar sobrecarga
                
                if not products:
                    return {
                        "success": False,
                        "response": "❌ No hay productos disponibles para comparar modelos."
                    }
                
                comparison_results = []
                
                for product in products:
                    try:
                        from models.predict import ModelPredictor
                        predictor = ModelPredictor(product.id)
                        comparison = predictor.compare_models()
                        
                        if comparison.get('success'):
                            best_model = comparison['best_model']
                            metrics = comparison['model_metrics'].get(best_model, {})
                            
                            comparison_results.append({
                                'product_name': product.nombre,
                                'product_id': product.id,
                                'best_model': best_model,
                                'mse': metrics.get('mse', 'N/A')
                            })
                        else:
                            comparison_results.append({
                                'product_name': product.nombre,
                                'product_id': product.id,
                                'best_model': 'Error',
                                'mse': f'Error: {comparison.get("error", "Desconocido")}'
                            })
                            
                    except Exception as e:
                        comparison_results.append({
                            'product_name': product.nombre,
                            'product_id': product.id,
                            'best_model': 'Error',
                            'mse': f'Error: {str(e)}'
                        })
                
                # Formatear respuesta
                response = "🤖 **Comparación de Modelos ML - Vista General**\n\n"
                
                if comparison_results:
                    response += "📊 **Resultados por Producto:**\n\n"
                    
                    for result in comparison_results:
                        response += f"**{result['product_name']} (ID: {result['product_id']})**\n"
                        response += f"• Mejor modelo: {result['best_model']}\n"
                        response += f"• Precisión (MSE): {result['mse']}\n\n"
                    
                    response += "💡 **Recomendaciones:**\n"
                    response += "• Los modelos lineales son buenos para tendencias estables\n"
                    response += "• Los modelos polinomiales capturan mejor patrones complejos\n"
                    response += "• Usa 'comparar modelos para producto [ID]' para análisis específico\n"
                    response += "• Usa 'predecir producto [ID]' para predicciones con el mejor modelo\n"
                else:
                    response += "❌ No se pudieron obtener resultados de comparación.\n"
                    response += "Verifica que los modelos estén entrenados correctamente."
                
                return {
                    "success": True,
                    "response": response,
                    "data": comparison_results
                }
            
        except Exception as e:
            return self._error_response(f"Error al comparar modelos: {str(e)}")
