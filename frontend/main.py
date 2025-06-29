import streamlit as st
from app import show_select_business
from dashboard import show_dashboard
from products import show_products
from sales import show_sales
from chatbot_app_working import ChatbotFrontend

# Configuración inicial (primer comando)
st.set_page_config(
    page_title="MicroAnalytics POS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado combinado
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

# Estado de la sesión compartido
if "business_id" not in st.session_state:
    st.session_state.business_id = None
if "page" not in st.session_state:
    st.session_state.page = "select_business"

# Inicializar el chatbot
chatbot = ChatbotFrontend()

# Navegación principal
if st.session_state.page == "select_business":
    show_select_business()
else:
    # Sidebar para navegación
    st.sidebar.title("MicroAnalytics")
    opcion = st.sidebar.selectbox("🖥️ Seleccionar sección", ["Dashboard", "🛒 Productos", "💰 Ventas", "🤖 Chat"])
    
    if opcion == "Dashboard":
        show_dashboard()
    elif opcion == "🛒 Productos":
        show_products()
    elif opcion == "💰 Ventas":
        show_sales()
    elif opcion == "🤖 Chat":
        chatbot.run()

# Botón para cambiar de negocio desde cualquier sección
if st.sidebar.button("Cambiar Negocio"):
    st.session_state.business_id = None
    st.session_state.page = "select_business"
    st.rerun()