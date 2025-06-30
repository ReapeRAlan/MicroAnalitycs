import streamlit as st
from products import get_products  # Importar funciones existentes

def show_sales():
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