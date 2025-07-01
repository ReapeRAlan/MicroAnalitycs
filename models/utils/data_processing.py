from typing import Tuple
import pandas as pd
from datetime import datetime, timedelta
from backend.base import SessionLocal
from backend.models.transaction import Transaction
from backend.models.transaction_detail import TransactionDetail
from backend.models.product import Product
from backend.models.inventory import Inventory
from backend.models.category import Category
from backend.models.supplier_price import SupplierPrice

def obtener_datos_enriquecidos(producto_id: int) -> pd.DataFrame:
    """Obtiene features enriquecidos para entrenamiento"""
    db = SessionLocal()
    try:
        # Consultas actualizadas a la base de datos
        transacciones = db.query(TransactionDetail).join(Transaction)\
            .filter(TransactionDetail.product_id == producto_id).all()
        producto = db.query(Product).filter(Product.id == producto_id).first()
        inventario = db.query(Inventory).filter(Inventory.product_id == producto_id).first()
        precios_proveedor = db.query(SupplierPrice)\
            .filter(SupplierPrice.product_id == producto_id).all()
        
        # Crear DataFrame base con nueva estructura
        data = pd.DataFrame([{
            # Features temporales
            'fecha': t.transaccion.fecha,
            'dia_semana': t.transaccion.fecha.weekday(),
            'mes': t.transaccion.fecha.month,
            'temporada': get_temporada(t.transaccion.fecha),
            
            # Features de producto
            'categoria_id': producto.category_id,
            'precio_base': float(producto.precio_base),
            'precio_venta': float(t.precio_unitario),
            
            # Features de ventas
            'cantidad_vendida': t.cantidad,
            'monto_total': float(t.cantidad * t.precio_unitario),
            
            # Features de inventario
            'stock_actual': inventario.stock_actual if inventario else 0,
            'dias_desde_ingreso': get_dias_desde_ingreso(inventario),
            
            # Features de proveedor
            'precio_proveedor_promedio': get_precio_proveedor_promedio(precios_proveedor),
            'margen': get_margen(t.precio_unitario, precios_proveedor),
            
            # Features calculados
            'ventas_7_dias': get_ventas_periodo(transacciones, t.transaccion.fecha, 7),
            'ventas_30_dias': get_ventas_periodo(transacciones, t.transaccion.fecha, 30),
            'variacion_precio': get_variacion_precio(t.precio_unitario, producto.precio_base)
        } for t in transacciones])
        
        return data
    finally:
        db.close()

def get_temporada(fecha: datetime) -> int:
    """Determina la temporada del año (1-4)"""
    return (fecha.month % 12 + 3) // 3

def get_dias_desde_ingreso(inventario: Inventory) -> int:
    """Calcula días desde último ingreso de inventario"""
    if not inventario or not inventario.ultimo_ingreso:
        return 0
    return (datetime.now() - inventario.ultimo_ingreso).days

def get_precio_proveedor_promedio(precios: list[SupplierPrice]) -> float:
    """Calcula precio promedio de proveedores"""
    if not precios:
        return 0.0
    return float(sum(p.precio for p in precios) / len(precios))

def get_margen(precio_venta: float, precios_proveedor: list[SupplierPrice]) -> float:
    """Calcula margen de ganancia"""
    precio_costo = get_precio_proveedor_promedio(precios_proveedor)
    if precio_costo == 0:
        return 0.0
    return (float(precio_venta) - precio_costo) / precio_costo

def get_ventas_periodo(transacciones: list[TransactionDetail], 
                      fecha: datetime, dias: int) -> int:
    """Calcula total de ventas en período anterior"""
    fecha_inicio = fecha - timedelta(days=dias)
    return sum(t.cantidad for t in transacciones 
              if fecha_inicio <= t.transaccion.fecha < fecha)

def get_variacion_precio(precio_actual: float, precio_base: float) -> float:
    """Calcula variación porcentual respecto al precio base"""
    if float(precio_base) == 0:
        return 0.0
    return (float(precio_actual) - float(precio_base)) / float(precio_base)