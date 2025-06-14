import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="MicroAnalytics POS", layout="wide", initial_sidebar_state="expanded")

# Estilo personalizado con tonos de azul
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
        padding: 10px 20px;
        font-weight: bold;
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
    }
    </style>
""", unsafe_allow_html=True)

# URL base de la API
API_BASE_URL = "http://localhost:8000"

# Funciones para interactuar con la API
def get_productos():
    try:
        response = requests.get(f"{API_BASE_URL}/productos/")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error al obtener productos: {e}")
        return []

def create_producto(nombre, precio_base, stock_actual):
    try:
        response = requests.post(f"{API_BASE_URL}/productos/", json={
            "nombre": nombre,
            "precio_base": precio_base,
            "stock_actual": stock_actual
        })
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error al crear producto: {e}")
        return None

def get_producto(producto_id):
    try:
        response = requests.get(f"{API_BASE_URL}/productos/{producto_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error al obtener producto: {e}")
        return None

def update_producto(producto_id, nombre, precio_base, stock_actual):
    try:
        response = requests.put(f"{API_BASE_URL}/productos/{producto_id}", json={
            "nombre": nombre,
            "precio_base": precio_base,
            "stock_actual": stock_actual
        })
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error al actualizar producto: {e}")
        return None

def delete_producto(producto_id):
    try:
        response = requests.delete(f"{API_BASE_URL}/productos/{producto_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error al eliminar producto: {e}")
        return None

def registrar_venta(producto_id, cantidad):
    try:
        response = requests.post(f"{API_BASE_URL}/ventas/", json={
            "producto_id": producto_id,
            "cantidad": cantidad
        })
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error al registrar venta: {e}")
        return None

def get_ventas():
    try:
        response = requests.get(f"{API_BASE_URL}/ventas/")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error al obtener ventas: {e}")
        return []

# Barra lateral para navegación
st.sidebar.title("MicroAnalytics")
opcion = st.sidebar.selectbox("🖥️ Seleccionar sección", ["Dashboard", "🛒 Productos", "💰 Ventas"])

# Dashboard
if opcion == "Dashboard":
    st.title("Dashboard")
    
    # Resumen de inventario
    st.header("📦 Inventario Actual")
    productos = get_productos()
    if productos:
        df_productos = pd.DataFrame(productos)
        st.dataframe(df_productos, use_container_width=True)
        
        # Gráfico de barras para stock
        fig = px.bar(df_productos, x="nombre", y="stock_actual", title="Stock por Producto",
                     color="stock_actual", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)
    
    # Resumen de ventas
    st.header("📈 Ventas Recientes")
    ventas = get_ventas()
    if ventas:
        df_ventas = pd.DataFrame(ventas)
        st.dataframe(df_ventas, use_container_width=True)

# Sección de Productos
elif opcion == "🛒 Productos":
    st.title("Product Management")
    
    # Menú lineal para CRUD
    tab1, tab2, tab3, tab4 = st.tabs(["🛍️ Agregar", "✏️ Actualizar", "🗑️ Eliminar", "📋 Listar"])
    
    with tab1:
        st.header("Agregar Producto")
        with st.form("form_crear_producto"):
            nombre = st.text_input("Nombre del producto")
            precio_base = st.number_input("Precio base", min_value=0.0, step=0.01)
            stock_actual = st.number_input("Stock inicial", min_value=0, step=1)
            if st.form_submit_button("Crear"):
                if nombre and precio_base >= 0 and stock_actual >= 0:
                    nuevo_producto = create_producto(nombre, precio_base, stock_actual)
                    if nuevo_producto:
                        st.success("Producto creado exitosamente")
                else:
                    st.error("Por favor, completa todos los campos correctamente")
    
    with tab2:
        st.header("Actualizar Producto")
        productos = get_productos()
        if productos:
            producto_id = st.selectbox("Seleccionar un producto", 
                                      [(p["id"], p["nombre"]) for p in productos], 
                                      format_func=lambda x: x[1], key="update_select")
            producto = get_producto(producto_id[0]) if producto_id else None
            with st.form("form_actualizar_producto"):
                nombre_update = st.text_input("Nuevo nombre", value=producto["nombre"] if producto else "")
                precio_base_update = st.number_input("Nuevo precio base", min_value=0.0, step=0.01, value=producto["precio_base"] if producto else 0.0)
                stock_actual_update = st.number_input("Nuevo stock", min_value=0, step=1, value=producto["stock_actual"] if producto else 0)
                if st.form_submit_button("Actualizar"):
                    if nombre_update and precio_base_update >= 0 and stock_actual_update >= 0:
                        updated = update_producto(producto_id[0], nombre_update, precio_base_update, stock_actual_update)
                        if updated:
                            st.success("Producto actualizado exitosamente")
                    else:
                        st.error("Por favor, completa todos los campos correctamente")
    
    with tab3:
        st.header("Eliminar Producto")
        productos = get_productos()
        if productos:
            producto_id_delete = st.selectbox("Seleccionar un producto para eliminar", 
                                            [(p["id"], p["nombre"]) for p in productos], 
                                            format_func=lambda x: x[1], key="delete_select")
            if st.button("Eliminar"):
                deleted = delete_producto(producto_id_delete[0])
                if deleted:
                    st.success("Producto eliminado exitosamente")
    
    with tab4:
        st.header("Lista de Productos")
        productos = get_productos()
        if productos:
            df_productos = pd.DataFrame(productos)
            st.dataframe(df_productos, use_container_width=True)

# Sección de Ventas
elif opcion == "💰 Ventas":
    st.title("Sales Management")
    
    # Menú lineal para Ventas
    tab1, tab2 = st.tabs(["💸 Agregar", "📊 Mostrar"])
    
    with tab1:
        st.header("Registrar Venta")
        productos = get_productos()
        with st.form("form_registrar_venta"):
            producto_id = st.selectbox("Seleccionar un producto", 
                                      [(p["id"], p["nombre"]) for p in productos], 
                                      format_func=lambda x: x[1])
            cantidad = st.number_input("Cantidad", min_value=1, step=1)
            if st.form_submit_button("Registrar"):
                if cantidad > 0:
                    venta = registrar_venta(producto_id[0], cantidad)
                    if venta:
                        st.success("Venta registrada exitosamente")
                else:
                    st.error("La cantidad debe ser mayor a 0")
    
    with tab2:
        st.header("Lista de Ventas")
        ventas = get_ventas()
        if ventas:
            df_ventas = pd.DataFrame(ventas)
            st.dataframe(df_ventas, use_container_width=True)