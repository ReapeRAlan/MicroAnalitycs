import requests
import random
from datetime import datetime, timedelta
import streamlit as st

# URL base de la API
API_BASE_URL = "http://localhost:8000/api"

def get_products(skip=0, limit=1000, force_refresh=False):
    try:
        timestamp = datetime.now().timestamp()
        response = requests.get(f"{API_BASE_URL}/products/?skip={skip}&limit={limit}&t={timestamp}")
        response.raise_for_status()
        products = response.json()
        if "business_id" in globals() and globals()["business_id"]:
            filtered_products = [p for p in products if p.get("business_id") == globals()["business_id"]]
            return filtered_products
        return products
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener productos: {str(e)}")
        return []

def get_categories():
    try:
        response = requests.get(f"{API_BASE_URL}/categories/")
        response.raise_for_status()
        return {cat["id"]: cat["nombre"] for cat in response.json()}
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener categorías: {str(e)}")
        return []

def generar_ventas_simuladas(cantidad=10, business_id="Negocio001"):
    """Genera ventas simuladas basadas en productos disponibles."""
    ventas = []
    start_date = datetime(2025, 8, 1)
    productos = get_products()
    if not productos:
        productos = [
            {"id": 1, "nombre": "Camiseta Básica", "precio_base": 15.99, "business_id": business_id, "stock_actual": random.randint(1, 10)},
            {"id": 2, "nombre": "Smartphone X10", "precio_base": 299.99, "business_id": business_id, "stock_actual": random.randint(1, 10)},
            {"id": 3, "nombre": "Zapatillas Deportivas", "precio_base": 49.99, "business_id": business_id, "stock_actual": random.randint(1, 10)},
            {"id": 4, "nombre": "Auriculares Bluetooth", "precio_base": 29.99, "business_id": business_id, "stock_actual": random.randint(1, 10)},
        ]
    productos_con_stock = [p for p in productos if p.get("stock_actual", 0) > 0]
    if not productos_con_stock:
        productos = [
            {"id": 1, "nombre": "Camiseta Básica", "precio_base": 15.99, "stock_actual": 5, "business_id": business_id},
            {"id": 2, "nombre": "Smartphone X10", "precio_base": 299.99, "stock_actual": 5, "business_id": business_id},
        ]
        productos_con_stock = productos
    for _ in range(min(cantidad, len(productos_con_stock))):
        producto = random.choice(productos_con_stock)
        max_vendible = min(5, producto.get("stock_actual", 0))
        if max_vendible > 0:
            cantidad_vendida = random.randint(1, max_vendible)
            fecha = start_date + timedelta(days=random.randint(0, 6), hours=random.randint(0, 23))
            precio = producto.get("precio_base", 0.0)
            total = cantidad_vendida * precio
            ventas.append({
                "Producto": producto["nombre"],
                "Cantidad": cantidad_vendida,
                "Precio Unitario": f"${precio:.2f}",
                "Total": f"${total:.2f}",
                "Fecha": fecha.strftime("%Y-%m-%d %H:%M")
            })
    return ventas

# No inicializamos ventas_simuladas aquí, lo haremos en main.py