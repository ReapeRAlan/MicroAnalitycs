import streamlit as st
from business import show_select_business
from dashboard import show_dashboard
from products import show_products
from sales import show_sales
from chatbot_app_working import ChatbotFrontend
from inventory import show_inventory

# Configuración inicial (primer comando)
st.set_page_config(
    page_title="MicroAnalytics POS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado combinado (incluye estilos del chat con ajustes)
st.markdown("""
    <style>
    /* Estilos generales de main.py */
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
    /* Cambiar títulos globales a blanco fuera del chat */
    h1, h2, h3 {
        color: #FFFFFF !important;
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
        color: #FFFFFF !important; /* Cambiar texto de la tabla a blanco */
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

    /* Estilos del chat de run() con ajustes */
    .stChatMessage {
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        font-size: 16px;
        line-height: 1.7;
        border: 2px solid transparent;
    }

    .user-message {
        background-color: #ffffff !important;
        border: 3px solid #1976d2 !important;
        color: #0d47a1 !important;
        font-weight: 600;
        box-shadow: 0 3px 10px rgba(25, 118, 210, 0.2);
    }

    .user-message strong {
        color: #0d47a1 !important;
        font-weight: 700;
    }

    .assistant-message {
        background-color: #ffffff !important;
        border: 3px solid #7b1fa2 !important;
        color: #212121 !important;
        box-shadow: 0 4px 15px rgba(123, 31, 162, 0.15);
    }

    /* Limitar el color negro al contexto del chat */
    .assistant-message,
    .assistant-message *,
    .assistant-message p,
    .assistant-message div,
    .assistant-message span,
    .assistant-message li,
    .assistant-message td,
    .assistant-message th {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* Títulos dentro del chat */
    .assistant-message h1,
    .assistant-message h2,
    .assistant-message h3,
    .assistant-message h4,
    .assistant-message h5,
    .assistant-message h6 {
        color: #000000 !important;
        font-weight: 800 !important;
        margin: 20px 0 15px 0 !important;
        text-shadow: none !important;
        background-color: #e8eaf6 !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        border-left: 4px solid #3f51b5 !important;
    }

    /* Texto enfatizado negro sólido */
    .assistant-message strong,
    .assistant-message b {
        color: #000000 !important;
        font-weight: 800 !important;
        background-color: #fff3e0 !important;
        padding: 2px 4px !important;
        border-radius: 3px !important;
    }

    /* Enlaces completamente visibles */
    .assistant-message a {
        color: #000000 !important;
        text-decoration: underline !important;
        font-weight: 700 !important;
        background-color: #e3f2fd !important;
        padding: 2px 4px !important;
        border-radius: 3px !important;
    }

    /* Indicadores de confianza con contraste extremo */
    .confidence-high { 
        color: #000000 !important; 
        font-weight: 900 !important;
        background-color: #c8e6c9 !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        border: 3px solid #2e7d32 !important;
        text-shadow: none !important;
    }

    .confidence-medium { 
        color: #000000 !important; 
        font-weight: 900 !important;
        background-color: #ffe0b2 !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        border: 3px solid #f57c00 !important;
        text-shadow: none !important;
    }

    .confidence-low { 
        color: #000000 !important; 
        font-weight: 900 !important;
        background-color: #ffcdd2 !important;
        padding: 6px 12px !important;
        border-radius: 6px !important;
        border: 3px solid #d32f2f !important;
        text-shadow: none !important;
    }

    /* Listas completamente negras */
    .assistant-message ul,
    .assistant-message ol {
        color: #000000 !important;
        margin: 15px 0 !important;
    }

    .assistant-message ul li,
    .assistant-message ol li {
        color: #000000 !important;
        font-weight: 600 !important;
        margin: 8px 0 !important;
        padding-left: 10px !important;
    }

    .assistant-message ul li::marker,
    .assistant-message ol li::marker {
        color: #000000 !important;
    }

    /* Código completamente visible */
    .assistant-message code,
    .assistant-message pre {
        background-color: #f5f5f5 !important;
        color: #000000 !important;
        border: 2px solid #666666 !important;
        border-radius: 4px !important;
        padding: 8px !important;
        font-weight: 600 !important;
    }

    /* Limitar reglas generales de Streamlit al contexto del chat */
    .assistant-message div[data-testid="stMarkdown"],
    .assistant-message div[data-testid="stMarkdown"] *,
    .assistant-message .stMarkdown,
    .assistant-message .stMarkdown *,
    .assistant-message .st-emotion-cache-acwcvw,
    .assistant-message .st-emotion-cache-acwcvw *,
    .assistant-message .st-emotion-cache-1sdpuyj,
    .assistant-message .st-emotion-cache-1sdpuyj * {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* Selectores específicos para elementos problemáticos dentro del chat */
    .assistant-message div[data-testid="stMarkdown"] p,
    .assistant-message div[data-testid="stMarkdown"] div,
    .assistant-message div[data-testid="stMarkdown"] span,
    .assistant-message div[data-testid="stMarkdown"] li,
    .assistant-message .stMarkdown p,
    .assistant-message .stMarkdown div,
    .assistant-message .stMarkdown span,
    .assistant-message .stMarkdown li {
        color: #000000 !important;
        font-weight: 500 !important;
    }

    /* Sidebar mejorado */
    .sidebar-section {
        margin-bottom: 30px;
        padding: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        color: #000000 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .sidebar-section * {
        color: #000000 !important;
    }

    /* Forzar todo a negro como último recurso dentro del chat */
    .assistant-message [class*="st-emotion"],
    .assistant-message [class*="e1rzn78k"],
    .assistant-message [class*="erovr38"] {
        color: #000000 !important;
    }

    /* Asegurar que elementos específicos dentro del chat sean negros */
    div.stChatMessage.assistant-message * {
        color: #000000 !important;
    }

    /* Override para cualquier clase que Streamlit pueda agregar dentro del chat */
    .assistant-message [class] {
        color: #000000 !important;
    }

    /* Modo oscuro deshabilitado para máximo contraste dentro del chat */
    @media (prefers-color-scheme: dark) {
        .assistant-message,
        .assistant-message * {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
    }

    /* Títulos del chat en blanco */
    .chat-title {
        color: #FFFFFF !important;
    }
    .chat-subtitle {
        color: #FFFFFF !important;
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
    opcion = st.sidebar.selectbox("🖥️ Seleccionar sección", ["Dashboard", "📦 Inventario", "🛒 Productos", "💰 Ventas", "🤖 Chat"])
    
    if opcion == "Dashboard":
        show_dashboard()
    elif opcion == "📦 Inventario":
        show_inventory()
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