from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.schemas.supplier_schema import (
    SupplierCreate,
    SupplierUpdate,
    SupplierRead
)
from backend.crud.supplier_crud import (
    get_supplier,
    get_suppliers,
    create_supplier,
    update_supplier,
    delete_supplier
)
from backend.base import get_db

router = APIRouter(
    prefix="/suppliers",
    tags=["Suppliers"]
)

#Ruta GET para obtener todos los proveedores
@router.get("/", response_model=List[SupplierRead],
            summary="Obtener todos los proveedores",
            description="Obtiene una lista de todos los proveedores disponibles en la base de datos"
)
def read_suppliers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return get_suppliers(db, skip=skip, limit=limit)

#Ruta GET para obtener un proveedor por su ID
@router.get("/{supplier_id}", response_model=SupplierRead,
            summary="Obtener un proveedor por su ID",
            description="Obtiene los datos de un proveedor específico por su ID")
def read_supplier(supplier_id: int, db: Session = Depends(get_db)):
    
    supplier = get_supplier(db, supplier_id=supplier_id)
    if not supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )
    return supplier

#Ruta POST para crear un nuevo proveedor
@router.post("/new", response_model=SupplierRead,
            summary="Crear un nuevo proveedor",
            description="Crea un nuevo proveedor y lo agrega a la base de datos")
def create_new_supplier(supplier: SupplierCreate, db: Session = Depends(get_db)):
    
    return create_supplier(db=db, supplier=supplier)

# Ruta PUT para actualización completa un proveedor existente
@router.put("/update/{supplier_id}", response_model=SupplierRead,
            summary="Actualizar un proveedor",
            description="Actualiza todos los campos de un proveedor existente")
def update_existing_supplier(
    supplier_id: int,
    supplier: SupplierUpdate,
    db: Session = Depends(get_db)
):
    
    updated_supplier = update_supplier(db, supplier_id=supplier_id, supplier=supplier)
    if not updated_supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )
    return updated_supplier

# Ruta PATCH para actualización parcial de un proveedor existente
@router.patch("/partial/update/{supplier_id}", response_model=SupplierRead,
            summary="Actualizar parcialmente un proveedor",
            description="Actualiza solo los campos especificados de un proveedor existente")
def partial_update_supplier(
    supplier_id: int,
    supplier: SupplierUpdate,
    db: Session = Depends(get_db)
):
    
    updated_supplier = update_supplier(db, supplier_id=supplier_id, supplier=supplier)
    if not updated_supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )
    return updated_supplier

# Ruta DELETE para eliminar un proveedor por su ID
@router.delete("/delete/{supplier_id}", response_model=SupplierRead,
            summary="Eliminar un proveedor",
            description="Elimina un proveedor existente y devuelve sus datos")
def remove_supplier(supplier_id: int, db: Session = Depends(get_db)):
    
    deleted_supplier = delete_supplier(db, supplier_id=supplier_id)
    if not deleted_supplier:
        raise HTTPException(
            status_code=404,
            detail="Supplier not found"
        )
    return deleted_supplier