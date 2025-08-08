#!/usr/bin/env python3
"""
Script de prueba para el chatbot
"""

import re

def test_patterns():
    """Probar patrones de comando"""
    
    # Patrones de predicción
    prediction_patterns = [
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
    ]
    
    # Patrones de comparación
    comparison_patterns = [
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
    ]
    
    # Mensajes de prueba
    test_cases = [
        ("prediction", "predecir producto 1", prediction_patterns),
        ("prediction", "predicción producto 1", prediction_patterns),
        ("comparison", "comparar todos los modelos", comparison_patterns),
        ("comparison", "comparar modelos para producto 4", comparison_patterns),
        ("comparison", "cuál modelo es mejor para producto 4", comparison_patterns),
        ("comparison", "mejor modelo", comparison_patterns),
        ("comparison", "todos los modelos", comparison_patterns),
    ]
    
    print("=== PRUEBA DE PATRONES ===\n")
    
    for command_type, message, patterns in test_cases:
        print(f"Comando: {command_type}")
        print(f"Mensaje: '{message}'")
        message_lower = message.lower()
        
        found = False
        for pattern in patterns:
            try:
                match = re.search(pattern, message_lower)
                if match:
                    print(f"  ✅ ENCONTRADO con patrón: {pattern}")
                    print(f"  📊 Grupos: {match.groups()}")
                    found = True
                    break
            except re.error as e:
                print(f"  ❌ Error en patrón {pattern}: {e}")
        
        if not found:
            print("  ❌ NO ENCONTRADO")
        print("-" * 50)

if __name__ == "__main__":
    test_patterns()
