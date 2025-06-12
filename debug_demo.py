#!/usr/bin/env python3
"""
Script de depuración para identificar el problema en la generación de datos.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def debug_generar_datos(producto_id: int = 1, n_dias: int = 180):
    """Versión simplificada para depuración."""
    print(f"Generando datos para {n_dias} días...")
    
    # Generar fechas
    fechas = pd.date_range(
        start=datetime.now() - timedelta(days=n_dias),
        end=datetime.now(),
        freq='D'
    )
    print(f"Fechas generadas: {len(fechas)}")
    
    # Simular patrones realistas de venta
    tendencia = np.linspace(10, 15, n_dias)
    print(f"Tendencia: {len(tendencia)}")
    
    estacionalidad_semanal = 2 * np.sin(2 * np.pi * np.arange(n_dias) / 7)
    print(f"Estacionalidad semanal: {len(estacionalidad_semanal)}")
    
    estacionalidad_mensual = 3 * np.sin(2 * np.pi * np.arange(n_dias) / 30)
    print(f"Estacionalidad mensual: {len(estacionalidad_mensual)}")
    
    ruido = np.random.normal(0, 2, n_dias)
    print(f"Ruido: {len(ruido)}")
    
    eventos = np.zeros(n_dias)
    indices_eventos = np.random.choice(n_dias, size=int(n_dias * 0.05), replace=False)
    eventos[indices_eventos] = np.random.uniform(5, 15, len(indices_eventos))
    print(f"Eventos: {len(eventos)}")
    
    # Ventas finales
    ventas_base = tendencia + estacionalidad_semanal + estacionalidad_mensual + ruido + eventos
    ventas = np.maximum(ventas_base, 0)
    print(f"Ventas: {len(ventas)}")
    
    # Crear cada columna individualmente
    print("Creando DataFrame...")
    
    # Verificar todas las longitudes antes de crear el DataFrame
    columnas = {
        'fecha': fechas,
        'producto_id': [producto_id] * n_dias,
        'cantidad_vendida': ventas,
        'precio_base': 100 + np.random.uniform(-20, 20, n_dias),
        'stock_actual': np.random.randint(5, 100, n_dias),
        'precio_proveedor_promedio': 70 + np.random.uniform(-10, 10, n_dias),
        'dia_semana': [fecha.weekday() for fecha in fechas],
        'mes': [fecha.month for fecha in fechas],
        'margen': np.random.uniform(0.2, 0.4, n_dias),
        'variacion_precio': np.random.uniform(-0.1, 0.1, n_dias),
        'precio_competencia': 105 + np.random.uniform(-25, 25, n_dias),
        'promocion_activa': np.random.choice([0, 1], n_dias, p=[0.8, 0.2])
    }
    
    # Verificar longitudes
    for nombre, valores in columnas.items():
        print(f"{nombre}: {len(valores)}")
    
    # Crear DataFrame
    try:
        data = pd.DataFrame(columnas)
        print(f"DataFrame creado exitosamente: {len(data)} filas")
        return data
    except Exception as e:
        print(f"Error creando DataFrame: {e}")
        return None

if __name__ == "__main__":
    print("=== DEBUG: Generación de datos ===")
    data = debug_generar_datos()
    if data is not None:
        print("¡Éxito!")
        print(data.head())
    else:
        print("Falló la generación de datos")
