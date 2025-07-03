import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# URL base de la API
API_URL = "http://localhost:8000/api/suppliers"

# Función para obtener la lista de proveedores
def fetch_suppliers(skip=0, limit=100):
    try:
        response = requests.get(f"{API_URL}/", params={"skip": skip, "limit": limit})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al recuperar proveedores: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return []

# Función para obtener un proveedor por ID
def fetch_supplier(supplier_id):
    try:
        response = requests.get(f"{API_URL}/{supplier_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al recuperar proveedor: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return None

# Función para crear un nuevo proveedor
def create_supplier(nombre, contacto):
    try:
        response = requests.post(f"{API_URL}/new", json={"nombre": nombre, "contacto": contacto if contacto else None})
        response.raise_for_status()
        st.success("Proveedor creado correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al crear proveedor: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

# Función para actualizar un proveedor
def update_supplier(supplier_id, nombre=None, contacto=None):
    try:
        payload = {k: v for k, v in {"nombre": nombre, "contacto": contacto}.items() if v is not None}
        response = requests.put(f"{API_URL}/update/{supplier_id}", json=payload)
        response.raise_for_status()
        st.success("Proveedor actualizado correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al actualizar proveedor: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

# Función para eliminar un proveedor
def delete_supplier(supplier_id):
    try:
        response = requests.delete(f"{API_URL}/delete/{supplier_id}")
        response.raise_for_status()
        st.success("Proveedor eliminado correctamente")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error al eliminar proveedor: {response.status_code} - {response.text if 'text' in response.__dict__ else str(e)}")
        return False

def show_supplier_contact_info():
    st.title("📞 Gestión de Contacto de Proveedores")
    st.markdown("Administración de la información de contacto de los proveedores")

    # Pestañas para CRUD
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Listar", "🛒 Crear", "✏️ Actualizar", "🗑️ Eliminar"])

    with tab1:
        st.header("Listar Proveedores")
        col1, col2 = st.columns(2)
        with col1:
            skip = st.number_input("Páginado (skip)", min_value=0, value=0, step=10)
        with col2:
            limit = st.number_input("Límite por página", min_value=1, value=10, step=1)
        suppliers_data = fetch_suppliers(skip=skip, limit=limit)
        if suppliers_data:
            df = pd.DataFrame(suppliers_data)
            df["fecha_registro"] = pd.to_datetime(df["fecha_registro"]).dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(df, hide_index=True, use_container_width=True)
        else:
            st.warning("No hay proveedores disponibles.")

    with tab2:
        st.header("Crear Proveedor")
        with st.form("form_create_supplier"):
            nombre = st.text_input("Nombre", max_chars=100)
            contacto = st.text_area("Contacto", height=100)
            if st.form_submit_button("Crear"):
                if nombre:
                    if create_supplier(nombre, contacto):
                        st.rerun()
                else:
                    st.error("El nombre es obligatorio.")

    with tab3:
        st.header("Actualizar Proveedor")
        suppliers_data = fetch_suppliers()
        if suppliers_data:
            supplier_id = st.selectbox("Seleccionar Proveedor", [s["id"] for s in suppliers_data])
            selected_supplier = fetch_supplier(supplier_id)
            if selected_supplier:
                with st.form("form_update_supplier"):
                    nombre = st.text_input("Nombre", value=selected_supplier["nombre"], max_chars=100)
                    contacto = st.text_area("Contacto", value=selected_supplier.get("contacto", ""), height=100)
                    if st.form_submit_button("Actualizar"):
                        if nombre:
                            if update_supplier(supplier_id, nombre, contacto):
                                st.rerun()
                        else:
                            st.error("El nombre es obligatorio.")
            else:
                st.info("Selecciona un proveedor para editar.")
        else:
            st.warning("No hay proveedores disponibles para actualizar.")

    with tab4:
        st.header("Eliminar Proveedor")
        suppliers_data = fetch_suppliers()
        if suppliers_data:
            with st.form("form_delete_supplier"):
                supplier_id = st.selectbox("Seleccionar Proveedor para Eliminar", [s["id"] for s in suppliers_data])
                st.warning("Esta acción no se puede deshacer.")
                if st.form_submit_button("Eliminar"):
                    if delete_supplier(supplier_id):
                        st.rerun()
        else:
            st.warning("No hay proveedores disponibles para eliminar.")

if __name__ == "__main__":
    show_supplier_contact_info()