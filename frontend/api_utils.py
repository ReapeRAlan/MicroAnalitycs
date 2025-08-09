import requests
from datetime import datetime

# URL base de la API
API_BASE_URL = "http://localhost:8000/api"

def get_products(skip=0, limit=1000, force_refresh=False):
    try:
        timestamp = datetime.now().timestamp()
        response = requests.get(f"{API_BASE_URL}/products/?skip={skip}&limit={limit}&t={timestamp}")
        response.raise_for_status()
        products = response.json()
        if "business_id" in globals() and globals()["business_id"]:  # Usar variable global si existe
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
        return {}