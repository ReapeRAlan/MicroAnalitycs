from typing import Optional
from sqlalchemy.sql import func
from sqlalchemy.orm import Session, joinedload
from backend.models.inventory import Inventory
from backend.schemas.inventory_schema import (
    InventoryCreate,
    InventoryUpdate,
    InventoryRead
)

# Obtiene un registro de inventario por ID
def get_inventory(db: Session, inventory_id: int) -> InventoryRead | None:
    
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    return InventoryRead.model_validate(db_inventory) if db_inventory else None

# Obtiene el inventario de un producto específico
def get_inventory_by_product(db: Session, product_id: int) -> InventoryRead | None:
    db_inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    return InventoryRead.model_validate(db_inventory) if db_inventory else None

# Obtiene una lista de registros de inventario con paginación y filtrado opcional
def get_all_inventory(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    min_stock: Optional[int] = None
) -> list[InventoryRead]:
    query = db.query(Inventory).options(joinedload(Inventory.producto))
    
    if min_stock is not None:
        query = query.filter(Inventory.stock_actual >= min_stock)
        
    return [
        InventoryRead.model_validate(inv) 
        for inv in query.offset(skip).limit(limit).all()
    ]

# Crea un nuevo registro de inventario
def create_inventory(db: Session, inventory: InventoryCreate) -> InventoryRead:
    
    db_inventory = Inventory(**inventory.model_dump())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return InventoryRead.model_validate(db_inventory)

# Actualiza un registro de inventario existente
def update_inventory(
    db: Session, 
    inventory_id: int, 
    inventory: InventoryUpdate
) -> InventoryRead | None:
    """Actualiza un registro de inventario"""
    db_inventory = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not db_inventory:
        return None
    
    update_data = inventory.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_inventory, field, value)
    
    # Actualiza automáticamente la fecha
    db_inventory.ultimo_ingreso = func.now()
    
    db.commit()
    db.refresh(db_inventory)
    return InventoryRead.model_validate(db_inventory)

# Elimina un registro de inventario por su ID
def delete_inventory(db: Session, inventory_id: int) -> dict:
    """Elimina un registro de inventario y retorna un diccionario con los datos básicos"""
    # Cargamos el inventario con la relación producto usando joinedload
    db_inventory = (
        db.query(Inventory)
        .options(joinedload(Inventory.producto))
        .filter(Inventory.id == inventory_id)
        .first()
    )
    
    if not db_inventory:
        return None
    
    # Preparamos los datos antes de eliminar
    result = {
        "id": db_inventory.id,
        "product_id": db_inventory.product_id,
        "stock_actual": db_inventory.stock_actual,
        "ultimo_ingreso": db_inventory.ultimo_ingreso.isoformat() if db_inventory.ultimo_ingreso else None
    }
    
    # Si el producto está cargado, añadimos su nombre
    if db_inventory.producto:
        result["product_name"] = db_inventory.producto.nombre
    
    db.delete(db_inventory)
    db.commit()
    
    return result