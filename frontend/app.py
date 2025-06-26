import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time
import json
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="MicroAnalytics POS", layout="wide", initial_sidebar_state="expanded")

# Estilo personalizado con tonos de azul y formato de tabla
st.markdown("""
    <style>
    .main {
        background-color: #1A2A44;
        color: #E0E8F0;
    }
    .stButton>button {
        background-color: #3498DB;
        color: #1A2A44;
        border-radius: 8px;
        border: none;
        padding: 5px 10px;
        font-weight: bold;
        vertical-align: middle;
        margin: 0;
        width: auto;
        box-sizing: border-box;
        display: inline-block;
    }
    .stButton>button:hover {
        background-color: #5DADE2;
        color: #1A2A44;
    }
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>select {
        background-color: #2B4066;
        color: #E0E8F0;
        border: 1px solid #3498DB;
        border-radius: 5px;
    }
    h1, h2, h3 {
        color: #2980B9;
        font-family: 'Arial', sans-serif;
    }
    .sidebar .sidebar-content {
        background-color: #2B4066;
        position: relative;
        height: 100vh;
    }
    .change-business-button {
        position: absolute;
        bottom: 20px;
        right: 20px;
    }
    .main .stDataFrame, .main .stDataFrame table {
        background-color: #1A2A44 !important;
        color: #E0E8F0 !important;
        border: none !important;
    }
    .main .stDataFrame th, .main .stDataFrame td {
        background-color: #1A2A44 !important;
        color: #E0E8F0 !important;
        border: 1px solid #3498DB !important;
        padding: 8px;
    }
    .main .stDataFrame tr {
        background-color: #1A2A44 !important;
    }
    .main .stTabs {
        background-color: #1A2A44 !important;
        border: none !important;
    }
    .main .stTabs [data-baseweb="tab"] {
        background-color: #2B4066 !important;
        color: #E0E8F0 !important;
        border: none !important;
    }
    .main .stTabs [data-baseweb="tab"]:hover {
        background-color: #3498DB !important;
        color: #1A2A44 !important;
    }
    .main .stForm {
        background-color: #1A2A44 !important;
        border: none !important;
    }
    .stContainer {
        background-color: #1A2A44 !important;
        border: none !important;
        color: #E0E8F0 !important;
    }
    /* Estilo personalizado para la tabla de negocios en Seleccionar */
    .business-table-container {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #3498DB;
    }
    .business-table {
        border-collapse: collapse;
        width: 100%;
    }
    .business-table table {
        width: 100%;
        border-collapse: collapse;
    }
    .business-table th, .business-table td {
        border: 1px solid #3498DB !important;
        padding: 8px;
        text-align: left;
        vertical-align: middle;
    }
    .business-table .button-cell {
        padding: 0;
        width: 34%;
    }
    .business-table .button-cell .button-wrapper {
        display: inline-block;
        width: auto;
        vertical-align: middle;
    }
    </style>
""", unsafe_allow_html=True)

# URL base de la API
API_BASE_URL = "http://localhost:8000/api"

# Inicializar estado de la sesión
if "business_id" not in st.session_state:
    st.session_state.business_id = None
if "page" not in st.session_state:
    st.session_state.page = "select_business"  # Inicio directo en selección de negocio

# Funciones para negocios
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

# Funciones para productos
def get_products(skip=0, limit=1000, force_refresh=False):
    try:
        timestamp = datetime.now().timestamp()
        response = requests.get(f"{API_BASE_URL}/products/?skip={skip}&limit={limit}&t={timestamp}")
        response.raise_for_status()
        products = response.json()
        print(f"Productos obtenidos de la API (force_refresh={force_refresh}, skip={skip}, limit={limit}, raw response: {json.dumps(products, indent=2)})")
        if st.session_state.business_id:
            filtered_products = [p for p in products if p.get("business_id") == st.session_state.business_id]
            print(f"Productos filtrados por business_id {st.session_state.business_id}: {json.dumps(filtered_products, indent=2)}")
            return filtered_products
        return products
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener productos: {str(e)}")
        return []

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

