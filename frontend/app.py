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
        border: none !important;
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
    </style>
""", unsafe_allow_html=True)

# URL base de la API (no se usará, pero se mantiene para consistencia)
API_BASE_URL = "http://localhost:8000"

# Inicializar estado de la sesión
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "business_id" not in st.session_state:
    st.session_state.business_id = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# Funciones con datos simulados
def get_businesses():
    return [
        {"id": 1, "nombre": "Negocio Simulado 1", "descripcion": "Tienda de tecnología en el centro"},
        {"id": 2, "nombre": "Negocio Simulado 2", "descripcion": "Cafetería artesanal"},
        {"id": 3, "nombre": "Negocio Simulado 3", "descripcion": "Librería independiente"}
    ]

def get_productos(business_id=None):
    # Simulación de productos para pruebas
    return [
        {"id": 1, "nombre": "Producto Simulado 1", "precio_base": 10.0, "stock_actual": 100},
        {"id": 2, "nombre": "Producto Simulado 2", "precio_base": 20.0, "stock_actual": 50}
    ]

def create_producto(nombre, precio_base, stock_actual, business_id=None):
    st.success(f"Producto creado (simulado): {nombre}, {precio_base}, {stock_actual}")
    return {"id": len(get_productos()) + 1, "nombre": nombre, "precio_base": precio_base, "stock_actual": stock_actual}

def get_producto(producto_id, business_id=None):
    productos = get_productos(business_id)
    return next((p for p in productos if p["id"] == producto_id), None)

def update_producto(producto_id, nombre, precio_base, stock_actual, business_id=None):
    st.success(f"Producto actualizado (simulado): {producto_id}, {nombre}, {precio_base}, {stock_actual}")
    return {"id": producto_id, "nombre": nombre, "precio_base": precio_base, "stock_actual": stock_actual}

def delete_producto(producto_id, business_id=None):
    st.success(f"Producto eliminado (simulado): {producto_id}")
    return {"message": "Eliminado"}

def registrar_venta(producto_id, cantidad, business_id=None):
    st.success(f"Venta registrada (simulada): {producto_id}, {cantidad}")
    return {"id": len(get_ventas(business_id)) + 1, "producto_id": producto_id, "cantidad": cantidad, "fecha": "2025-06-22"}

def get_ventas(business_id=None):
    # Simulación de ventas para pruebas
    return [
        {"id": 1, "producto_id": 1, "cantidad": 5, "fecha": "2025-06-22"},
        {"id": 2, "producto_id": 2, "cantidad": 3, "fecha": "2025-06-21"}
    ]

# Pantalla de Login
def show_login():
    st.markdown("<h1 style='text-align: center; color: #2980B9;'>Bienvenido a MicroAnalytics</h1>", unsafe_allow_html=True)
    with st.form("form_login"):
        st.markdown("<h3 style='text-align: center; color: #2980B9;'>Iniciar Sesión</h3>", unsafe_allow_html=True)
        correo = st.text_input("Correo Electrónico", placeholder="ejemplo@correo.com")
        contrasena = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
        cols = st.columns([2, 1, 2])
        with cols[1]:
            if st.form_submit_button("Iniciar Sesión"):
                if correo and contrasena:
                    st.session_state.logged_in = True
                    st.session_state.page = "select_business"
                    st.success("Inicio de sesión exitoso (simulado).")
                else:
                    st.error("Por favor, completa todos los campos.")

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
                    st.success(f"Negocio '{n['nombre']}' seleccionado.")
        else:
            st.warning("No hay negocios disponibles.")
    
    with tab2:
        st.header("Crear Negocio")
        with st.form("form_crear_negocio"):
            nombre = st.text_input("Nombre del negocio")
            descripcion = st.text_area("Descripción")
            if st.form_submit_button("Crear"):
                if nombre:
                    st.success(f"Negocio creado (simulado): {nombre}, {descripcion}")
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
            selected_negocio = next((n for n in negocios if n["id"] == negocio_id[0]), None)
            if selected_negocio:
                with st.form("form_actualizar_negocio"):
                    nombre_update = st.text_input("Nuevo nombre", value=selected_negocio["nombre"])
                    descripcion_update = st.text_area("Nueva descripción", value=selected_negocio["descripcion"])
                    if st.form_submit_button("Actualizar"):
                        if nombre_update:
                            st.success(f"Negocio actualizado (simulado): {nombre_update}, {descripcion_update}")
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
                    st.success(f"Negocio eliminado (simulado): {negocio_id_delete[1]}")
        else:
            st.warning("No hay negocios disponibles para eliminar.")

# Pantalla Principal (Dashboard, Productos, Ventas)
def show_main():
    # Barra lateral
    st.sidebar.title("MicroAnalytics")
    opcion = st.sidebar.selectbox(
        "🖥️ Seleccionar sección", ["Dashboard", "🛒 Productos", "💰 Ventas"]
    )
    st.sidebar.markdown("<div class='change-business-button'>", unsafe_allow_html=True)
    if st.sidebar.button("Cambiar Negocio"):
        st.session_state.page = "select_business"
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # Dashboard
    if opcion == "Dashboard":
        st.title(f"Dashboard - Negocio {st.session_state.business_id}")
        st.header("📦 Inventario Actual")
        productos = get_productos(st.session_state.business_id)
        if productos:
            df_productos = pd.DataFrame(productos)
            st.dataframe(df_productos, use_container_width=True)
            fig = px.bar(df_productos, x="nombre", y="stock_actual", title="Stock por Producto",
                         color="stock_actual", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay productos disponibles.")
        
        st.header("📈 Ventas Recientes")
        ventas = get_ventas(st.session_state.business_id)
        if ventas:
            df_ventas = pd.DataFrame(ventas)
            st.dataframe(df_ventas, use_container_width=True)
        else:
            st.info("No hay ventas disponibles.")

    # Sección de Productos
    elif opcion == "🛒 Productos":
        st.title(f"Product Management - Negocio {st.session_state.business_id}")
        
        tab1, tab2, tab3, tab4 = st.tabs(["🛍️ Agregar", "✏️ Actualizar", "🗑️ Eliminar", "📋 Listar"])
        
        with tab1:
            st.header("Agregar Producto")
            with st.form("form_crear_producto"):
                nombre = st.text_input("Nombre del producto")
                precio_base = st.number_input("Precio base", min_value=0.0, step=0.01)
                stock_actual = st.number_input("Stock inicial", min_value=0, step=1)
                if st.form_submit_button("Crear"):
                    if nombre and precio_base >= 0 and stock_actual >= 0:
                        nuevo_producto = create_producto(nombre, precio_base, stock_actual, st.session_state.business_id)
                        if nuevo_producto:
                            st.success("Producto creado exitosamente")
                    else:
                        st.error("Por favor, completa todos los campos correctamente")
        
        with tab2:
            st.header("Actualizar Producto")
            productos = get_productos(st.session_state.business_id)
            if productos:
                producto_id = st.selectbox("Seleccionar un producto", 
                                          [(p["id"], p["nombre"]) for p in productos], 
                                          format_func=lambda x: x[1], key="update_select")
                producto = get_producto(producto_id[0], st.session_state.business_id) if producto_id else None
                with st.form("form_actualizar_producto"):
                    nombre_update = st.text_input("Nuevo nombre", value=producto["nombre"] if producto else "")
                    precio_base_update = st.number_input("Nuevo precio base", min_value=0.0, step=0.01, value=producto["precio_base"] if producto else 0.0)
                    stock_actual_update = st.number_input("Nuevo stock", min_value=0, step=1, value=producto["stock_actual"] if producto else 0)
                    if st.form_submit_button("Actualizar"):
                        if nombre_update and precio_base_update >= 0 and stock_actual_update >= 0:
                            updated = update_producto(producto_id[0], nombre_update, precio_base_update, stock_actual_update, st.session_state.business_id)
                            if updated:
                                st.success("Producto actualizado exitosamente")
                        else:
                            st.error("Por favor, completa todos los campos correctamente")
            else:
                st.warning("No hay productos disponibles para actualizar.")
        
        with tab3:
            st.header("Eliminar Producto")
            productos = get_productos(st.session_state.business_id)
            if productos:
                producto_id_delete = st.selectbox("Seleccionar un producto para eliminar", 
                                                [(p["id"], p["nombre"]) for p in productos], 
                                                format_func=lambda x: x[1], key="delete_select")
                if st.button("Eliminar"):
                    deleted = delete_producto(producto_id_delete[0], st.session_state.business_id)
                    if deleted:
                        st.success("Producto eliminado exitosamente")
            else:
                st.warning("No hay productos disponibles para eliminar.")
        
        with tab4:
            st.header("Lista de Productos")
            productos = get_productos(st.session_state.business_id)
            if productos:
                df_productos = pd.DataFrame(productos)
                st.dataframe(df_productos, use_container_width=True)
            else:
                st.info("No hay productos disponibles.")

    # Sección de Ventas
    elif opcion == "💰 Ventas":
        st.title(f"Sales Management - Negocio {st.session_state.business_id}")
        
        tab1, tab2 = st.tabs(["💸 Agregar", "📊 Mostrar"])
        
        with tab1:
            st.header("Registrar Venta")
            productos = get_productos(st.session_state.business_id)
            if productos:
                with st.form("form_registrar_venta"):
                    producto_id = st.selectbox("Seleccionar un producto", 
                                              [(p["id"], p["nombre"]) for p in productos], 
                                              format_func=lambda x: x[1])
                    cantidad = st.number_input("Cantidad", min_value=1, step=1)
                    if st.form_submit_button("Registrar"):
                        if cantidad > 0:
                            venta = registrar_venta(producto_id[0], cantidad, st.session_state.business_id)
                            if venta:
                                st.success("Venta registrada exitosamente")
                        else:
                            st.error("La cantidad debe ser mayor a 0")
            else:
                st.info("No hay productos disponibles para registrar ventas.")
        
        with tab2:
            st.header("Lista de Ventas")
            ventas = get_ventas(st.session_state.business_id)
            if ventas:
                df_ventas = pd.DataFrame(ventas)
                st.dataframe(df_ventas, use_container_width=True)
            else:
                st.info("No hay ventas disponibles.")

# Control de navegación
if st.session_state.page == "login":
    show_login()
elif st.session_state.page == "select_business":
    show_select_business()
else:
    show_main()