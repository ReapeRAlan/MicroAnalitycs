from sqlalchemy.orm import Session, joinedload
from typing import Optional
from backend.models.supplier_price import SupplierPrice
from backend.schemas.supplier_price_schema import (
    SupplierPriceCreate,
    SupplierPriceRead,
    SupplierPriceUpdate,
    SupplierPriceWithRelations
)

#Busca un precio de proveedor por su ID en la base de datos
def get_supplier_price(db: Session, price_id: int) -> Optional[SupplierPriceRead]:
    db_price = db.query(SupplierPrice).filter(SupplierPrice.id == price_id).first()
    return SupplierPriceRead.model_validate(db_price) if db_price else None

# Obtiene un precio de proveedor con relaciones cargadas
def get_supplier_price_with_relations(db: Session, price_id: int) -> Optional[SupplierPriceWithRelations]:
    db_price = (
        db.query(SupplierPrice)
        .options(
            joinedload(SupplierPrice.producto),
            joinedload(SupplierPrice.proveedor)
        )
        .filter(SupplierPrice.id == price_id)
        .first()
    )
    
    if not db_price:
        return None
    
    price_data = {
        **db_price.__dict__,
        "producto": {
            "id": db_price.producto.id,
            "nombre": db_price.producto.nombre
        } if db_price.producto else None,
        "proveedor": {
            "id": db_price.proveedor.id,
            "nombre": db_price.proveedor.nombre
        } if db_price.proveedor else None
    }
    
    price_data.pop('_sa_instance_state', None)
    if price_data['producto']:
        price_data['producto'].pop('_sa_instance_state', None)
    if price_data['proveedor']:
        price_data['proveedor'].pop('_sa_instance_state', None)
    
    return SupplierPriceWithRelations.model_validate(price_data)

# Obtiene una lista de precios de proveedores con paginación y filtros opcionales
def get_supplier_prices(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    supplier_id: Optional[int] = None
) -> list[SupplierPriceRead]:
    query = db.query(SupplierPrice)
    
    if product_id:
        query = query.filter(SupplierPrice.product_id == product_id)
    if supplier_id:
        query = query.filter(SupplierPrice.supplier_id == supplier_id)
        
    return [
        SupplierPriceRead.model_validate(p)
        for p in query.offset(skip).limit(limit).all()
    ]

# Crea un nuevo precio de proveedor en la base de datos
def create_supplier_price(db: Session, price: SupplierPriceCreate) -> SupplierPriceRead:
    db_price = SupplierPrice(**price.model_dump())
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return SupplierPriceRead.model_validate(db_price)

# Actualiza un precio de proveedor existente en la base de datos
def update_supplier_price(
    db: Session,
    price_id: int,
    price: SupplierPriceUpdate
) -> Optional[SupplierPriceRead]:
    db_price = db.query(SupplierPrice).filter(SupplierPrice.id == price_id).first()
    if not db_price:
        return None
    
    update_data = price.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_price, field, value)
    
    db.commit()
    db.refresh(db_price)
    return SupplierPriceRead.model_validate(db_price)

# Elimina un precio de proveedor por su ID
def delete_supplier_price(db: Session, price_id: int) -> Optional[SupplierPriceRead]:
    db_price = db.query(SupplierPrice).filter(SupplierPrice.id == price_id).first()
    if not db_price:
        return None
    
    db.delete(db_price)
    db.commit()
    return SupplierPriceRead.model_validate(db_price)

# Obtiene todos los precios de proveedores con relaciones cargadas y paginación
# En backend/crud/supplier_price_crud.py
def get_all_supplier_prices_with_relations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    supplier_id: Optional[int] = None
) -> list[SupplierPriceWithRelations]:
    query = (
        db.query(SupplierPrice)
        .options(
            joinedload(SupplierPrice.producto),
            joinedload(SupplierPrice.proveedor)
        )
    )
    
    if product_id:
        query = query.filter(SupplierPrice.product_id == product_id)
    if supplier_id:
        query = query.filter(SupplierPrice.supplier_id == supplier_id)
        
    db_prices = query.offset(skip).limit(limit).all()
    
    prices_list = []
    for db_price in db_prices:
        price_data = {
            **db_price.__dict__,
            "producto": {
                "id": db_price.producto.id,
                "nombre": db_price.producto.nombre
            } if db_price.producto else None,
            "proveedor": {
                "id": db_price.proveedor.id,
                "nombre": db_price.proveedor.nombre
            } if db_price.proveedor else None
        }
        price_data.pop('_sa_instance_state', None)
        prices_list.append(SupplierPriceWithRelations.model_validate(price_data))
    
    return prices_list