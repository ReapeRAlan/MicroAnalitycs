import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# URL base de la API
API_URL = "http://localhost:8000/api/categories"

# Función para obtener la lista de categorías
def fetch_categories(skip=0, limit=1000):
    try:
        response = requests.get(f"{API_URL}/", params={"skip": skip, "limit": limit})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al recuperar categorías: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return []

# Función para obtener una categoría por ID
def fetch_category(category_id):
    try:
        response = requests.get(f"{API_URL}/{category_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al recuperar categoría: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return None

# Función para crear una nueva categoría
def create_category(category_data):
    try:
        response = requests.post(f"{API_URL}/new", json=category_data)
        response.raise_for_status()
        st.success("Categoría creada correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al crear categoría: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

# Función para actualizar una categoría
def update_category(category_id, category_data):
    try:
        response = requests.put(f"{API_URL}/update/{category_id}", json=category_data)
        response.raise_for_status()
        st.success("Categoría actualizada correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al actualizar categoría: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

# Función para eliminar una categoría
def delete_category(category_id):
    try:
        response = requests.delete(f"{API_URL}/delete/{category_id}")
        response.raise_for_status()
        st.success("Categoría eliminada correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al eliminar categoría: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

def show_categories():
    st.title("📂 Gestión de Categorías")
    st.markdown("Administración de categorías para el negocio seleccionado")

    # Pestañas para CRUD
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Listar", "🛒 Crear", "✏️ Actualizar", "🗑️ Eliminar"])

    with tab1:
        st.header("Listar Categorías")
        col1, col2 = st.columns(2)
        with col1:
            skip = st.number_input("Páginado (skip)", min_value=0, value=0, step=10)
        with col2:
            limit = st.number_input("Límite por página", min_value=1, value=10, step=1)
        categories_data = fetch_categories(skip=skip, limit=limit)
        if categories_data:
            df = pd.DataFrame(categories_data)
            df["fecha_registro"] = pd.to_datetime(df["fecha_registro"]).dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.warning("No hay categorías disponibles.")

    with tab2:
        st.header("Crear Categoría")
        with st.form("form_create_category"):
            nombre = st.text_input("Nombre", max_chars=100)
            descripcion = st.text_area("Descripción", height=100)
            if st.form_submit_button("Crear"):
                if nombre:
                    category_data = {"nombre": nombre, "descripcion": descripcion if descripcion else None}
                    if create_category(category_data):
                        st.rerun()
                else:
                    st.error("El nombre es obligatorio.")

    with tab3:
        st.header("Actualizar Categoría")
        categories_data = fetch_categories()
        if categories_data:
            category_id = st.selectbox("Seleccionar Categoría", [c["id"] for c in categories_data])
            selected_category = fetch_category(category_id)
            if selected_category:
                with st.form("form_update_category"):
                    nombre = st.text_input("Nombre", value=selected_category["nombre"], max_chars=100)
                    descripcion = st.text_area("Descripción", value=selected_category.get("descripcion", ""), height=100)
                    if st.form_submit_button("Actualizar"):
                        if nombre:
                            category_data = {"nombre": nombre, "descripcion": descripcion if descripcion else None}
                            if update_category(category_id, category_data):
                                st.rerun()
                        else:
                            st.error("El nombre es obligatorio.")
            else:
                st.info("Selecciona una categoría para editar.")
        else:
            st.warning("No hay categorías disponibles para actualizar.")

    with tab4:
        st.header("Eliminar Categoría")
        categories_data = fetch_categories()
        if categories_data:
            with st.form("form_delete_category"):
                category_id = st.selectbox("Seleccionar Categoría para Eliminar", [c["id"] for c in categories_data])
                st.warning("Esta acción no se puede deshacer.")
                if st.form_submit_button("Eliminar"):
                    if delete_category(category_id):
                        st.rerun()
        else:
            st.warning("No hay categorías disponibles para eliminar.")

if __name__ == "__main__":
    show_categories()