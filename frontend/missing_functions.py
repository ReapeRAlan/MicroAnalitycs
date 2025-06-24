"""
Funciones faltantes para agregar al chatbot
"""

def _generate_prediction_interpretation(self, prediction_data: dict, user_input: str) -> str:
    """Generar interpretación detallada de la predicción"""
    try:
        product_id = prediction_data.get('producto_id', 'N/A')
        predictions = prediction_data.get('predicciones', [])
        confidence = prediction_data.get('confianza', 0)
        model = prediction_data.get('mejor_modelo', 'unknown')
        
        if not predictions:
            return "No se pudieron generar predicciones para este producto."
        
        avg_demand = sum(predictions) / len(predictions)
        
        response = f"""
**📊 Predicción para Producto {product_id}**

🎯 **Demanda promedio proyectada**: {avg_demand:.1f} unidades
🤖 **Modelo utilizado**: {model.title()}
📈 **Confianza**: {confidence:.1%}
📊 **Período**: {len(predictions)} días

**💡 Recomendaciones:**
"""
        
        if avg_demand > 100:
            response += """
🔥 **Alta demanda proyectada**
- Aumentar inventario inmediatamente
- Stock recomendado: {:.0f} unidades
""".format(avg_demand * 1.5)
        elif avg_demand > 50:
            response += """
✅ **Demanda moderada**
- Mantener niveles actuales
- Stock recomendado: {:.0f} unidades
""".format(avg_demand * 1.3)
        else:
            response += """
📉 **Demanda baja**
- Evaluar promociones
- Reducir inventario gradualmente
"""
        
        return response
        
    except Exception as e:
        return f"Error generando interpretación: {str(e)}"


def _generate_comparison_interpretation(self, comparison_data: dict, user_input: str) -> str:
    """Generar interpretación de comparación de modelos"""
    try:
        response = f"""
**🔍 Análisis de Comparación de Modelos**

Los modelos han sido evaluados y aquí están los resultados:

**📊 Métricas explicadas:**
- **R² Score**: Qué tan bien explica el modelo tus datos (mayor = mejor)
- **MSE**: Error cuadrático medio (menor = mejor)
- **MAE**: Error absoluto medio (menor = mejor)

**💡 Recomendación:**
Usa el modelo con **mayor R²** para tus predicciones futuras.

**🎯 Guía rápida:**
- Linear: ⚡ Rápido para tendencias simples
- Polynomial: 🔄 Mejor para patrones complejos  
- Random Forest: 🎯 Máxima precisión

**📋 Próximos pasos:**
1. Implementa el modelo recomendado
2. Monitorea precisión por 2 semanas
3. Re-evalúa mensualmente
"""
        return response
        
    except Exception as e:
        return f"Error en interpretación de comparación: {str(e)}"


def _extract_product_id(self, user_input: str) -> int:
    """Extraer ID de producto del input"""
    import re
    
    # Buscar "producto X"
    match = re.search(r'producto\s+(\d+)', user_input.lower())
    if match:
        return int(match.group(1))
    
    # Buscar números en el texto
    numbers = re.findall(r'\b\d+\b', user_input)
    if numbers:
        return int(numbers[0])
    
    # Mapear categorías a IDs
    user_lower = user_input.lower()
    if 'ropa' in user_lower:
        return 1
    elif 'electronica' in user_lower:
        return 2
    elif 'comida' in user_lower:
        return 3
    else:
        return 1  # Por defecto


def _handle_general_chat(self, user_input: str) -> str:
    """Manejar chat general usando Ollama o fallback"""
    try:
        if self.ollama_client:
            # Usar Ollama para respuesta natural
            conversation_context = self._build_conversation_context()
            return asyncio.run(self._get_ollama_response(user_input, conversation_context))
        else:
            return self._get_intelligent_fallback(user_input)
    except Exception as e:
        return self._get_intelligent_fallback(user_input)


def _get_intelligent_fallback(self, user_input: str) -> str:
    """Respuesta inteligente de fallback"""
    user_lower = user_input.lower()
    
    if any(word in user_lower for word in ['hola', 'hi', 'buenos']):
        return """¡Hola! 👋 Soy tu asistente de análisis de demanda.

**¿En qué puedo ayudarte?**
- 📊 Predicciones de demanda
- 🔍 Comparación de modelos  
- 📈 Análisis de tendencias

**Ejemplos:**
- "¿Qué modelo es mejor?"
- "¿Qué se espera para la ropa?"
- "Predice la demanda del producto 1"
"""
    
    elif any(word in user_lower for word in ['gracias', 'thanks']):
        return "¡De nada! 😊 ¿Hay algo más en lo que pueda ayudarte?"
    
    elif 'productos' in user_lower and 'conservar' in user_lower:
        return """📊 **Análisis de Productos a Conservar**

Para recomendarte qué productos conservar, necesito analizar:

1. **📈 Demanda proyectada** de cada producto
2. **💰 Rentabilidad** por unidad
3. **🔄 Rotación** de inventario
4. **📊 Tendencias** del mercado

**¿Podrías especificar?**
- ¿Tienes productos específicos en mente?
- ¿Qué categoría te interesa más?
- ¿Buscas análisis por rentabilidad o demanda?

**Ejemplos de consultas:**
- "Analiza la rentabilidad de la ropa"
- "¿Qué productos de electrónicos tienen más demanda?"
- "Compara la rentabilidad de mis productos"
"""
    
    else:
        return """No estoy seguro de cómo ayudarte con esa consulta específica.

**Puedo ayudarte con:**
- 📊 **Predicciones**: "Predice la demanda del producto X"
- 🔍 **Comparaciones**: "¿Qué modelo es más preciso?"
- 📈 **Análisis**: "Analiza las tendencias de ropa"

¿Podrías ser más específico sobre lo que necesitas?"""
