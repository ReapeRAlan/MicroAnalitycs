"""
Generador de datasets de prueba usando Faker para testing de modelos de regresión
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from pathlib import Path

try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    print("Warning: Faker no está disponible. Instalando...")

class DatasetGenerator:
    """Generador de datasets sintéticos para testing"""
    
    def __init__(self, locale: str = 'es_ES'):
        if FAKER_AVAILABLE:
            self.fake = Faker(locale)
        else:
            self.fake = None
            print("Faker no disponible - usando generación básica")
        
        self.output_dir = Path("tests/datasets")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_products_dataset(self, num_products: int = 100) -> pd.DataFrame:
        """Genera dataset de productos"""
        print(f"Generando dataset de {num_products} productos...")
        
        products = []
        categories = ['Electrónicos', 'Ropa', 'Hogar', 'Deportes', 'Libros', 'Alimentación']
        
        for i in range(num_products):
            if self.fake:
                product = {
                    'producto_id': i + 1,
                    'nombre': self.fake.catch_phrase(),
                    'categoria': self.fake.random_element(categories),
                    'precio_base': float(self.fake.pydecimal(left_digits=3, right_digits=2, positive=True)),
                    'costo_proveedor': 0,  # Se calculará después
                    'marca': self.fake.company(),
                    'descripcion': self.fake.text(max_nb_chars=200),
                    'peso_kg': round(self.fake.pyfloat(left_digits=1, right_digits=2, positive=True), 2),
                    'dimensiones': f"{self.fake.random_int(10, 100)}x{self.fake.random_int(10, 100)}x{self.fake.random_int(5, 50)}",
                    'fecha_lanzamiento': self.fake.date_between(start_date='-2y', end_date='today'),
                    'activo': self.fake.boolean(chance_of_getting_true=90)
                }
            else:
                # Generación básica sin Faker
                product = {
                    'producto_id': i + 1,
                    'nombre': f"Producto {i+1}",
                    'categoria': np.random.choice(categories),
                    'precio_base': round(np.random.uniform(10, 1000), 2),
                    'costo_proveedor': 0,
                    'marca': f"Marca {np.random.randint(1, 20)}",
                    'descripcion': f"Descripción del producto {i+1}",
                    'peso_kg': round(np.random.uniform(0.1, 10), 2),
                    'dimensiones': f"{np.random.randint(10, 100)}x{np.random.randint(10, 100)}x{np.random.randint(5, 50)}",
                    'fecha_lanzamiento': (datetime.now() - timedelta(days=np.random.randint(0, 730))).date(),
                    'activo': np.random.choice([True, False], p=[0.9, 0.1])
                }
            
            # Calcular costo como 60-80% del precio
            product['costo_proveedor'] = round(product['precio_base'] * np.random.uniform(0.6, 0.8), 2)
            product['margen'] = round((product['precio_base'] - product['costo_proveedor']) / product['precio_base'], 3)
            
            products.append(product)
        
        df = pd.DataFrame(products)
        filepath = self.output_dir / 'productos_sinteticos.csv'
        df.to_csv(filepath, index=False)
        print(f"Dataset de productos guardado en: {filepath}")
        
        return df
    
    def generate_sales_time_series(self, producto_ids: List[int], days: int = 365) -> pd.DataFrame:
        """Genera series temporales de ventas realistas"""
        print(f"Generando series temporales de {days} días para {len(producto_ids)} productos...")
        
        all_sales = []
        base_date = datetime.now() - timedelta(days=days)
        
        for producto_id in producto_ids:
            # Parámetros únicos por producto
            base_demand = np.random.uniform(5, 50)  # Demanda base diaria
            seasonality_strength = np.random.uniform(0.1, 0.5)  # Fuerza de estacionalidad
            trend_slope = np.random.uniform(-0.01, 0.02)  # Tendencia (puede ser negativa)
            noise_level = np.random.uniform(0.1, 0.3)  # Nivel de ruido
            
            for day in range(days):
                date = base_date + timedelta(days=day)
                
                # Componentes de la serie temporal
                trend = base_demand + (trend_slope * day)
                
                # Estacionalidad (anual y semanal)
                annual_season = seasonality_strength * np.sin(2 * np.pi * day / 365.25)
                weekly_season = seasonality_strength * 0.5 * np.sin(2 * np.pi * day / 7)
                
                # Efectos especiales
                weekend_effect = -0.3 if date.weekday() >= 5 else 0  # Menos ventas en fin de semana
                month_end_effect = 0.2 if date.day >= 28 else 0  # Más ventas al final del mes
                holiday_effect = 0.5 if date.month == 12 and date.day >= 20 else 0  # Efecto navideño
                
                # Ruido aleatorio
                noise = np.random.normal(0, noise_level * base_demand)
                
                # Calcular demanda final
                demand = trend + annual_season + weekly_season + weekend_effect + month_end_effect + holiday_effect + noise
                demand = max(0, int(round(demand)))  # No puede ser negativa
                
                # Datos adicionales
                precio_base = 100 + np.random.normal(0, 5)  # Precio con pequeña variación
                stock_actual = max(20, 100 - (day % 30) + np.random.randint(-10, 10))
                precio_proveedor = precio_base * np.random.uniform(0.6, 0.8)
                
                sale_record = {
                    'fecha': date.strftime('%Y-%m-%d'),
                    'producto_id': producto_id,
                    'cantidad_vendida': demand,
                    'dia_semana': date.weekday(),
                    'mes': date.month,
                    'dia_mes': date.day,
                    'trimestre': (date.month - 1) // 3 + 1,
                    'es_fin_semana': date.weekday() >= 5,
                    'es_feriado': self._is_holiday(date),
                    'precio_base': round(precio_base, 2),
                    'stock_actual': stock_actual,
                    'precio_proveedor_promedio': round(precio_proveedor, 2),
                    'margen': round((precio_base - precio_proveedor) / precio_base, 3),
                    'variacion_precio': round(np.random.uniform(-0.05, 0.05), 4)
                }
                
                all_sales.append(sale_record)
        
        # Crear DataFrame y calcular features históricos
        df = pd.DataFrame(all_sales)
        df = self._add_historical_features(df)
        
        filepath = self.output_dir / 'ventas_tiempo_series.csv'
        df.to_csv(filepath, index=False)
        print(f"Dataset de ventas guardado en: {filepath}")
        
        return df
    
    def _is_holiday(self, date: datetime) -> bool:
        """Determina si una fecha es feriado (simplificado)"""
        # Feriados fijos chilenos (simplificado)
        holidays = [
            (1, 1),   # Año Nuevo
            (5, 1),   # Día del Trabajo
            (9, 18),  # Fiestas Patrias
            (9, 19),  # Día del Ejército
            (12, 25), # Navidad
        ]
        
        return (date.month, date.day) in holidays
    
    def _add_historical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Agrega features históricos calculados"""
        print("Calculando features históricos...")
        
        df = df.sort_values(['producto_id', 'fecha']).reset_index(drop=True)
        
        # Calcular ventanas móviles por producto
        for producto_id in df['producto_id'].unique():
            mask = df['producto_id'] == producto_id
            producto_data = df[mask].copy()
            
            # Ventas acumuladas en ventanas
            producto_data['ventas_7_dias'] = producto_data['cantidad_vendida'].rolling(window=7, min_periods=1).sum()
            producto_data['ventas_30_dias'] = producto_data['cantidad_vendida'].rolling(window=30, min_periods=1).sum()
            
            # Promedios móviles
            producto_data['promedio_ventas_7_dias'] = producto_data['cantidad_vendida'].rolling(window=7, min_periods=1).mean()
            producto_data['promedio_ventas_30_dias'] = producto_data['cantidad_vendida'].rolling(window=30, min_periods=1).mean()
            
            # Tendencia y volatilidad
            producto_data['tendencia_ventas'] = producto_data['cantidad_vendida'].rolling(window=14, min_periods=7).apply(
                lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) >= 7 else 0
            )
            producto_data['volatilidad_ventas'] = producto_data['cantidad_vendida'].rolling(window=14, min_periods=1).std()
            
            # Frecuencia de compra (días entre compras > 0)
            compras = producto_data[producto_data['cantidad_vendida'] > 0].index
            if len(compras) > 1:
                gaps = np.diff(compras)
                producto_data['frecuencia_compra'] = 1 / (np.mean(gaps) + 1) if len(gaps) > 0 else 0
            else:
                producto_data['frecuencia_compra'] = 0
            
            # Actualizar el DataFrame principal
            df.loc[mask, producto_data.columns] = producto_data
        
        # Rellenar NaNs
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(0)
        
        return df
    
    def generate_supplier_data(self, num_suppliers: int = 50) -> pd.DataFrame:
        """Genera dataset de proveedores"""
        print(f"Generando dataset de {num_suppliers} proveedores...")
        
        suppliers = []
        countries = ['Chile', 'Perú', 'Argentina', 'Brasil', 'Colombia', 'China', 'EEUU']
        
        for i in range(num_suppliers):
            if self.fake:
                supplier = {
                    'proveedor_id': i + 1,
                    'nombre': self.fake.company(),
                    'pais': self.fake.random_element(countries),
                    'ciudad': self.fake.city(),
                    'contacto_email': self.fake.company_email(),
                    'telefono': self.fake.phone_number(),
                    'calificacion': round(self.fake.pyfloat(min_value=3.0, max_value=5.0), 1),
                    'tiempo_entrega_dias': self.fake.random_int(1, 30),
                    'descuento_volumen': round(self.fake.pyfloat(min_value=0, max_value=0.15), 3),
                    'moneda': self.fake.random_element(['CLP', 'USD', 'EUR']),
                    'activo': self.fake.boolean(chance_of_getting_true=85)
                }
            else:
                supplier = {
                    'proveedor_id': i + 1,
                    'nombre': f"Proveedor {i+1}",
                    'pais': np.random.choice(countries),
                    'ciudad': f"Ciudad {i+1}",
                    'contacto_email': f"contacto{i+1}@proveedor.com",
                    'telefono': f"+56 9 {np.random.randint(10000000, 99999999)}",
                    'calificacion': round(np.random.uniform(3.0, 5.0), 1),
                    'tiempo_entrega_dias': np.random.randint(1, 30),
                    'descuento_volumen': round(np.random.uniform(0, 0.15), 3),
                    'moneda': np.random.choice(['CLP', 'USD', 'EUR']),
                    'activo': np.random.choice([True, False], p=[0.85, 0.15])
                }
            
            suppliers.append(supplier)
        
        df = pd.DataFrame(suppliers)
        filepath = self.output_dir / 'proveedores_sinteticos.csv'
        df.to_csv(filepath, index=False)
        print(f"Dataset de proveedores guardado en: {filepath}")
        
        return df
    
    def generate_complete_dataset(self, num_products: int = 50, days: int = 365) -> Dict[str, pd.DataFrame]:
        """Genera un dataset completo para testing"""
        print("="*60)
        print("GENERANDO DATASET COMPLETO PARA TESTING")
        print("="*60)
        
        datasets = {}
        
        # 1. Productos
        products_df = self.generate_products_dataset(num_products)
        datasets['productos'] = products_df
        
        # 2. Proveedores
        suppliers_df = self.generate_supplier_data()
        datasets['proveedores'] = suppliers_df
        
        # 3. Series temporales de ventas
        product_ids = products_df['producto_id'].tolist()[:num_products]  # Usar solo algunos productos
        sales_df = self.generate_sales_time_series(product_ids, days)
        datasets['ventas'] = sales_df
        
        # 4. Precios de proveedores
        supplier_prices = []
        for product_id in product_ids:
            for supplier_id in suppliers_df['proveedor_id'].sample(n=min(5, len(suppliers_df))):
                base_price = products_df[products_df['producto_id'] == product_id]['costo_proveedor'].iloc[0]
                price_variation = np.random.uniform(0.9, 1.1)
                
                supplier_price = {
                    'producto_id': product_id,
                    'proveedor_id': supplier_id,
                    'precio': round(base_price * price_variation, 2),
                    'moneda': 'CLP',
                    'fecha_cotizacion': (datetime.now() - timedelta(days=np.random.randint(0, 30))).date(),
                    'cantidad_minima': np.random.randint(1, 100),
                    'tiempo_entrega': np.random.randint(5, 30),
                    'activo': True
                }
                supplier_prices.append(supplier_price)
        
        supplier_prices_df = pd.DataFrame(supplier_prices)
        datasets['precios_proveedores'] = supplier_prices_df
        
        # Guardar todos los datasets
        filepath = self.output_dir / 'dataset_completo.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            # Convertir DataFrames a dict para JSON
            json_data = {name: df.to_dict('records') for name, df in datasets.items()}
            json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\nDataset completo guardado en: {filepath}")
        print(f"Total de productos: {len(datasets['productos'])}")
        print(f"Total de proveedores: {len(datasets['proveedores'])}")
        print(f"Total de registros de ventas: {len(datasets['ventas'])}")
        print(f"Total de precios de proveedores: {len(datasets['precios_proveedores'])}")
        
        return datasets

def main():
    """Función principal para generar datasets de prueba"""
    try:
        # Instalar Faker si no está disponible
        if not FAKER_AVAILABLE:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "pip", "install", "faker"])
            print("Faker instalado. Reinicia el script.")
            return
        
        generator = DatasetGenerator()
        
        # Generar dataset completo
        datasets = generator.generate_complete_dataset(num_products=30, days=180)
        
        print("\n✓ Generación de datasets completada exitosamente")
        
        # Mostrar estadísticas
        for name, df in datasets.items():
            print(f"\nDataset '{name}':")
            print(f"  Registros: {len(df)}")
            print(f"  Columnas: {len(df.columns)}")
            if 'cantidad_vendida' in df.columns:
                print(f"  Ventas promedio: {df['cantidad_vendida'].mean():.2f}")
            if 'precio_base' in df.columns:
                print(f"  Precio promedio: ${df['precio_base'].mean():.2f}")
        
    except Exception as e:
        print(f"Error generando datasets: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
