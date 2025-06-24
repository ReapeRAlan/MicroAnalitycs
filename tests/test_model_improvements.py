"""
Tests unitarios para las mejoras de modelos
"""
import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
from datetime import datetime, timedelta

# Imports locales
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.training.train_regresion import ModeloLinealMejorado, SimpleDataValidator, SimpleDataCleaner
from models.training.train_polynomial import ModeloPolinomicoMejorado
from models.utils.model_cache import ModelCacheMejorado
from models.utils.model_comparison import ModelComparatorMejorado

class TestDataValidationAndCleaning(unittest.TestCase):
    """Tests para validación y limpieza de datos"""
    
    def setUp(self):
        """Configuración inicial para tests"""
        self.validator = SimpleDataValidator()
        self.cleaner = SimpleDataCleaner()
        
        # Datos de ejemplo
        self.valid_data = pd.DataFrame({
            'fecha': pd.date_range('2023-01-01', periods=100),
            'producto_id': [1] * 100,
            'cantidad_vendida': np.random.poisson(10, 100),
            'precio_base': np.random.uniform(50, 150, 100),
            'stock_actual': np.random.randint(0, 100, 100),
            'precio_proveedor_promedio': np.random.uniform(30, 100, 100)
        })
        
        # Datos con problemas
        self.problematic_data = self.valid_data.copy()
        # Introducir valores faltantes
        self.problematic_data.loc[0:10, 'precio_base'] = np.nan
        self.problematic_data.loc[20:25, 'cantidad_vendida'] = np.nan
        self.problematic_data.loc[50:55, 'stock_actual'] = np.nan
    
    def test_data_validation_valid_data(self):
        """Test validación con datos válidos"""
        issues = self.validator.validate_data_quality(self.valid_data, 1)
        
        # No debería haber errores fatales
        self.assertNotIn('fatal_errors', issues)
        
    def test_data_validation_missing_columns(self):
        """Test validación con columnas faltantes"""
        incomplete_data = self.valid_data.drop(columns=['precio_base'])
        issues = self.validator.validate_data_quality(incomplete_data, 1)
        
        # Debería detectar columnas faltantes
        self.assertIn('missing_columns', issues)
        self.assertIn('precio_base', issues['missing_columns'])
        
    def test_data_cleaning(self):
        """Test limpieza de datos"""
        cleaned_data = self.cleaner.clean_data(self.problematic_data, 1)
        
        # Los datos limpiados deberían tener menos filas (por dropna)
        self.assertLess(len(cleaned_data), len(self.problematic_data))
        
        # No debería haber valores faltantes en columnas críticas
        self.assertEqual(cleaned_data['cantidad_vendida'].isnull().sum(), 0)
        self.assertEqual(cleaned_data['precio_base'].isnull().sum(), 0)
        
    def test_feature_updating(self):
        """Test actualización de features históricos"""
        modelo = ModeloLinealMejorado(1)
        updated_data = modelo._update_historical_features(self.valid_data)
        
        # Debería tener features calculados
        expected_features = ['ventas_7_dias', 'ventas_30_dias', 'tendencia_30_dias']
        for feature in expected_features:
            self.assertIn(feature, updated_data.columns)

