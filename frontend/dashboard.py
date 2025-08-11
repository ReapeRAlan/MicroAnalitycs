import streamlit as st
import pandas as pd
import plotly.express as px
from api_utils import get_products
from sales import get_sales

def show_dashboard():
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
    ventas = get_sales()
    if ventas:
        df_ventas = pd.DataFrame(ventas)
        st.subheader("Listado de Ventas")
        st.dataframe(df_ventas, use_container_width=True)
        st.subheader("Gráfico de Ventas por Producto")
        df_ventas["Total_Value"] = df_ventas["Total"].apply(lambda x: float(x.replace("$", "")))
        fig_ventas = px.bar(df_ventas, x="Producto", y="Total_Value", title="Total de Ventas por Producto",
                            color="Total_Value", color_continuous_scale="Viridis",
                            labels={"Total_Value": "Total ($)", "Producto": "Producto"})
        st.plotly_chart(fig_ventas, use_container_width=True)
    else:
        st.info("No hay ventas disponibles.")