import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time
import json
from datetime import datetime
from api_utils import get_products, get_categories  # Importar desde api_utils
from inventory import create_inventory  # Mantener esta importación, ahora segura

# URL base de la API (opcional, ya en api_utils)
API_BASE_URL = "http://localhost:8000/api"

def get_product(product_id):
    try:
        response = requests.get(f"{API_BASE_URL}/products/{product_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener producto: {str(e)}")
        return None

def create_product(nombre, descripcion, precio_base, category_id, business_id):
    try:
        response = requests.post(f"{API_BASE_URL}/products/new", json={
            "nombre": nombre,
            "descripcion": descripcion,
            "precio_base": precio_base,
            "category_id": category_id,
            "business_id": business_id
        })
        response.raise_for_status()
        new_product = response.json()
        print(f"Respuesta de creación de producto (raw): {json.dumps(new_product, indent=2)}")
        print(f"Status Code: {response.status_code}")
        
        # Crear un registro de inventario para el nuevo producto
        if create_inventory(new_product["id"], 0):  # Inicializar stock en 0
            st.success(f"Producto creado exitosamente: {nombre} y inventario inicializado.")
        else:
            st.warning(f"Producto creado: {nombre}, pero no se pudo inicializar el inventario.")
        return new_product
    except requests.exceptions.RequestException as e:
        st.error(f"Error al crear producto: {str(e)}")
        return None

def update_product(product_id, nombre=None, descripcion=None, precio_base=None, category_id=None, business_id=None):
    try:
        payload = {k: v for k, v in {
            "nombre": nombre,
            "descripcion": descripcion,
            "precio_base": precio_base,
            "category_id": category_id,
            "business_id": business_id
        }.items() if v is not None}
        response = requests.put(f"{API_BASE_URL}/products/update/{product_id}", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al actualizar producto: {str(e)}")
        return None

def delete_product(product_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/products/delete/{product_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error al eliminar producto: {str(e)}")
        return None

# Pantalla de Productos
def show_products():
    st.title(f"Product Management - Negocio {st.session_state.business_id}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🛍️ Agregar", "✏️ Actualizar", "🗑️ Eliminar", "📋 Listar"])
    
    with tab1:
        st.header("Agregar Producto")
        with st.form("form_crear_producto"):
            nombre = st.text_input("Nombre del producto")
            descripcion = st.text_area("Descripción")
            precio_base = st.number_input("Precio base", min_value=0.0, step=0.01)
            category_id = st.number_input("ID de Categoría", min_value=1, step=1)
            business_id = st.session_state.business_id
            if st.form_submit_button("Crear"):
                if nombre and precio_base >= 0 and category_id and business_id:
                    new_product = create_product(nombre, descripcion, precio_base, category_id, business_id)
                    if new_product:
                        st.success(f"Producto creado exitosamente: {nombre}")
                        get_products(force_refresh=True)
                        time.sleep(4)
                        st.rerun()
                    else:
                        st.error("Error al crear el producto a pesar de 200 OK, revisa la terminal.")
                else:
                    st.error("Por favor, completa todos los campos correctamente")
    
    with tab2:
        st.header("Actualizar Producto")
        productos = get_products()
        if productos:
            producto_id = st.selectbox("Seleccionar un producto", 
                                      [(p["id"], p["nombre"]) for p in productos], 
                                      format_func=lambda x: x[1], key="update_select")
            producto = get_product(producto_id[0]) if producto_id else None
            with st.form("form_actualizar_producto"):
                nombre_update = st.text_input("Nuevo nombre", value=producto["nombre"] if producto else "")
                descripcion_update = st.text_area("Nueva descripción", value=producto["descripcion"] if producto else "")
                precio_base_update = st.number_input("Nuevo precio base", min_value=0.0, step=0.01, value=producto["precio_base"] if producto else 0.0)
                category_id_update = st.number_input("Nuevo ID de Categoría", min_value=1, step=1, value=producto["category_id"] if producto else 1)
                business_id_update = st.session_state.business_id
                if st.form_submit_button("Actualizar"):
                    if nombre_update and precio_base_update >= 0 and category_id_update and business_id_update:
                        updated_product = update_product(producto_id[0], nombre_update, descripcion_update, precio_base_update, category_id_update, business_id_update)
                        if updated_product:
                            st.success(f"Producto actualizado exitosamente: {nombre_update}")
                            st.rerun()
                        else:
                            st.error("Error al actualizar el producto.")
                    else:
                        st.error("Por favor, completa todos los campos correctamente")
        else:
            st.warning("No hay productos disponibles para actualizar.")
    
    with tab3:
        st.header("Eliminar Producto")
        productos = get_products()
        if productos:
            producto_id_delete = st.selectbox("Seleccionar un producto para eliminar", 
                                            [(p["id"], p["nombre"]) for p in productos], 
                                            format_func=lambda x: x[1], key="delete_select")
            if st.button("Eliminar"):
                deleted_product = delete_product(producto_id_delete[0])
                if deleted_product:
                    st.success(f"Producto eliminado exitosamente: {producto_id_delete[1]}")
                    st.rerun()
                else:
                    st.error("Error al eliminar el producto.")
        else:
            st.warning("No hay productos disponibles para eliminar.")
    
    with tab4:
        st.header("Lista de Productos")
        if st.button("Refresh"):
            st.rerun()
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            product_id_filter = st.number_input("Filtrar por ID", min_value=0, value=0, step=1, help="Ingresa 0 para no filtrar por ID")
        with col2:
            categories = get_categories()
            categories = {0: "Todas"} | categories  # Agregar opción "Todas"
            selected_category = st.selectbox("Filtrar por Categoría", options=list(categories.keys()), format_func=lambda x: categories.get(x, "Sin nombre"))

        # Aplicar filtros
        filtered_products = get_products()
        if filtered_products:
            if product_id_filter > 0:
                filtered_products = [p for p in filtered_products if p["id"] == product_id_filter]
            if selected_category != 0:
                filtered_products = [p for p in filtered_products if p["category_id"] == selected_category]
            if not filtered_products:
                st.info("No hay productos que coincidan con los filtros.")
            else:
                df_productos = pd.DataFrame(filtered_products)
                # Agregar columna con nombre de categoría
                df_productos["categoria_nombre"] = df_productos["category_id"].map(categories).fillna("Sin categoría")
                st.dataframe(df_productos, use_container_width=True)
        else:
            st.info("No hay productos disponibles.")

if __name__ == "__main__":
    show_products()