import requests
import streamlit as st
import pandas as pd

API_URL = "http://localhost:8000"

st.sidebar.title("MicroAnalitycs")
page = st.sidebar.selectbox("Ir a", ["Ver inventario", "Registrar venta", "Chatbot IA"])

if page == "Ver inventario":
    st.header("Inventario")
    resp = requests.get(f"{API_URL}/inventario/")
    if resp.ok:
        df = pd.DataFrame(resp.json())
        st.dataframe(df)
    else:
        st.error("No se pudo cargar el inventario")

elif page == "Registrar venta":
    st.header("Registrar venta")
    productos = requests.get(f"{API_URL}/productos/").json()
    prod_map = {p['nombre']: p['id'] for p in productos}
    nombre = st.selectbox("Producto", list(prod_map.keys()))
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    if st.button("Registrar"):
        resp = requests.post(f"{API_URL}/ventas/", json={"producto_id": prod_map[nombre], "cantidad": int(cantidad)})
        if resp.ok:
            st.success(str(resp.json()))
        else:
            st.error(resp.json().get("detail"))

elif page == "Chatbot IA":
    st.header("Chatbot")
    msg = st.text_input("Escribe tu pregunta")
    if st.button("Enviar"):
        resp = requests.post(f"{API_URL}/chatbot/", params={"mensaje": msg})
        if resp.ok:
            st.write(resp.json()["respuesta"])
        else:
            st.error("Error en chatbot")
