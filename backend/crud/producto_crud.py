from sqlalchemy.orm import Session
from backend.models.producto import Producto
from backend.schemas.producto import ProductoCreate


def get_productos(db: Session):
    return db.query(Producto).all()


def get_producto(db: Session, producto_id: int):
    return db.query(Producto).filter(Producto.id == producto_id).first()


def create_producto(db: Session, producto: ProductoCreate):
    db_obj = Producto(**producto.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_producto(db: Session, producto_id: int, data: ProductoCreate):
    db_obj = get_producto(db, producto_id)
    if not db_obj:
        return None
    for field, value in data.dict().items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_producto(db: Session, producto_id: int):
    db_obj = get_producto(db, producto_id)
    if not db_obj:
        return None
    db.delete(db_obj)
    db.commit()
    return db_obj
