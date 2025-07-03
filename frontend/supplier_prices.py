import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# URL base de la API
API_URL = "http://localhost:8000/api/supplier-prices"

# Función para obtener la lista de precios de proveedores
def fetch_supplier_prices(skip=0, limit=100, product_id=None, supplier_id=None):
    try:
        params = {"skip": skip, "limit": limit}
        if product_id:
            params["product_id"] = product_id
        if supplier_id:
            params["supplier_id"] = supplier_id
        response = requests.get(f"{API_URL}/", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al recuperar precios: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return []

# Función para obtener un precio por ID
def fetch_supplier_price(price_id):
    try:
        response = requests.get(f"{API_URL}/{price_id}/details")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al recuperar precio: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return None

# Función para crear un nuevo precio
def create_supplier_price(product_id, supplier_id, precio):
    try:
        response = requests.post(f"{API_URL}/", json={"product_id": product_id, "supplier_id": supplier_id, "precio": precio})
        response.raise_for_status()
        st.success("Precio creado correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al crear precio: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

# Función para actualizar un precio
def update_supplier_price(price_id, precio):
    try:
        response = requests.put(f"{API_URL}/{price_id}", json={"precio": precio})
        response.raise_for_status()
        st.success("Precio actualizado correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al actualizar precio: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

# Función para eliminar un precio
def delete_supplier_price(price_id):
    try:
        response = requests.delete(f"{API_URL}/{price_id}")
        response.raise_for_status()
        st.success("Precio eliminado correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al eliminar precio: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

def show_supplier_prices():
    st.title("💰 Precios de los Proveedores")
    st.markdown("Gestión de precios de proveedores para productos")

    # Pestañas para CRUD
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Listar", "🛒 Crear", "✏️ Actualizar", "🗑️ Eliminar"])

    with tab1:
        st.header("Listar Precios")
        col1, col2, col3 = st.columns(3)
        with col1:
            skip = st.number_input("Páginado (skip)", min_value=0, value=0, step=10)
        with col2:
            limit = st.number_input("Límite por página", min_value=1, value=10, step=1)
        with col3:
            product_id = st.number_input("Filtrar por ID de Producto", min_value=0, value=0, step=1)
        supplier_id = st.number_input("Filtrar por ID de Proveedor", min_value=0, value=0, step=1)
        prices_data = fetch_supplier_prices(skip=skip, limit=limit, product_id=product_id if product_id > 0 else None, supplier_id=supplier_id if supplier_id > 0 else None)
        if prices_data:
            df = pd.DataFrame(prices_data)
            df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%Y-%m-%d %H:%M:%S")
            # Nota: Las relaciones producto y proveedor no están disponibles en /supplier-prices/. 
            # Para mostrar nombres, necesitarías iterar sobre cada precio con /details o ajustar la API.
            st.dataframe(df[["id", "product_id", "supplier_id", "precio", "fecha"]], hide_index=True, use_container_width=True)
        else:
            st.warning("No hay precios disponibles.")

    with tab2:
        st.header("Crear Precio")
        with st.form("form_create_price"):
            product_id = st.number_input("ID de Producto", min_value=1, step=1)
            supplier_id = st.number_input("ID de Proveedor", min_value=1, step=1)
            precio = st.number_input("Precio", min_value=0.0, step=0.01)
            if st.form_submit_button("Crear"):
                if product_id and supplier_id and precio >= 0:
                    if create_supplier_price(product_id, supplier_id, precio):
                        st.rerun()
                else:
                    st.error("Por favor, completa todos los campos correctamente.")

    with tab3:
        st.header("Actualizar Precio")
        prices_data = fetch_supplier_prices()
        if prices_data:
            price_id = st.selectbox("Seleccionar Precio", [p["id"] for p in prices_data])
            selected_price = fetch_supplier_price(price_id)
            if selected_price:
                with st.form("form_update_price"):
                    precio = st.number_input("Nuevo Precio", min_value=0.0, step=0.01, value=selected_price["precio"])
                    if st.form_submit_button("Actualizar"):
                        if precio >= 0:
                            if update_supplier_price(price_id, precio):
                                st.rerun()
                        else:
                            st.error("El precio debe ser un valor positivo.")
            else:
                st.info("Selecciona un precio para editar.")
        else:
            st.warning("No hay precios disponibles para actualizar.")

    with tab4:
        st.header("Eliminar Precio")
        prices_data = fetch_supplier_prices()
        if prices_data:
            with st.form("form_delete_price"):
                price_id = st.selectbox("Seleccionar Precio para Eliminar", [p["id"] for p in prices_data])
                st.warning("Esta acción no se puede deshacer.")
                if st.form_submit_button("Eliminar"):
                    if delete_supplier_price(price_id):
                        st.rerun()
        else:
            st.warning("No hay precios disponibles para eliminar.")

if __name__ == "__main__":
    show_supplier_prices()