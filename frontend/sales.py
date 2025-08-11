import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import random
from inventory import fetch_inventory, update_inventory
from api_utils import get_products

@st.cache_data
def get_products_from_api():
    API_BASE_URL = "http://localhost:8000/api"
    try:
        timestamp = datetime.now().timestamp()
        response = requests.get(f"{API_BASE_URL}/products/?skip=0&limit=1000&t={timestamp}")
        response.raise_for_status()
        products = response.json()
        if st.session_state.business_id:
            filtered_products = [p for p in products if p.get("business_id") == st.session_state.business_id]
            return filtered_products
        return products
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener productos: {str(e)}")
        return []

def get_inventory_for_product(product_id):
    inventory = fetch_inventory()
    return next((item for item in inventory if item.get("product_id") == product_id), None)

def get_sales():
    """Devuelve la lista de ventas almacenada en st.session_state."""
    return st.session_state.get("ventas_simuladas", [])

def show_sales():
    st.title(f"Sales Management - Negocio {st.session_state.business_id}")
    
    productos = get_products_from_api()
    if not productos:
        productos = [
            {"id": 1, "nombre": "Camiseta Básica", "precio_base": 15.99, "business_id": st.session_state.business_id or "Negocio001"},
            {"id": 2, "nombre": "Smartphone X10", "precio_base": 299.99, "business_id": st.session_state.business_id or "Negocio001"},
            {"id": 3, "nombre": "Zapatillas Deportivas", "precio_base": 49.99, "business_id": st.session_state.business_id or "Negocio001"},
            {"id": 4, "nombre": "Auriculares Bluetooth", "precio_base": 29.99, "business_id": st.session_state.business_id or "Negocio001"},
        ]

    inventario = fetch_inventory()
    for producto in productos:
        inv = get_inventory_for_product(producto["id"])
        if inv:
            producto["stock_actual"] = inv["stock_actual"]
        else:
            producto["stock_actual"] = random.randint(1, 10)

    tab1, tab2 = st.tabs(["💸 Agregar", "📊 Mostrar"])
    
    with tab1:
        st.header("Registrar Venta")
        if productos:
            with st.form("form_registrar_venta"):
                producto_id = st.selectbox("Seleccionar un producto", 
                                          [(p["id"], p["nombre"]) for p in productos], 
                                          format_func=lambda x: x[1])
                cantidad = st.number_input("Cantidad", min_value=1, step=1)
                producto_seleccionado = next(p for p in productos if p["id"] == producto_id[0])
                stock_actual = producto_seleccionado.get("stock_actual", 0)
                st.write(f"Stock disponible: {stock_actual}")
                if st.form_submit_button("Registrar"):
                    if cantidad > 0:
                        if stock_actual >= cantidad:
                            precio = producto_seleccionado.get("precio_base", producto_seleccionado.get("precio", 0.0))
                            total = cantidad * precio
                            nueva_venta = {
                                "Producto": producto_seleccionado["nombre"],
                                "Cantidad": cantidad,
                                "Precio Unitario": f"${precio:.2f}",
                                "Total": f"${total:.2f}",
                                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
                            }
                            st.session_state.ventas_simuladas.append(nueva_venta)
                            inv = get_inventory_for_product(producto_id[0])
                            if inv:
                                nuevo_stock = inv["stock_actual"] - cantidad
                                if update_inventory(inv["id"], nuevo_stock):
                                    producto_seleccionado["stock_actual"] = nuevo_stock
                                    st.success("Venta registrada y stock actualizado exitosamente")
                                else:
                                    st.error("Venta registrada, pero no se pudo actualizar el stock.")
                            else:
                                st.error("No se encontró un registro de inventario para este producto.")
                        else:
                            st.error(f"No hay suficiente stock. Disponible: {stock_actual}")
                    else:
                        st.error("La cantidad debe ser mayor a 0")
        else:
            st.info("No hay productos disponibles para registrar ventas.")
    
    with tab2:
        st.header("Lista de Ventas")
        ventas = st.session_state.ventas_simuladas
        if ventas:
            df_ventas = pd.DataFrame(ventas)
            st.dataframe(df_ventas, use_container_width=True)
            st.subheader("Total de Ventas por Producto")
            try:
                df_ventas["Total_Value"] = df_ventas["Total"].apply(lambda x: float(x.replace("$", "")))
                totales = df_ventas.groupby("Producto")["Total_Value"].sum()
                st.bar_chart(totales)
            except Exception as e:
                st.error(f"Error al generar el gráfico: {e}")
        else:
            st.info("No hay ventas disponibles.")

if "business_id" not in st.session_state:
    st.session_state.business_id = "Negocio001"

if __name__ == "__main__":
    show_sales()