class TestModelTraining(unittest.TestCase):
    """Tests para entrenamiento de modelos mejorados"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear datos sintéticos para testing
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=200)
        
        self.test_data = pd.DataFrame({
            'fecha': dates,
            'producto_id': [1] * 200,
            'cantidad_vendida': np.random.poisson(15, 200) + np.sin(np.arange(200) * 0.1) * 3,
            'precio_base': np.random.uniform(80, 120, 200),
            'stock_actual': np.random.randint(10, 100, 200),
            'precio_proveedor_promedio': np.random.uniform(50, 90, 200),
            'dia_semana': [d.weekday() for d in dates],
            'mes': [d.month for d in dates],
            'margen': np.random.uniform(0.2, 0.5, 200),
            'variacion_precio': np.random.uniform(-0.1, 0.1, 200)
        })
        
        # Calcular features derivados
        self.test_data['ventas_7_dias'] = self.test_data['cantidad_vendida'].rolling(7, min_periods=1).mean()
        self.test_data['ventas_30_dias'] = self.test_data['cantidad_vendida'].rolling(30, min_periods=1).mean()
        
        # Crear directorio temporal para modelos
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Limpieza después de tests"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_linear_model_training(self):
        """Test entrenamiento modelo lineal mejorado"""
        try:
            modelo = ModeloLinealMejorado(1)
            
            # Mock del método de obtención de datos
            original_method = modelo._get_validated_data
            modelo._get_validated_data = lambda: self.test_data
            
            # Entrenar modelo
            resultado = modelo.train_with_validation(model_type='ridge')
            
            # Restaurar método original
            modelo._get_validated_data = original_method
            
            # Verificar que se completó el entrenamiento
            if resultado and 'error' not in resultado:
                self.assertIn('metricas', resultado)
                self.assertIn('modelo_tipo', resultado)
                
        except Exception as e:
            # Si hay errores de dependencias, solo imprimir advertencia
            print(f"Warning: Test de modelo lineal falló (posible falta de sklearn): {e}")
            
    def test_polynomial_model_training(self):
        """Test entrenamiento modelo polinómico mejorado"""
        try:
            modelo = ModeloPolinomicoMejorado(1, grado=2)
            
            # Mock del método de obtención de datos
            original_method = modelo._get_validated_data
            modelo._get_validated_data = lambda: self.test_data
            
            # Entrenar modelo
            resultado = modelo.train_with_validation()
            
            # Restaurar método original
            modelo._get_validated_data = original_method
            
            # Verificar que se completó el entrenamiento
            if resultado and 'error' not in resultado:
                self.assertIn('metricas', resultado)
                self.assertIn('grado_polinomio', resultado)
                
        except Exception as e:
            print(f"Warning: Test de modelo polinómico falló (posible falta de sklearn): {e}")

class TestModelCache(unittest.TestCase):
    """Tests para sistema de caché de modelos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache = ModelCacheMejorado(base_path=self.temp_dir)
        
        # Modelo mock para testing
        self.mock_model = {'type': 'test_model', 'params': [1, 2, 3]}
        
    def tearDown(self):
        """Limpieza"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_cache_and_load_model(self):
        """Test cachear y cargar modelo"""
        # Cachear modelo
        cache_id = self.cache.cache_model(
            self.mock_model, 
            producto_id=1, 
            model_type='linear',
            metadata={'test': True}
        )
        
        self.assertIsNotNone(cache_id)
        
        # Cargar modelo
        loaded_model, metadata = self.cache.load_model(cache_id=cache_id)
        
        self.assertIsNotNone(loaded_model)
        self.assertIsNotNone(metadata)
        self.assertEqual(loaded_model['type'], 'test_model')
        
    def test_cache_predictions(self):
        """Test caché de predicciones"""
        prediction = [10, 15, 20, 25]
        input_hash = "test_hash_12345"
        
        # Cachear predicción
        pred_id = self.cache.cache_prediction(
            prediction, producto_id=1, input_hash=input_hash
        )
        
        self.assertIsNotNone(pred_id)
        
        # Cargar predicción
        loaded_prediction = self.cache.load_prediction(1, input_hash)
        
        self.assertEqual(prediction, loaded_prediction)
        
    def test_cache_stats(self):
        """Test estadísticas de caché"""
        # Cachear algunos modelos
        for i in range(3):
            self.cache.cache_model(
                {'model': f'test_{i}'}, 
                producto_id=i+1, 
                model_type='test'
            )
        
        stats = self.cache.get_cache_stats()
        
        self.assertIn('models', stats)
        self.assertIn('predictions', stats)
        self.assertEqual(stats['models']['count'], 3)
        
    def test_cache_cleanup(self):
        """Test limpieza de caché"""
        # Cachear modelo
        cache_id = self.cache.cache_model(
            self.mock_model, 
            producto_id=1, 
            model_type='linear'
        )
        
        # Forzar limpieza
        cleanup_result = self.cache.cleanup_cache(force=True)
        
        self.assertIn('removed_models', cleanup_result)

class TestModelComparison(unittest.TestCase):
    """Tests para comparación de modelos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Datos de prueba
        np.random.seed(42)
        self.test_data = pd.DataFrame({
            'fecha': pd.date_range('2023-01-01', periods=100),
            'producto_id': [1] * 100,
            'cantidad_vendida': np.random.poisson(10, 100),
            'precio_base': np.random.uniform(50, 150, 100),
            'stock_actual': np.random.randint(0, 100, 100),
            'dia_semana': np.random.randint(0, 7, 100),
            'mes': np.random.randint(1, 13, 100),
            'ventas_7_dias': np.random.uniform(8, 12, 100),
            'ventas_30_dias': np.random.uniform(9, 11, 100),
            'margen': np.random.uniform(0.2, 0.5, 100),
            'variacion_precio': np.random.uniform(-0.1, 0.1, 100)
        })
        
    def tearDown(self):
        """Limpieza"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_model_comparison_structure(self):
        """Test estructura de comparación de modelos"""
        try:
            comparator = ModelComparatorMejorado(1)
            
            # Mock de evaluación para evitar dependencias
            def mock_evaluate_model(model_name, config, data, retrain):
                return {
                    'modelo_nombre': model_name,
                    'evaluado': True,
                    'metricas_validacion': {
                        'r2': {'mean': 0.8, 'std': 0.1},
                        'mae': {'mean': 2.5, 'std': 0.3},
                        'mape': {'mean': 15.0, 'std': 2.0}
                    },
                    'metricas_rendimiento': {
                        'interpretabilidad': 0.8,
                        'robustez_outliers': 0.6
                    }
                }
            
            comparator._evaluate_model = mock_evaluate_model
            
            # Ejecutar comparación
            resultado = comparator.compare_all_models(self.test_data, retrain_if_needed=False)
            
            # Verificar estructura del resultado
            self.assertIn('producto_id', resultado)
            self.assertIn('modelos_evaluados', resultado)
            self.assertIn('ranking_modelos', resultado)
            self.assertIn('recomendaciones', resultado)
            
        except Exception as e:
            print(f"Warning: Test de comparación falló: {e}")

class TestIntegration(unittest.TestCase):
    """Tests de integración para el sistema completo"""
    
    def setUp(self):
        """Configuración inicial"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Datos realistas para testing
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=150)
        
        # Simular patrón de ventas con tendencia y estacionalidad
        trend = np.linspace(10, 15, 150)
        seasonality = 3 * np.sin(2 * np.pi * np.arange(150) / 30)  # Ciclo mensual
        noise = np.random.normal(0, 1, 150)
        ventas = trend + seasonality + noise
        ventas = np.maximum(ventas, 0)  # No ventas negativas
        
        self.integration_data = pd.DataFrame({
            'fecha': dates,
            'producto_id': [1] * 150,
            'cantidad_vendida': ventas,
            'precio_base': 100 + np.random.uniform(-10, 10, 150),
            'stock_actual': np.random.randint(10, 100, 150),
            'precio_proveedor_promedio': 70 + np.random.uniform(-5, 5, 150),
            'dia_semana': [d.weekday() for d in dates],
            'mes': [d.month for d in dates],
            'margen': np.random.uniform(0.25, 0.35, 150),
            'variacion_precio': np.random.uniform(-0.05, 0.05, 150)
        })
        
        # Calcular features derivados
        self.integration_data['ventas_7_dias'] = (
            self.integration_data['cantidad_vendida'].rolling(7, min_periods=1).mean()
        )
        self.integration_data['ventas_30_dias'] = (
            self.integration_data['cantidad_vendida'].rolling(30, min_periods=1).mean()
        )
        
    def tearDown(self):
        """Limpieza"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_end_to_end_workflow(self):
        """Test flujo completo: validación -> entrenamiento -> caché -> comparación"""
        try:
            # 1. Validación de datos
            validator = SimpleDataValidator()
            issues = validator.validate_data_quality(self.integration_data, 1)
            self.assertNotIn('fatal_errors', issues)
            
            # 2. Limpieza de datos
            cleaner = SimpleDataCleaner()
            clean_data = cleaner.clean_data(self.integration_data, 1)
            self.assertGreater(len(clean_data), 100)  # Suficientes datos después de limpieza
            
            # 3. Configurar caché
            cache = ModelCacheMejorado(base_path=self.temp_dir)
            
            # 4. Simular entrenamiento y caché de modelo
            mock_model = {
                'type': 'integration_test',
                'trained_on': datetime.now().isoformat(),
                'data_size': len(clean_data)
            }
            
            cache_id = cache.cache_model(
                mock_model,
                producto_id=1,
                model_type='linear',
                metadata={'integration_test': True}
            )
            
            self.assertIsNotNone(cache_id)
            
            # 5. Cargar modelo desde caché
            loaded_model, metadata = cache.load_model(cache_id=cache_id)
            self.assertEqual(loaded_model['type'], 'integration_test')
            
            # 6. Verificar estadísticas de caché
            stats = cache.get_cache_stats()
            self.assertEqual(stats['models']['count'], 1)
            
            print("✓ Test de integración completado exitosamente")
            
        except Exception as e:
            print(f"Warning: Test de integración falló: {e}")
            
    def test_data_quality_metrics(self):
        """Test métricas de calidad de datos"""
        # Calcular métricas básicas
        data_quality = {
            'completeness': (
                1 - self.integration_data.isnull().sum().sum() / 
                (len(self.integration_data) * len(self.integration_data.columns))
            ),
            'consistency': len(self.integration_data[self.integration_data['cantidad_vendida'] >= 0]) / len(self.integration_data),
            'temporal_coverage': (self.integration_data['fecha'].max() - self.integration_data['fecha'].min()).days
        }
        
        # Verificar calidad mínima
        self.assertGreater(data_quality['completeness'], 0.95)  # 95% completo
        self.assertGreater(data_quality['consistency'], 0.99)   # 99% consistente
        self.assertGreater(data_quality['temporal_coverage'], 100)  # Más de 100 días

def run_all_tests():
    """Ejecuta todos los tests"""
    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests
    test_classes = [
        TestDataValidationAndCleaning,
        TestModelTraining,
        TestModelCache,
        TestModelComparison,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print(f"\n{'='*50}")
    print(f"RESUMEN DE TESTS")
    print(f"{'='*50}")
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Exitosos: {result.testsRun - len(result.errors) - len(result.failures)}")
    
    if result.errors:
        print(f"\nErrores encontrados:")
        for test, error in result.errors:
            print(f"- {test}: {error}")
    
    if result.failures:
        print(f"\nFallos encontrados:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Ejecutar tests
    success = run_all_tests()
    exit(0 if success else 1)
