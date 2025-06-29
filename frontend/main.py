import streamlit as st
from app import show_select_business
from dashboard import show_dashboard
from products import show_products
from sales import show_sales
from chatbot_app_working import ChatbotFrontend

# Configuración inicial (primer comando)
st.set_page_config(page_title="MicroAnalytics POS & Chat", layout="wide")

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