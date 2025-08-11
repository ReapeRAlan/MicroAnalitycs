import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# URL base de la API
API_BASE_URL = "http://localhost:8000/api"

def get_businesses(skip=0, limit=100):
    try:
        response = requests.get(f"{API_BASE_URL}/business/", params={"skip": skip, "limit": limit})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener negocios: {str(e)}")
        return []

def get_business(business_id):
    try:
        response = requests.get(f"{API_BASE_URL}/business/{business_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener negocio: {str(e)}")
        return None

def create_business(nombre, descripcion):
    try:
        response = requests.post(f"{API_BASE_URL}/business/new", json={"nombre": nombre, "descripcion": descripcion})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al crear negocio: {str(e)}")
        return None

def update_business(business_id, nombre, descripcion):
    try:
        response = requests.put(f"{API_BASE_URL}/business/update/{business_id}", json={"nombre": nombre, "descripcion": descripcion})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al actualizar negocio: {str(e)}")
        return None

def delete_business(business_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/business/delete/{business_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al eliminar negocio: {str(e)}")
        return None

def show_select_business():
    st.title("Gestión de Negocios")
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Seleccionar", "🛍️ Crear", "✏️ Actualizar", "🗑️ Eliminar"])
    
    with tab1:
        st.header("Seleccionar Negocio")
        negocios = get_businesses()
        if negocios:
            for index, row in pd.DataFrame(negocios).iterrows():
                col1, col2, col3 = st.columns([2, 4, 1])
                with col1:
                    st.write(row["nombre"])
                with col2:
                    st.write(row["descripcion"])
                with col3:
                    if st.button("Seleccionar", key=f"select_{row['id']}"):
                        st.session_state.business_id = row['id']
                        st.session_state.page = "main"
                        st.rerun()
        else:
            st.warning("No hay negocios disponibles. Crea uno primero.")
    
    with tab2:
        st.header("Crear Negocio")
        with st.form("form_crear_negocio"):
            nombre = st.text_input("Nombre del negocio")
            descripcion = st.text_area("Descripción")
            if st.form_submit_button("Crear"):
                if nombre:
                    new_business = create_business(nombre, descripcion)
                    if new_business:
                        st.success(f"Negocio creado: {nombre}")
                        st.rerun()
                    else:
                        st.error("Error al crear el negocio.")
                else:
                    st.error("El nombre es obligatorio.")
    
    with tab3:
        st.header("Actualizar Negocio")
        negocios = get_businesses()
        if negocios:
            negocio_id = st.selectbox("Seleccionar negocio", [n["id"] for n in negocios], key="update_business_select")
            selected_negocio = get_business(negocio_id) if negocio_id else None
            if selected_negocio:
                with st.form("form_actualizar_negocio"):
                    nombre_update = st.text_input("Nuevo nombre", value=selected_negocio["nombre"])
                    descripcion_update = st.text_area("Nueva descripción", value=selected_negocio["descripcion"])
                    if st.form_submit_button("Actualizar"):
                        if nombre_update:
                            updated_business = update_business(negocio_id, nombre_update, descripcion_update)
                            if updated_business:
                                st.success(f"Negocio actualizado: {nombre_update}")
                                st.rerun()
                            else:
                                st.error("Error al actualizar el negocio.")
                        else:
                            st.error("El nombre es obligatorio.")
            else:
                st.info("Selecciona un negocio para editar.")
        else:
            st.warning("No hay negocios disponibles para actualizar.")
    
    with tab4:
        st.header("Eliminar Negocio")
        negocios = get_businesses()
        if negocios:
            with st.form("form_eliminar_negocio"):
                negocio_id_delete = st.selectbox("Seleccionar negocio para eliminar", [n["id"] for n in negocios], key="delete_business_select")
                st.warning("Esta acción no se puede deshacer.")
                if st.form_submit_button("Eliminar"):
                    deleted_business = delete_business(negocio_id_delete)
                    if deleted_business:
                        st.success("Negocio eliminado")
                        st.rerun()
                    else:
                        st.error("Error al eliminar el negocio.")
        else:
            st.warning("No hay negocios disponibles para eliminar.")