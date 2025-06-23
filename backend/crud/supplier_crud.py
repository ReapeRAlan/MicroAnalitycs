from sqlalchemy.orm import Session
from backend.models.supplier import Supplier
from backend.schemas.supplier_schema import (
    SupplierCreate,
    SupplierUpdate,
    SupplierRead,
    
)

# Busca un proveedor por su ID en la base de datos
def get_supplier(db: Session, supplier_id: int) -> SupplierRead | None:
    
    db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    return SupplierRead.model_validate(db_supplier, from_attributes=True) if db_supplier else None


# Obtiene una lista de proveedores con paginación 
def get_suppliers(
    db: Session, 
    skip: int = 0, 
    limit: int = 100
) -> list[SupplierRead]:
    supplers = db.query(Supplier).offset(skip).limit(limit).all()
    return [SupplierRead.model_validate(b, from_attributes=True) for b in supplers]

# Crea un nuevo proveedor en la base de datos y retorna el proveedor creado
def create_supplier(db: Session, supplier: SupplierCreate) -> SupplierRead:
    db_supplier = Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return SupplierRead.model_validate(db_supplier, from_attributes=True)

# Actualiza un proveedor existente 
def update_supplier(
    db: Session, 
    supplier_id: int, 
    supplier: SupplierUpdate
) -> SupplierRead | None:
    db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not db_supplier:
        return None
    
    update_data = supplier.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_supplier, field, value)
    
    db.commit()
    db.refresh(db_supplier)
    return SupplierRead.model_validate(db_supplier, from_attributes=True)

# Elimina un proveedor por su ID 
def delete_supplier(db: Session, supplier_id: int) -> SupplierRead | None:
    
    db_supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not db_supplier:
        return None
    
    db.delete(db_supplier)
    db.commit()
    return SupplierRead.model_validate(db_supplier, from_attributes=True)