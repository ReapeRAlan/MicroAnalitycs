import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# URL base de la API
API_URL = "http://localhost:8000/api/inventory"

# Función para obtener la lista de inventario
def fetch_inventory(skip=0, limit=1000, min_stock=None):
    params = {"skip": skip, "limit": limit}
    if min_stock is not None:
        params["min_stock"] = min_stock
    try:
        response = requests.get(f"{API_URL}/", params=params)
        response.raise_for_status()
        return response.json()  # Devuelve la lista de diccionarios directamente
    except requests.exceptions.RequestException as e:
        st.error(f"Error al recuperar el inventario: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return []

# Función para crear un nuevo registro de inventario
def create_inventory(product_id, stock_actual):
    payload = {"product_id": product_id, "stock_actual": stock_actual}
    try:
        response = requests.post(f"{API_URL}/new", json=payload)
        response.raise_for_status()
        st.success("Registro de inventario creado correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al crear inventario: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

# Función para actualizar un registro de inventario
def update_inventory(inventory_id, stock_actual):
    payload = {"stock_actual": stock_actual}
    try:
        response = requests.put(f"{API_URL}/update/{inventory_id}", json=payload)
        response.raise_for_status()
        st.success("Registro de inventario actualizado correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al actualizar el inventario: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

# Función para eliminar un registro de inventario
def delete_inventory(inventory_id):
    try:
        response = requests.delete(f"{API_URL}/delete/{inventory_id}")
        response.raise_for_status()
        st.success("Registro de inventario eliminado correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al borrar el inventario: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

def show_inventory():
    st.title("📦 Gestión de Inventario")
    st.markdown("Administración de inventario para el negocio seleccionado")

    # Pestañas para CRUD
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Listar", "🛒 Crear", "✏️ Actualizar", "🗑️ Eliminar"])

    with tab1:
        st.header("Listar Inventario")
        col1, col2 = st.columns(2)
        with col1:
            min_stock = st.number_input("Stock mínimo", min_value=0, value=0, step=1)
        with col2:
            limit = st.number_input("Límite por página", min_value=1, value=10, step=1)
        inventory_data = fetch_inventory(skip=0, limit=limit, min_stock=min_stock if min_stock > 0 else None)
        if inventory_data:
            # Procesar los datos para extraer solo el nombre del producto
            processed_data = []
            for item in inventory_data:
                item_copy = item.copy()  # Crear una copia para no modificar el original
                if "producto" in item_copy and item_copy["producto"] is not None:
                    item_copy["producto"] = item_copy["producto"].get("nombre", "Sin nombre")  # Extraer solo el nombre
                else:
                    item_copy["producto"] = "Sin nombre"  # Si no hay producto, usar un valor por defecto
                processed_data.append(item_copy)
            
            df = pd.DataFrame(processed_data)
            df["ultimo_ingreso"] = pd.to_datetime(df["ultimo_ingreso"]).dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.warning("No hay inventario disponible.")

    with tab2:
        st.header("Crear Inventario de Producto")
        with st.form("form_create_inventory"):
            product_id = st.number_input("ID del Producto", min_value=1, step=1)
            stock_actual = st.number_input("Stock Actual", min_value=0, step=1)
            if st.form_submit_button("Crear"):
                if create_inventory(product_id, stock_actual):
                    st.rerun()

    with tab3:
        st.header("Actualizar Inventario de Producto")
        inventory_data = fetch_inventory()
        if inventory_data:
            inventory_id = st.selectbox("Seleccionar ID del Producto", [i["id"] for i in inventory_data])
            selected_inventory = next((i for i in inventory_data if i["id"] == inventory_id), None)
            if selected_inventory:
                with st.form("form_update_inventory"):
                    stock_actual = st.number_input("Nuevo Stock Actual", min_value=0, value=selected_inventory["stock_actual"], step=1)
                    if st.form_submit_button("Actualizar"):
                        if update_inventory(inventory_id, stock_actual):
                            st.rerun()
            else:
                st.info("Selecciona un inventario para editar.")
        else:
            st.warning("No hay un inventario disponible para actualizar.")

    with tab4:
        st.header("Eliminar Inventario")
        inventory_data = fetch_inventory()
        if inventory_data:
            with st.form("form_delete_inventory"):
                inventory_id = st.selectbox("Seleccionar ID del Producto para Eliminar", [i["id"] for i in inventory_data])
                st.warning("Esta acción no se puede deshacer.")
                if st.form_submit_button("Eliminar"):
                    if delete_inventory(inventory_id):
                        st.rerun()
        else:
            st.warning("No hay inventario disponible para eliminar.")

if __name__ == "__main__":
    show_inventory()