"""
Script de ejemplo para demostrar las mejoras implementadas en los modelos
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from models.training.train_regresion import ModeloLinealMejorado, SimpleDataValidator, SimpleDataCleaner
    from models.training.train_polynomial import ModeloPolinomicoMejorado
    from models.utils.model_cache import ModelCacheMejorado
    from models.utils.model_comparison import ModelComparatorMejorado
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrese de que la estructura del proyecto esté correcta")
    exit(1)

def generar_datos_ejemplo(producto_id: int = 1, n_dias: int = 180) -> pd.DataFrame:
    """
    Genera datos sintéticos realistas para demostración.
    
    Args:
        producto_id: ID del producto
        n_dias: Número de días de datos
        
    Returns:
        DataFrame con datos sintéticos
    """
    print(f"Generando {n_dias} días de datos para producto {producto_id}...")
    
    # Configurar semilla para reproducibilidad
    np.random.seed(42)
    
    # Generar fechas (asegurándonos de que sea exactamente n_dias)
    fechas = pd.date_range(
        start=datetime.now() - timedelta(days=n_dias-1),
        end=datetime.now(),
        freq='D'
    )
    
    # Verificar que tenemos exactamente n_dias
    if len(fechas) != n_dias:
        fechas = pd.date_range(
            start=datetime.now() - timedelta(days=n_dias-1),
            periods=n_dias,
            freq='D'
        )
    
    # Simular patrones realistas de venta
    n_real = len(fechas)  # Usar la longitud real de fechas
    
    # Tendencia creciente leve
    tendencia = np.linspace(10, 15, n_real)
    
    # Estacionalidad semanal (más ventas en fin de semana)
    estacionalidad_semanal = 2 * np.sin(2 * np.pi * np.arange(n_real) / 7)
    
    # Estacionalidad mensual
    estacionalidad_mensual = 3 * np.sin(2 * np.pi * np.arange(n_real) / 30)
    
    # Ruido aleatorio
    ruido = np.random.normal(0, 2, n_real)
    
    # Eventos especiales (picos de venta ocasionales)
    eventos = np.zeros(n_real)
    indices_eventos = np.random.choice(n_real, size=int(n_real * 0.05), replace=False)
    eventos[indices_eventos] = np.random.uniform(5, 15, len(indices_eventos))
    
    # Ventas finales
    ventas_base = tendencia + estacionalidad_semanal + estacionalidad_mensual + ruido + eventos
    ventas = np.maximum(ventas_base, 0)  # No ventas negativas
    
    # Crear DataFrame
    data = pd.DataFrame({
        'fecha': fechas,
        'producto_id': [producto_id] * len(fechas),  # Usar len(fechas) para estar seguros
        'cantidad_vendida': ventas,
        'precio_base': 100 + np.random.uniform(-20, 20, len(fechas)),
        'stock_actual': np.random.randint(5, 100, len(fechas)),
        'precio_proveedor_promedio': 70 + np.random.uniform(-10, 10, len(fechas)),
        'dia_semana': [fecha.weekday() for fecha in fechas],
        'mes': [fecha.month for fecha in fechas],
        'margen': np.random.uniform(0.2, 0.4, len(fechas)),
        'variacion_precio': np.random.uniform(-0.1, 0.1, len(fechas)),
        'precio_competencia': 105 + np.random.uniform(-25, 25, len(fechas)),
        'promocion_activa': np.random.choice([0, 1], len(fechas), p=[0.8, 0.2])
    })
    
    # Calcular features derivados
    data['ventas_7_dias'] = data['cantidad_vendida'].rolling(window=7, min_periods=1).mean()
    data['ventas_30_dias'] = data['cantidad_vendida'].rolling(window=30, min_periods=1).mean()
    
    # Calcular tendencia
    def calcular_tendencia(serie):
        if len(serie) < 2:
            return 0
        x = np.arange(len(serie))
        try:
            return np.polyfit(x, serie, 1)[0]
        except:
            return 0
    
    data['tendencia_30_dias'] = data['cantidad_vendida'].rolling(
        window=30, min_periods=2
    ).apply(calcular_tendencia)
    
    # Estacionalidad simple (promedio por día de la semana)
    try:
        estacionalidad = data.groupby('dia_semana')['cantidad_vendida'].transform('mean')
        data['estacionalidad'] = estacionalidad / data['cantidad_vendida'].mean()
    except Exception:
        # Fallback en caso de error
        data['estacionalidad'] = 1.0
    
    print(f"✓ Datos generados: {len(data)} registros desde {data['fecha'].min()} hasta {data['fecha'].max()}")
    return data

def demostrar_validacion_y_limpieza(data: pd.DataFrame) -> pd.DataFrame:
    """Demuestra la validación y limpieza de datos."""
    print("\n" + "="*60)
    print("DEMOSTRACIÓN: VALIDACIÓN Y LIMPIEZA DE DATOS")
    print("="*60)
    
    # Introducir algunos problemas en los datos para demostración
    data_con_problemas = data.copy()
    
    # Simular valores faltantes de forma más simple
    n_problemas = max(1, int(len(data) * 0.05))
    
    # Seleccionar índices aleatorios y convertir a lista
    np.random.seed(42)  # Para reproducibilidad
    indices_precio = np.random.choice(len(data), size=min(5, n_problemas), replace=False)
    indices_stock = np.random.choice(len(data), size=min(3, n_problemas), replace=False)
    
    # Introducir valores faltantes usando un bucle simple
    for idx in indices_precio:
        data_con_problemas.at[idx, 'precio_base'] = np.nan
    
    for idx in indices_stock:
        data_con_problemas.at[idx, 'stock_actual'] = np.nan
    
    print(f"Datos originales: {len(data)} registros")
    print(f"Datos con problemas introducidos: {data_con_problemas.isnull().sum().sum()} valores faltantes")
    
    # 1. Validación de datos
    print("\n1. Validando calidad de datos...")
    validator = SimpleDataValidator()
    issues = validator.validate_data_quality(data_con_problemas, 1)
    
    if issues:
        print("   Problemas encontrados:")
        for problema, detalle in issues.items():
            print(f"   - {problema}: {detalle}")
    else:
        print("   ✓ No se encontraron problemas críticos")
    
    # 2. Limpieza de datos
    print("\n2. Limpiando datos...")
    cleaner = SimpleDataCleaner()
    datos_limpios = cleaner.clean_data(data_con_problemas, 1)
    
    print(f"   Antes de limpieza: {len(data_con_problemas)} registros, {data_con_problemas.isnull().sum().sum()} valores faltantes")
    print(f"   Después de limpieza: {len(datos_limpios)} registros, {datos_limpios.isnull().sum().sum()} valores faltantes")
    print(f"   ✓ Datos limpiados exitosamente")
    
    return datos_limpios

def demostrar_entrenamiento_modelos(data: pd.DataFrame):
    """Demuestra el entrenamiento de modelos mejorados."""
    print("\n" + "="*60)
    print("DEMOSTRACIÓN: ENTRENAMIENTO DE MODELOS MEJORADOS")
    print("="*60)
    
    producto_id = 1
    
    # 1. Modelo Lineal Mejorado
    print("\n1. Entrenando Modelo Lineal Mejorado...")
    try:
        modelo_lineal = ModeloLinealMejorado(producto_id)
        
        # Mock del método de datos para usar nuestros datos de ejemplo
        modelo_lineal._get_validated_data = lambda: data
        
        resultado_lineal = modelo_lineal.train_with_validation(model_type='auto')
        
        if resultado_lineal and 'error' not in resultado_lineal:
            print("   ✓ Modelo lineal entrenado exitosamente")
            print(f"   - Tipo de modelo: {resultado_lineal.get('modelo_tipo', 'No especificado')}")
            
            metricas = resultado_lineal.get('metricas', {})
            if metricas:
                print(f"   - R² promedio: {metricas.get('r2_medio', 0):.4f}")
                print(f"   - MAE promedio: {metricas.get('mae_medio', 0):.4f}")
                print(f"   - MAPE promedio: {metricas.get('mape_medio', 0):.2f}%")
        else:
            print("   ⚠ Error en entrenamiento de modelo lineal (posible falta de dependencias)")
            
    except Exception as e:
        print(f"   ⚠ Error entrenando modelo lineal: {e}")
    
    # 2. Modelo Polinómico Mejorado
    print("\n2. Entrenando Modelo Polinómico Mejorado...")
    try:
        modelo_poly = ModeloPolinomicoMejorado(producto_id, grado=2)
        
        # Mock del método de datos
        modelo_poly._get_validated_data = lambda: data
        
        resultado_poly = modelo_poly.train_with_validation()
        
        if resultado_poly and 'error' not in resultado_poly:
            print("   ✓ Modelo polinómico entrenado exitosamente")
            print(f"   - Grado del polinomio: {resultado_poly.get('grado_polinomio', 2)}")
            
            metricas = resultado_poly.get('metricas', {})
            if metricas:
                print(f"   - R² promedio: {metricas.get('r2_medio', 0):.4f}")
                print(f"   - MAE promedio: {metricas.get('mae_medio', 0):.4f}")
                print(f"   - MAPE promedio: {metricas.get('mape_medio', 0):.2f}%")
        else:
            print("   ⚠ Error en entrenamiento de modelo polinómico (posible falta de dependencias)")
            
    except Exception as e:
        print(f"   ⚠ Error entrenando modelo polinómico: {e}")

def demostrar_cache_modelos():
    """Demuestra el sistema de caché de modelos."""
    print("\n" + "="*60)
    print("DEMOSTRACIÓN: SISTEMA DE CACHÉ DE MODELOS")
    print("="*60)
    
    try:
        # Crear instancia de caché
        cache = ModelCacheMejorado()
        
        # Modelo mock para demostración
        modelo_ejemplo = {
            'tipo': 'linear_regression',
            'coeficientes': [1.5, -0.3, 2.1, 0.8],
            'intercept': 5.2,
            'r2_score': 0.85,
            'entrenado_en': datetime.now().isoformat()
        }
        
        print("\n1. Cacheando modelo...")
        cache_id = cache.cache_model(
            modelo_ejemplo,
            producto_id=1,
            model_type='linear',
            metadata={
                'features_utilizadas': ['precio', 'stock', 'dia_semana', 'mes'],
                'datos_entrenamiento': 180,
                'validacion_cruzada': True
            }
        )
        
        if cache_id:
            print(f"   ✓ Modelo cacheado con ID: {cache_id}")
        else:
            print("   ⚠ Error cacheando modelo")
            return
        
        print("\n2. Cargando modelo desde caché...")
        modelo_cargado, metadata = cache.load_model(cache_id=cache_id)
        
        if modelo_cargado:
            print(f"   ✓ Modelo cargado exitosamente")
            print(f"   - Tipo: {modelo_cargado.get('tipo')}")
            print(f"   - R² Score: {modelo_cargado.get('r2_score')}")
            if metadata:
                print(f"   - Features en metadata: {metadata.get('features_utilizadas', [])}")
            else:
                print("   - Metadata no disponible")
        else:
            print("   ⚠ Error cargando modelo")
        
        print("\n3. Cacheando predicción...")
        prediccion_ejemplo = [12.5, 15.2, 18.1, 14.7, 16.3]
        input_hash = "ejemplo_hash_12345"
        
        pred_id = cache.cache_prediction(
            prediccion_ejemplo,
            producto_id=1,
            input_hash=input_hash,
            model_cache_id=cache_id
        )
        
        if pred_id:
            print(f"   ✓ Predicción cacheada con ID: {pred_id}")
        
        print("\n4. Cargando predicción desde caché...")
        prediccion_cargada = cache.load_prediction(1, input_hash)
        
        if prediccion_cargada:
            print(f"   ✓ Predicción cargada: {prediccion_cargada}")
        
        print("\n5. Estadísticas del caché...")
        stats = cache.get_cache_stats()
        
        print(f"   - Modelos en caché: {stats['models']['count']}")
        print(f"   - Predicciones en caché: {stats['predictions']['count']}")
        print(f"   - Tamaño total (MB): {stats['models']['total_size_mb']:.2f}")
        print(f"   - Estado del caché: {stats['cache_health']}")
        
    except Exception as e:
        print(f"   ⚠ Error en demostración de caché: {e}")

def demostrar_comparacion_modelos(data: pd.DataFrame):
    """Demuestra el sistema de comparación de modelos."""
    print("\n" + "="*60)
    print("DEMOSTRACIÓN: COMPARACIÓN Y SELECCIÓN DE MODELOS")
    print("="*60)
    
    try:
        comparator = ModelComparatorMejorado(1)
        
        # Mock de evaluación para demostración
        def mock_evaluate_model(model_name, config, data, retrain):
            """Mock de evaluación que simula resultados realistas"""
            # Simular diferentes niveles de rendimiento por tipo de modelo
            base_metrics = {
                'linear_auto': {'r2': 0.75, 'mape': 18.5, 'interpretability': 0.9, 'robustness': 0.6},
                'linear_ridge': {'r2': 0.78, 'mape': 17.2, 'interpretability': 0.85, 'robustness': 0.7},
                'polynomial_2': {'r2': 0.82, 'mape': 15.8, 'interpretability': 0.7, 'robustness': 0.5},
                'polynomial_3': {'r2': 0.79, 'mape': 16.9, 'interpretability': 0.6, 'robustness': 0.4},
                'polynomial_auto': {'r2': 0.84, 'mape': 14.2, 'interpretability': 0.5, 'robustness': 0.3}
            }
            
            metrics = base_metrics.get(model_name, {'r2': 0.7, 'mape': 20.0, 'interpretability': 0.5, 'robustness': 0.5})
            
            return {
                'modelo_nombre': model_name,
                'evaluado': True,
                'metricas_validacion': {
                    'r2': {'mean': metrics['r2'], 'std': 0.05},
                    'mae': {'mean': 2.5, 'std': 0.3},
                    'mape': {'mean': metrics['mape'], 'std': 2.0},
                    'rmse': {'mean': 3.2, 'std': 0.4}
                },
                'metricas_rendimiento': {
                    'interpretabilidad': metrics['interpretability'],
                    'robustez_outliers': metrics['robustness'],
                    'complejidad': 1 - metrics['interpretability'],
                    'tamaño_modelo_mb': 0.5
                },
                'fecha_evaluacion': datetime.now().isoformat(),
                'entrenado_recientemente': True
            }
        
        # Reemplazar método de evaluación
        comparator._evaluate_model = mock_evaluate_model
        
        print("\n1. Evaluando modelos disponibles...")
        resultado = comparator.compare_all_models(data, retrain_if_needed=False)
        
        if 'error' not in resultado:
            print(f"   ✓ Comparación completada para producto {resultado['producto_id']}")
            print(f"   - Modelos evaluados: {resultado['metricas_resumen']['modelos_evaluados']}")
            print(f"   - Mejor R²: {resultado['metricas_resumen']['mejor_r2']:.4f}")
            print(f"   - Mejor MAPE: {resultado['metricas_resumen']['mejor_mape']:.2f}%")
            
            print(f"\n2. Ranking de modelos:")
            for i, modelo in enumerate(resultado['ranking_modelos'][:3], 1):
                print(f"   {i}. {modelo['modelo']}")
                print(f"      - Score combinado: {modelo['score_combinado']:.4f}")
                print(f"      - R²: {modelo['r2']:.4f}")
                print(f"      - MAPE: {modelo['mape']:.2f}%")
                print(f"      - Interpretabilidad: {modelo['interpretabilidad']:.2f}")
            
            if resultado.get('mejor_modelo'):
                print(f"\n3. Mejor modelo seleccionado: {resultado['mejor_modelo']}")
            
            if resultado.get('recomendaciones'):
                print(f"\n4. Recomendaciones:")
                for recomendacion in resultado['recomendaciones']:
                    print(f"   - {recomendacion}")
        else:
            print(f"   ⚠ Error en comparación: {resultado.get('error')}")
            
    except Exception as e:
        print(f"   ⚠ Error en demostración de comparación: {e}")

def mostrar_resumen_mejoras():
    """Muestra un resumen de todas las mejoras implementadas."""
    print("\n" + "="*80)
    print("RESUMEN DE MEJORAS IMPLEMENTADAS")
    print("="*80)
    
    mejoras = [
        {
            'categoria': 'VALIDACIÓN Y CALIDAD DE DATOS',
            'mejoras': [
                'Validación automática de columnas requeridas',
                'Detección de valores faltantes críticos',
                'Limpieza automática de datos con múltiples estrategias',
                'Actualización automática de features históricos',
                'Manejo robusto de datos inconsistentes'
            ]
        },
        {
            'categoria': 'MEJORAS EN MODELOS',
            'mejoras': [
                'Selección automática del mejor algoritmo',
                'Optimización de hiperparámetros con GridSearch',
                'Validación cruzada temporal para series de tiempo',
                'Escalado robusto menos sensible a outliers',
                'Selección automática de features relevantes',
                'Múltiples métricas de evaluación (R², MAE, RMSE, MAPE)'
            ]
        },
        {
            'categoria': 'SISTEMA DE CACHÉ',
            'mejoras': [
                'Caché comprimido para modelos y predicciones',
                'Versionado automático de modelos',
                'Metadata rica para tracking de modelos',
                'Limpieza automática de caché obsoleto',
                'Estadísticas y monitoreo del caché',
                'Caché de predicciones para evitar recálculos'
            ]
        },
        {
            'categoria': 'COMPARACIÓN Y SELECCIÓN',
            'mejoras': [
                'Comparación automática de múltiples algoritmos',
                'Ranking basado en múltiples criterios',
                'Métricas de interpretabilidad y robustez',
                'Recomendaciones automáticas basadas en rendimiento',
                'Análisis de trade-offs entre precisión y complejidad',
                'Persistencia de resultados de comparación'
            ]
        },
        {
            'categoria': 'MANEJO DE ERRORES Y LOGGING',
            'mejoras': [
                'Manejo robusto de dependencias faltantes',
                'Decoradores para manejo automático de errores',
                'Logging detallado de operaciones',
                'Fallbacks para operaciones críticas',
                'Validación de entrada en todos los métodos'
            ]
        }
    ]
    
    for categoria_info in mejoras:
        print(f"\n{categoria_info['categoria']}:")
        for i, mejora in enumerate(categoria_info['mejoras'], 1):
            print(f"  {i}. {mejora}")
    
    print("\n" + "="*80)
    print("BENEFICIOS PRINCIPALES:")
    print("="*80)
    
    beneficios = [
        "✓ Mayor precisión en predicciones",
        "✓ Selección automática del mejor modelo",
        "✓ Manejo robusto de datos de baja calidad",
        "✓ Mejor rendimiento con caché inteligente",
        "✓ Facilidad de uso con configuración automática",
        "✓ Monitoreo y tracking completo",
        "✓ Escalabilidad mejorada",
        "✓ Mantenimiento simplificado"
    ]
    
    for beneficio in beneficios:
        print(f"  {beneficio}")

def main():
    """Función principal que ejecuta todas las demostraciones."""
    print("DEMOSTRACIÓN DE MEJORAS EN MODELOS DE MICROANALYTICS")
    print("="*80)
    print("Este script demuestra las mejoras implementadas en los modelos de predicción")
    print("para el sistema MicroAnalytics.")
    print()
    
    try:
        # 1. Generar datos de ejemplo
        data = generar_datos_ejemplo(producto_id=1, n_dias=180)
        
        # 2. Demostrar validación y limpieza
        data_limpia = demostrar_validacion_y_limpieza(data)
        
        # 3. Demostrar entrenamiento de modelos
        demostrar_entrenamiento_modelos(data_limpia)
        
        # 4. Demostrar sistema de caché
        demostrar_cache_modelos()
        
        # 5. Demostrar comparación de modelos
        demostrar_comparacion_modelos(data_limpia)
        
        # 6. Mostrar resumen de mejoras
        mostrar_resumen_mejoras()
        
        print("\n" + "="*80)
        print("✓ DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80)
        print()
        print("Para usar estas mejoras en producción:")
        print("1. Instale las dependencias: pip install -r requirements.txt")
        print("2. Configure las rutas de datos en data_processing.py")
        print("3. Ejecute los modelos con: python -m models.training.train_regresion")
        print("4. Use la comparación con: python -m models.utils.model_comparison")
        
    except Exception as e:
        print(f"\n❌ Error en demostración: {e}")
        print("Verifique que todas las dependencias estén instaladas y la estructura del proyecto sea correcta")

if __name__ == "__main__":
    main()
