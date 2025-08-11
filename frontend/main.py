import streamlit as st

# Configuración inicial (primer comando)
st.set_page_config(
    page_title="MicroAnalytics POS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado combinado
st.markdown("""
    <style>
    .main { background-color: #1A2A44; color: #E0E8F0; }
    .stButton>button { background-color: #3498DB; color: #1A2A44; border-radius: 8px; border: none; padding: 5px 10px; font-weight: bold; vertical-align: middle; margin: 0; width: auto; box-sizing: border-box; display: inline-block; }
    .stButton>button:hover { background-color: #5DADE2; color: #1A2A44; }
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>select { background-color: #2B4066; color: #E0E8F0; border: 1px solid #3498DB; border-radius: 5px; }
    h1, h2, h3 { color: #FFFFFF !important; font-family: 'Arial', sans-serif; }
    .sidebar .sidebar-content { background-color: #2B4066; position: relative; height: 100vh; }
    .change-business-button { position: absolute; bottom: 20px; right: 20px; }
    .main .stDataFrame, .main .stDataFrame table { background-color: #1A2A44 !important; color: #E0E8F0 !important; border: none !important; }
    .main .stDataFrame th, .main .stDataFrame td { background-color: #1A2A44 !important; color: #E0E8F0 !important; border: 1px solid #3498DB !important; padding: 8px; }
    .main .stDataFrame tr { background-color: #1A2A44 !important; }
    .main .stTabs { background-color: #1A2A44 !important; border: none !important; }
    .main .stTabs [data-baseweb="tab"] { background-color: #2B4066 !important; color: #E0E8F0 !important; border: none !important; }
    .main .stTabs [data-baseweb="tab"]:hover { background-color: #3498DB !important; color: #1A2A44 !important; }
    .main .stForm { background-color: #1A2A44 !important; border: none !important; }
    .stContainer { background-color: #1A2A44 !important; border: none !important; color: #E0E8F0 !important; }
    </style>
""", unsafe_allow_html=True)

# Importaciones después de set_page_config
from business import show_select_business
from dashboard import show_dashboard
from products import show_products
from sales import show_sales
from category import show_categories
from inventory import show_inventory
from supplier import show_supplier_contact_info
from supplier_prices import show_supplier_prices
from chatbot_app import ChatbotFrontend

# Estado de la sesión compartido
if "business_id" not in st.session_state:
    st.session_state.business_id = "Negocio001"  # Inicialización por defecto
if "page" not in st.session_state:
    st.session_state.page = "select_business"

# Inicializar ventas simuladas después de establecer business_id
from api_utils import generar_ventas_simuladas
if "ventas_simuladas" not in st.session_state:
    st.session_state.ventas_simuladas = generar_ventas_simuladas(business_id=st.session_state.business_id)

# Inicializar el chatbot
chatbot = ChatbotFrontend()

# Navegación principal
if st.session_state.page == "select_business":
    show_select_business()
else:
    st.sidebar.title("MicroAnalytics")
    opcion = st.sidebar.selectbox("🖥️ Seleccionar sección", ["Dashboard", "📦 Inventario", "🛒 Productos", "💰 Ventas", "📂 Categorías", "🏭 Proveedores", "🤖 Chat"])
    
    if opcion == "🏭 Proveedores":
        sub_opcion = st.sidebar.selectbox("📦 Submenú Proveedores", ["📞 Gestión de Contacto", "💰 Precios de Proveedores"])

    if opcion == "Dashboard":
        show_dashboard()
    elif opcion == "📦 Inventario":
        show_inventory()
    elif opcion == "🛒 Productos":
        show_products()
    elif opcion == "💰 Ventas":
        show_sales()
    elif opcion == "📂 Categorías":
        show_categories()
    elif opcion == "🏭 Proveedores":
        if sub_opcion == "📞 Gestión de Contacto":
            show_supplier_contact_info()
        elif sub_opcion == "💰 Precios de Proveedores":
            show_supplier_prices()
    elif opcion == "🤖 Chat":
        chatbot.run()

# Botón para cambiar de negocio desde cualquier sección
if st.session_state.page != "select_business":
    if st.sidebar.button("Cambiar Negocio"):
        st.session_state.business_id = None
        st.session_state.page = "select_business"
        st.rerun()