# Pantalla de Selección de Negocio
def show_select_business():
    st.title("Gestión de Negocios")
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Seleccionar", "🛍️ Crear", "✏️ Actualizar", "🗑️ Eliminar"])
    
    with tab1:
        st.header("Seleccionar Negocio")
        negocios = get_businesses()
        if negocios:
            for n in negocios:
                cols = st.columns([3, 3, 1])
                cols[0].write(n["nombre"])
                cols[1].write(n["descripcion"])
                if cols[2].button("Seleccionar", key=f"select_{n['id']}"):
                    st.session_state.business_id = n["id"]
                    st.session_state.page = "main"
                    st.rerun()
        else:
            st.warning("No hay negocios disponibles.")
    
    with tab2:
        st.header("Crear Negocio")
        with st.form("form_crear_negocio"):
            nombre = st.text_input("Nombre del negocio")
            descripcion = st.text_area("Descripción")
            if st.form_submit_button("Crear"):
                if nombre:
                    new_business = create_business(nombre, descripcion)
                    if new_business:
                        st.success(f"Negocio creado exitosamente: {nombre}")
                        st.rerun()
                    else:
                        st.error("Error al crear el negocio.")
                else:
                    st.error("El nombre es obligatorio.")
    
    with tab3:
        st.header("Actualizar Negocio")
        negocios = get_businesses()
        if negocios:
            negocio_id = st.selectbox(
                "Seleccionar negocio",
                [(n["id"], n["nombre"]) for n in negocios],
                format_func=lambda x: x[1],
                key="update_business_select"
            )
            selected_negocio = get_business(negocio_id[0]) if negocio_id else None
            if selected_negocio:
                with st.form("form_actualizar_negocio"):
                    nombre_update = st.text_input("Nuevo nombre", value=selected_negocio["nombre"])
                    descripcion_update = st.text_area("Nueva descripción", value=selected_negocio["descripcion"])
                    if st.form_submit_button("Actualizar"):
                        if nombre_update:
                            updated_business = update_business(negocio_id[0], nombre_update, descripcion_update)
                            if updated_business:
                                st.success(f"Negocio actualizado exitosamente: {nombre_update}")
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
                negocio_id_delete = st.selectbox(
                    "Seleccionar negocio para eliminar",
                    [(n["id"], n["nombre"]) for n in negocios],
                    format_func=lambda x: x[1],
                    key="delete_business_select"
                )
                st.warning("Esta acción no se puede deshacer.")
                if st.form_submit_button("Eliminar"):
                    deleted_business = delete_business(negocio_id_delete[0])
                    if deleted_business:
                        st.success(f"Negocio eliminado exitosamente: {negocio_id_delete[1]}")
                        st.rerun()
                    else:
                        st.error("Error al eliminar el negocio.")
        else:
            st.warning("No hay negocios disponibles para eliminar.")

# Pantalla Principal (Dashboard, Productos, Ventas)
def show_main():
    st.sidebar.title("MicroAnalytics")
    opcion = st.sidebar.selectbox(
        "🖥️ Seleccionar sección", ["Dashboard", "🛒 Productos", "💰 Ventas"]
    )
    st.sidebar.markdown("<div class='change-business-button'>", unsafe_allow_html=True)
    if st.sidebar.button("Cambiar Negocio"):
        st.session_state.business_id = None
        st.session_state.page = "select_business"
        st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    if opcion == "Dashboard":
        st.title(f"Dashboard - Negocio {st.session_state.business_id}")
        st.header("📦 Inventario Actual")
        productos = get_products()
        if productos:
            df_productos = pd.DataFrame(productos)
            st.dataframe(df_productos, use_container_width=True)
            fig = px.bar(df_productos, x="nombre", y="precio_base", title="Precios por Producto",
                         color="precio_base", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay productos disponibles.")

        st.header("📈 Ventas Recientes")
        ventas = []
        if ventas:
            df_ventas = pd.DataFrame(ventas)
            st.dataframe(df_ventas, use_container_width=True)
        else:
            st.info("No hay ventas disponibles.")

    elif opcion == "🛒 Productos":
        st.title(f"Product Management - Negocio {st.session_state.business_id}")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛍️ Agregar", "✏️ Actualizar", "🗑️ Eliminar", "📋 Listar", "🔍 Buscar por ID"])
        
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
            productos = get_products()
            if productos:
                df_productos = pd.DataFrame(productos)
                st.dataframe(df_productos, use_container_width=True)
            else:
                st.info("No hay productos disponibles.")
        
        with tab5:
            st.header("Buscar Producto por ID")
            product_id = st.number_input("Ingrese el ID del producto", min_value=1, step=1)
            if st.button("Buscar"):
                product = get_product(product_id)
                if product:
                    st.write("Detalles del producto:")
                    df_product = pd.DataFrame([product])
                    st.table(df_product)
                else:
                    st.error("Producto no encontrado.")

    elif opcion == "💰 Ventas":
        st.title(f"Sales Management - Negocio {st.session_state.business_id}")
        
        tab1, tab2 = st.tabs(["💸 Agregar", "📊 Mostrar"])
        
        with tab1:
            st.header("Registrar Venta")
            productos = get_products()
            if productos:
                with st.form("form_registrar_venta"):
                    producto_id = st.selectbox("Seleccionar un producto", 
                                              [(p["id"], p["nombre"]) for p in productos], 
                                              format_func=lambda x: x[1])
                    cantidad = st.number_input("Cantidad", min_value=1, step=1)
                    if st.form_submit_button("Registrar"):
                        if cantidad > 0:
                            st.success("Venta registrada exitosamente (simulado por ahora)")
                        else:
                            st.error("La cantidad debe ser mayor a 0")
            else:
                st.info("No hay productos disponibles para registrar ventas.")
        
        with tab2:
            st.header("Lista de Ventas")
            ventas = []
            if ventas:
                df_ventas = pd.DataFrame(ventas)
                st.dataframe(df_ventas, use_container_width=True)
            else:
                st.info("No hay ventas disponibles.")

# Control de navegación
if st.session_state.page == "select_business":
    show_select_business()
else:
    show_main()