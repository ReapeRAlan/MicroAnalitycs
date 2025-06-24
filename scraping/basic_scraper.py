"""
Módulo básico de scraping para obtener datos de precios y productos
"""
import requests
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
import json
from pathlib import Path

class BasicScraper:
    """Scraper básico para datos de productos y precios"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache_dir = Path("scraping/cache")
        self.cache_dir.mkdir(exist_ok=True)
    
    def scrape_product_prices(self, product_name: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Simula scraping de precios de productos.
        En una implementación real, esto haría requests a sitios web reales.
        """
        print(f"Simulando scraping para: {product_name}")
        
        # Simular datos de diferentes tiendas
        stores = ['Amazon', 'MercadoLibre', 'Falabella', 'Ripley', 'Sodimac']
        results = []
        
        base_price = np.random.uniform(50, 500)
        
        for i, store in enumerate(stores[:max_results]):
            # Simular variación de precios entre tiendas
            price_variation = np.random.uniform(0.8, 1.2)
            price = base_price * price_variation
            
            result = {
                'store': store,
                'product_name': product_name,
                'price': round(price, 2),
                'currency': 'CLP',
                'availability': np.random.choice(['En stock', 'Pocas unidades', 'Agotado'], p=[0.7, 0.2, 0.1]),
                'rating': round(np.random.uniform(3.5, 5.0), 1),
                'reviews_count': np.random.randint(10, 1000),
                'url': f"https://{store.lower()}.com/product/{i}",
                'scraped_at': datetime.now().isoformat(),
                'shipping_cost': round(np.random.uniform(0, 15), 2) if np.random.random() > 0.3 else 0
            }
            results.append(result)
            
            # Simular delay entre requests
            time.sleep(0.1)
        
        return results
    
    def get_market_trends(self, category: str) -> Dict[str, Any]:
        """
        Simula obtención de tendencias de mercado.
        """
        print(f"Obteniendo tendencias para categoría: {category}")
        
        # Simular datos de tendencias
        trends = {
            'category': category,
            'trend_direction': np.random.choice(['up', 'down', 'stable'], p=[0.4, 0.3, 0.3]),
            'price_change_percentage': round(np.random.uniform(-20, 20), 2),
            'demand_level': np.random.choice(['low', 'medium', 'high'], p=[0.2, 0.5, 0.3]),
            'seasonal_factor': round(np.random.uniform(0.8, 1.3), 2),
            'market_saturation': round(np.random.uniform(0.3, 0.9), 2),
            'competitor_count': np.random.randint(5, 50),
            'data_date': datetime.now().isoformat(),
            'confidence_score': round(np.random.uniform(0.6, 0.95), 2)
        }
        
        return trends
    
    def scrape_competitor_data(self, product_keywords: List[str]) -> pd.DataFrame:
        """
        Simula scraping de datos de competidores.
        """
        print(f"Scrapeando datos de competidores para: {product_keywords}")
        
        data = []
        for keyword in product_keywords:
            # Generar múltiples productos por keyword
            for i in range(np.random.randint(3, 8)):
                competitor_data = {
                    'keyword': keyword,
                    'competitor_name': f"Competidor_{i+1}",
                    'product_name': f"{keyword} - Modelo {i+1}",
                    'price': round(np.random.uniform(100, 1000), 2),
                    'stock_level': np.random.choice(['Alto', 'Medio', 'Bajo']),
                    'sales_rank': np.random.randint(1, 1000),
                    'launch_date': (datetime.now() - timedelta(days=np.random.randint(30, 365))).date(),
                    'features_count': np.random.randint(3, 15),
                    'brand_reputation': round(np.random.uniform(3.0, 5.0), 1),
                    'market_share': round(np.random.uniform(0.01, 0.15), 3),
                    'promotion_active': np.random.choice([True, False], p=[0.3, 0.7]),
                    'scraped_at': datetime.now()
                }
                data.append(competitor_data)
        
        return pd.DataFrame(data)
    
    def save_scraped_data(self, data: Any, filename: str):
        """Guarda datos scrapeados en caché"""
        filepath = self.cache_dir / f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if isinstance(data, pd.DataFrame):
            data.to_json(filepath, orient='records', date_format='iso')
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"Datos guardados en: {filepath}")
    
    def load_cached_data(self, filename_pattern: str) -> Optional[Any]:
        """Carga datos desde caché"""
        cache_files = list(self.cache_dir.glob(f"{filename_pattern}*.json"))
        
        if not cache_files:
            return None
        
        # Cargar el archivo más reciente
        latest_file = max(cache_files, key=lambda f: f.stat().st_mtime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error cargando caché: {e}")
            return None

class PriceMonitor:
    """Monitor de precios para seguimiento continuo"""
    
    def __init__(self):
        self.scraper = BasicScraper()
        self.monitored_products = []
    
    def add_product_to_monitor(self, product_name: str, target_price: float):
        """Agrega un producto al monitoreo"""
        product = {
            'name': product_name,
            'target_price': target_price,
            'added_at': datetime.now(),
            'last_check': None,
            'price_history': []
        }
        self.monitored_products.append(product)
        print(f"Producto agregado al monitoreo: {product_name} (precio objetivo: ${target_price})")
    
    def check_prices(self) -> List[Dict[str, Any]]:
        """Verifica precios de productos monitoreados"""
        alerts = []
        
        for product in self.monitored_products:
            print(f"Verificando precios para: {product['name']}")
            
            # Scrape actual prices
            current_prices = self.scraper.scrape_product_prices(product['name'])
            
            if current_prices:
                min_price = min(item['price'] for item in current_prices)
                
                # Actualizar historial
                product['price_history'].append({
                    'date': datetime.now(),
                    'min_price': min_price,
                    'prices': current_prices
                })
                product['last_check'] = datetime.now()
                
                # Verificar si alcanzó precio objetivo
                if min_price <= product['target_price']:
                    alert = {
                        'product': product['name'],
                        'current_price': min_price,
                        'target_price': product['target_price'],
                        'savings': product['target_price'] - min_price,
                        'best_store': min(current_prices, key=lambda x: x['price'])['store'],
                        'alert_type': 'price_target_reached'
                    }
                    alerts.append(alert)
        
        return alerts
    
    def get_price_trends(self, product_name: str) -> Dict[str, Any]:
        """Obtiene tendencias de precio para un producto"""
        product = next((p for p in self.monitored_products if p['name'] == product_name), None)
        
        if not product or not product['price_history']:
            return {'error': 'Producto no encontrado o sin historial'}
        
        history = product['price_history']
        prices = [entry['min_price'] for entry in history]
        
        return {
            'product': product_name,
            'current_price': prices[-1] if prices else None,
            'average_price': np.mean(prices) if prices else None,
            'min_price': min(prices) if prices else None,
            'max_price': max(prices) if prices else None,
            'price_trend': 'increasing' if len(prices) > 1 and prices[-1] > prices[0] else 'decreasing',
            'volatility': np.std(prices) if len(prices) > 1 else 0,
            'data_points': len(prices)
        }

def demo_scraping():
    """Función demo del scraping"""
    print("="*50)
    print("DEMO DE SCRAPING")
    print("="*50)
    
    # Demo básico
    scraper = BasicScraper()
    
    # Scraping de precios
    print("\n1. Scraping de precios:")
    prices = scraper.scrape_product_prices("Laptop Gaming", max_results=5)
    for price in prices:
        print(f"  {price['store']}: ${price['price']} ({price['availability']})")
    
    # Tendencias de mercado
    print("\n2. Tendencias de mercado:")
    trends = scraper.get_market_trends("Electrónicos")
    print(f"  Tendencia: {trends['trend_direction']}")
    print(f"  Cambio de precio: {trends['price_change_percentage']}%")
    print(f"  Nivel de demanda: {trends['demand_level']}")
    
    # Datos de competidores
    print("\n3. Datos de competidores:")
    competitor_data = scraper.scrape_competitor_data(["smartphone", "tablet"])
    print(f"  {len(competitor_data)} productos de competidores encontrados")
    print(f"  Rango de precios: ${competitor_data['price'].min()} - ${competitor_data['price'].max()}")
    
    # Monitor de precios
    print("\n4. Monitor de precios:")
    monitor = PriceMonitor()
    monitor.add_product_to_monitor("iPhone 15", 800.0)
    monitor.add_product_to_monitor("Samsung Galaxy S24", 700.0)
    
    alerts = monitor.check_prices()
    if alerts:
        print(f"  {len(alerts)} alertas generadas")
        for alert in alerts:
            print(f"    {alert['product']}: ${alert['current_price']} (ahorro: ${alert['savings']})")
    else:
        print("  No hay alertas de precio")
    
    print("\n✓ Demo de scraping completado")

if __name__ == "__main__":
    demo_scraping()
