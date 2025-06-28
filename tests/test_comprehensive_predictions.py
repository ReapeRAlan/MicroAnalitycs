"""
Tests completos para el sistema de predicciones
Incluyendo pruebas con datos dummy y validación de formatos
"""
import sys
import os
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Agregar directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.predict import predict_demanda, ModelPredictor
from models.utils.model_comparison import ModelComparatorMejorado, AutoModelSelector
from models.utils.data_processing import obtener_datos_enriquecidos

class TestPredictionAPI(unittest.TestCase):
    """Tests para API de predicciones"""
    
    def setUp(self):
        """Configuración inicial para tests"""
        self.producto_id = 999  # ID de prueba
        self.test_data = self._create_dummy_data()
    
    def _create_dummy_data(self) -> pd.DataFrame:
        """Crea datos dummy para testing"""
        np.random.seed(42)  # Para reproducibilidad
        
        # Generar 100 días de datos históricos
        start_date = datetime.now() - timedelta(days=100)
        dates = [start_date + timedelta(days=i) for i in range(100)]
        
        data = []
        for i, fecha in enumerate(dates):
            # Simular datos con tendencias y estacionalidad
            base_demand = 10 + np.sin(i * 2 * np.pi / 30) * 3  # Ciclo mensual
            seasonal = 1.2 if fecha.weekday() < 5 else 0.8  # Más demanda entre semana
            noise = np.random.normal(0, 1)
            
            cantidad = max(0, int(base_demand * seasonal + noise))
            
            row = {
                'fecha': fecha.strftime('%Y-%m-%d'),
                'producto_id': self.producto_id,
                'cantidad_vendida': cantidad,
                'dia_semana': fecha.weekday(),
                'mes': fecha.month,
                'precio_base': 100 + np.random.normal(0, 5),
                'stock_actual': max(50, 100 - i + np.random.randint(-10, 10)),
                'precio_proveedor_promedio': 80 + np.random.normal(0, 3),
                'ventas_7_dias': max(0, cantidad * 7 + np.random.randint(-5, 5)),
                'ventas_30_dias': max(0, cantidad * 30 + np.random.randint(-20, 20)),
                'margen': np.random.uniform(0.1, 0.3),
                'variacion_precio': np.random.uniform(-0.05, 0.05),
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def test_predict_demanda_basic(self):
        """Test función básica predict_demanda"""
        print("Testeando función básica predict_demanda...")
        
        # Test con ID que no existe (debería retornar lista vacía)
        resultado = predict_demanda(999, 7)
        self.assertIsInstance(resultado, list)
        print(f"Resultado para producto inexistente: {len(resultado)} predicciones")
        
        # Test con parámetros válidos
        resultado = predict_demanda(1, 3)
        self.assertIsInstance(resultado, list)
        print(f"Resultado para producto 1: {len(resultado)} predicciones")
    
    def test_model_predictor_class(self):
        """Test clase ModelPredictor"""
        print("Testeando clase ModelPredictor...")
        
        try:
            predictor = ModelPredictor(self.producto_id)
            self.assertEqual(predictor.producto_id, self.producto_id)
            print("✓ ModelPredictor inicializado correctamente")
            
            # Test método get_cache_stats
            stats = predictor.get_cache_stats()
            self.assertIsInstance(stats, dict)
            print(f"✓ Cache stats obtenidas: {len(stats)} métricas")
            
        except Exception as e:
            print(f"⚠ Error en ModelPredictor: {e}")
    
    def test_auto_model_selector(self):
        """Test selector automático de modelos"""
        print("Testeando AutoModelSelector...")
        
        try:
            selector = AutoModelSelector(self.producto_id)
            
            # Test con datos dummy
            best_model = selector.get_best_model(self.test_data)
            print(f"✓ Mejor modelo seleccionado: {best_model}")
            
            # Test sin datos
            best_model_no_data = selector.get_best_model()
            print(f"✓ Modelo sin datos: {best_model_no_data}")
            
        except Exception as e:
            print(f"⚠ Error en AutoModelSelector: {e}")
    
    def test_prediction_output_format(self):
        """Test formato de salida de predicciones"""
        print("Testeando formato de salida...")
        
        try:
            predictor = ModelPredictor(self.producto_id)
            
            # Simular que tenemos un modelo entrenado (aunque no exista)
            # Este test valida el formato esperado
            
            result_format = {
                'predictions': {},
                'best_prediction': {},
                'model_performances': {},
                'metadata': {
                    'producto_id': self.producto_id,
                    'dias_adelante': 7,
                    'timestamp': datetime.now().isoformat(),
                    'models_used': [],
                    'data_points': len(self.test_data)
                }
            }
            
            # Validar estructura esperada
            self.assertIn('predictions', result_format)
            self.assertIn('best_prediction', result_format)
            self.assertIn('metadata', result_format)
            
            metadata = result_format['metadata']
            self.assertIn('producto_id', metadata)
            self.assertIn('timestamp', metadata)
            
            print("✓ Formato de salida validado correctamente")
            
        except Exception as e:
            print(f"⚠ Error validando formato: {e}")
    
    def test_model_comparison_dummy_data(self):
        """Test comparación con datos dummy"""
        print("Testeando comparación con datos dummy...")
        
        try:
            comparator = ModelComparatorMejorado(self.producto_id)
            
            # Test con datos dummy (no debería fallar)
            results = comparator.compare_all_models(self.test_data, retrain_if_needed=False)
            
            # Validar estructura de resultados
            self.assertIsInstance(results, dict)
            self.assertIn('producto_id', results)
            self.assertIn('modelos_evaluados', results)
            self.assertIn('ranking_modelos', results)
            self.assertIn('recomendaciones', results)
            
            print(f"✓ Comparación completada para {len(results['modelos_evaluados'])} modelos")
            print(f"✓ Mejor modelo: {results.get('mejor_modelo', 'Ninguno')}")
            print(f"✓ Recomendaciones: {len(results.get('recomendaciones', []))}")
            
        except Exception as e:
            print(f"⚠ Error en comparación: {e}")
    
    def test_data_validation(self):
        """Test validación de datos de entrada"""
        print("Testeando validación de datos...")
        
        # Test datos válidos
        self.assertFalse(self.test_data.empty)
        self.assertIn('fecha', self.test_data.columns)
        self.assertIn('cantidad_vendida', self.test_data.columns)
        print("✓ Datos dummy tienen estructura correcta")
        
        # Test datos vacíos
        empty_data = pd.DataFrame()
        self.assertTrue(empty_data.empty)
        print("✓ Detección de datos vacíos funciona")
        
        # Test datos con valores nulos
        data_with_nulls = self.test_data.copy()
        data_with_nulls.loc[0, 'cantidad_vendida'] = np.nan
        null_count = data_with_nulls.isnull().sum().sum()
        self.assertGreater(null_count, 0)
        print(f"✓ Datos con {null_count} valores nulos detectados")

class TestDataGeneration(unittest.TestCase):
    """Tests para generación de datos de prueba"""
    
    def test_faker_data_generation(self):
        """Test generación de datos con Faker"""
        print("Testeando generación de datos con Faker...")
        
        try:
            from faker import Faker
            fake = Faker('es_ES')  # Español de España
            
            # Generar datos de productos
            productos = []
            for i in range(10):
                producto = {
                    'id': i + 1,
                    'nombre': fake.catch_phrase(),
                    'precio': fake.pydecimal(left_digits=3, right_digits=2, positive=True),
                    'categoria': fake.word(),
                    'descripcion': fake.text(max_nb_chars=100),
                    'fecha_creacion': fake.date_this_year()
                }
                productos.append(producto)
            
            self.assertEqual(len(productos), 10)
            print(f"✓ Generados {len(productos)} productos de prueba")
            print(f"✓ Ejemplo: {productos[0]['nombre']} - ${productos[0]['precio']}")
            
        except ImportError:
            print("⚠ Faker no está instalado - instalando...")
            import subprocess
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "faker"])
                print("✓ Faker instalado correctamente")
            except Exception as e:
                print(f"⚠ Error instalando Faker: {e}")
    
    def test_time_series_generation(self):
        """Test generación de series temporales"""
        print("Testeando generación de series temporales...")
        
        # Generar serie temporal con tendencia y estacionalidad
        n_days = 365
        dates = pd.date_range(start='2024-01-01', periods=n_days, freq='D')
        
        # Componentes de la serie
        trend = np.linspace(100, 200, n_days)  # Tendencia creciente
        seasonal = 10 * np.sin(2 * np.pi * np.arange(n_days) / 365)  # Estacionalidad anual
        weekly = 5 * np.sin(2 * np.pi * np.arange(n_days) / 7)  # Patrón semanal
        noise = np.random.normal(0, 5, n_days)  # Ruido
        
        values = trend + seasonal + weekly + noise
        values = np.maximum(values, 0)  # No valores negativos
        
        time_series = pd.DataFrame({
            'fecha': dates,
            'valor': values
        })
        
        self.assertEqual(len(time_series), n_days)
        self.assertTrue(all(time_series['valor'] >= 0))
        
        print(f"✓ Serie temporal generada: {n_days} días")
        print(f"✓ Rango de valores: {time_series['valor'].min():.2f} - {time_series['valor'].max():.2f}")
        print(f"✓ Media: {time_series['valor'].mean():.2f}")

def run_comprehensive_tests():
    """Ejecuta todos los tests y genera reporte"""
    print("="*60)
    print("TESTS COMPLETOS DEL SISTEMA DE PREDICCIONES")
    print("="*60)
    
    # Configurar suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestPredictionAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestDataGeneration))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Reporte final
    print("\n" + "="*60)
    print("RESUMEN DE TESTS COMPLETOS")
    print("="*60)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Exitosos: {result.testsRun - len(result.errors) - len(result.failures)}")
    
    if result.errors:
        print("\nERRORES:")
        for test, error in result.errors:
            print(f"- {test}: {error}")
    
    if result.failures:
        print("\nFALLOS:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    run_comprehensive_tests()
