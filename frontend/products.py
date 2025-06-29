import streamlit as st
import pandas as pd
import time
from app import get_products, get_product, create_product, update_product, delete_product  # Importar funciones existentes

def show_products():
    st.title(f"Product Management - Negocio {st.session_state.business_id}")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛍️ Agregar", "✏️ Actualizar", "🗑️ Eliminar", "📋 Listar", "🔍 Buscar por ID"])
    
    with tab1:
        st.header("Agregar Producto")
        with st.form("form_crear_producto"):
            nombre = st.text_input("Nombre del producto")
            descripcion = st.text_area("Descripción")
            precio_base = st.number_input("Precio base", min_value=0.0, step=0.01)
            category_id = st.number_input("ID de Categoría", min_value=1, step=1)
            business_id = st.session_state.business_id
            if st.form_submit_button("Crear"):
                if nombre and precio_base >= 0 and category_id and business_id:
                    new_product = create_product(nombre, descripcion, precio_base, category_id, business_id)
                    if new_product:
                        st.success(f"Producto creado exitosamente: {nombre}")
                        get_products(force_refresh=True)
                        time.sleep(4)
                        st.rerun()
                    else:
                        st.error("Error al crear el producto a pesar de 200 OK, revisa la terminal.")
                else:
                    st.error("Por favor, completa todos los campos correctamente")
    
    with tab2:
        st.header("Actualizar Producto")
        productos = get_products()
        if productos:
            producto_id = st.selectbox("Seleccionar un producto", 
                                      [(p["id"], p["nombre"]) for p in productos], 
                                      format_func=lambda x: x[1], key="update_select")
            producto = get_product(producto_id[0]) if producto_id else None
            with st.form("form_actualizar_producto"):
                nombre_update = st.text_input("Nuevo nombre", value=producto["nombre"] if producto else "")
                descripcion_update = st.text_area("Nueva descripción", value=producto["descripcion"] if producto else "")
                precio_base_update = st.number_input("Nuevo precio base", min_value=0.0, step=0.01, value=producto["precio_base"] if producto else 0.0)
                category_id_update = st.number_input("Nuevo ID de Categoría", min_value=1, step=1, value=producto["category_id"] if producto else 1)
                business_id_update = st.session_state.business_id
                if st.form_submit_button("Actualizar"):
                    if nombre_update and precio_base_update >= 0 and category_id_update and business_id_update:
                        updated_product = update_product(producto_id[0], nombre_update, descripcion_update, precio_base_update, category_id_update, business_id_update)
                        if updated_product:
                            st.success(f"Producto actualizado exitosamente: {nombre_update}")
                            st.rerun()
                        else:
                            st.error("Error al actualizar el producto.")
                    else:
                        st.error("Por favor, completa todos los campos correctamente")
        else:
            st.warning("No hay productos disponibles para actualizar.")
    
    with tab3:
        st.header("Eliminar Producto")
        productos = get_products()
        if productos:
            producto_id_delete = st.selectbox("Seleccionar un producto para eliminar", 
                                            [(p["id"], p["nombre"]) for p in productos], 
                                            format_func=lambda x: x[1], key="delete_select")
            if st.button("Eliminar"):
                deleted_product = delete_product(producto_id_delete[0])
                if deleted_product:
                    st.success(f"Producto eliminado exitosamente: {producto_id_delete[1]}")
                    st.rerun()
                else:
                    st.error("Error al eliminar el producto.")
        else:
            st.warning("No hay productos disponibles para eliminar.")
    
    with tab4:
        st.header("Lista de Productos")
        if st.button("Refresh"):
            st.rerun()
        productos = get_products()
        if productos:
            df_productos = pd.DataFrame(productos)
            st.dataframe(df_productos, use_container_width=True)
        else:
            st.info("No hay productos disponibles.")
    
    with tab5:
        st.header("Buscar Producto por ID")
        product_id = st.number_input("Ingrese el ID del producto", min_value=1, step=1)
        if st.button("Buscar"):
            product = get_product(product_id)
            if product:
                st.write("Detalles del producto:")
                df_product = pd.DataFrame([product])
                st.table(df_product)
            else:
                st.error("Producto no encontrado.")