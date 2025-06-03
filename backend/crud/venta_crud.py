from sqlalchemy.orm import Session
from backend.models.venta import Venta
from backend.models.producto import Producto
from backend.schemas.venta import VentaCreate


def create_venta(db: Session, venta: VentaCreate):
    producto = db.query(Producto).filter(Producto.id == venta.producto_id).first()
    if not producto or producto.stock_actual < venta.cantidad:
        return None
    total = producto.precio_base * venta.cantidad
    producto.stock_actual -= venta.cantidad
    db_venta = Venta(producto_id=venta.producto_id, cantidad=venta.cantidad, total=total)
    db.add(db_venta)
    db.commit()
    db.refresh(db_venta)
    return db_venta


def get_ventas(db: Session):
    return db.query(Venta).all()
