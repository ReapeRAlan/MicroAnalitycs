from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.schemas.inventory_schema import (
    InventoryCreate,
    InventoryUpdate,
    InventoryRead
)
from backend.crud.inventory_crud import (
    get_inventory,
    get_all_inventory,
    create_inventory,
    update_inventory,
    delete_inventory,
    get_inventory_by_product
)
from backend.base import get_db

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"])

@router.get("/", response_model=List[InventoryRead],
            summary="Obtener todos los registros de inventario",
            description="Obtiene una lista de todos los registros de inventario con paginación y filtrado opcional" )
def read_inventory(
    skip: int = 0,
    limit: int = 100,
    min_stock: Optional[int] = Query(
        None, 
        description="Filtrar por stock mínimo"
    ),
    db: Session = Depends(get_db)
):
    
    return get_all_inventory(db, skip=skip, limit=limit, min_stock=min_stock)


# Ruta GET para obtener un registro de inventario por ID
@router.get("/{inventory_id}", response_model=InventoryRead,
            summary="Obtener un registro de inventario por ID",
            description="Obtiene un registro de inventario específico por su ID")
def read_single_inventory(inventory_id: int, db: Session = Depends(get_db)):
    
    inventory = get_inventory(db, inventory_id=inventory_id)
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )
    return inventory

# Ruta GET para obtener el inventario de un producto específico
@router.get("/product/{product_id}", response_model=InventoryRead,
            summary="Obtener inventario por ID de producto",
            description="Obtiene el registro de inventario asociado a un producto específico por su ID")
def read_inventory_for_product(product_id: int, db: Session = Depends(get_db)):
    inventory = get_inventory_by_product(db, product_id=product_id)
    if not inventory:
        raise HTTPException(
            status_code=404,
            detail="inventory record not found for the specified product"
        )
    return inventory


# Ruta POST para crear un nuevo registro de inventario
@router.post("/new", response_model=InventoryRead,
            summary="Crear un nuevo registro de inventario",
            description="Crea un nuevo registro de inventario en la base de datos y retorna el registro creado")
def create_new_inventory(
    inventory: InventoryCreate, 
    db: Session = Depends(get_db)
):
    return create_inventory(db=db, inventory=inventory)


# Ruta PUT para actualizar un registro de inventario existente
@router.put("/update/{inventory_id}", response_model=InventoryRead,
            summary="Actualizar un registro de inventario existente",
            description="Actualiza todos los campos de un registro de inventario existente, reemplazando los valores actuales")
def update_existing_inventory(
    inventory_id: int,
    inventory: InventoryUpdate,
    db: Session = Depends(get_db)
):
 
    updated_inventory = update_inventory(
        db, 
        inventory_id=inventory_id, 
        inventory=inventory
    )
    if not updated_inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )
    return updated_inventory


# Ruta PATCH para actualizar parcialmente un registro de inventario existente
@router.patch("/partial/update/{inventory_id}", response_model=InventoryRead,
              summary="Actualizar parcialmente un registro de inventario",
              description="Actualiza solo los campos especificados de un registro de inventario existente"
)
def partial_update_inventory(
    inventory_id: int,
    inventory: InventoryUpdate,
    db: Session = Depends(get_db)
):
    updated_inventory = update_inventory(
        db, 
        inventory_id=inventory_id, 
        inventory=inventory
    )
    if not updated_inventory:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )
    return updated_inventory


# Ruta DELETE para eliminar un registro de inventario por su ID
@router.delete("/delete/{inventory_id}", 
              response_model=dict,
              summary="Eliminar un registro de inventario",
              description="Elimina un registro de inventario y devuelve información básica del registro eliminado",
             )
def remove_inventory(inventory_id: int, db: Session = Depends(get_db)):
    deleted_data = delete_inventory(db, inventory_id=inventory_id)
    if not deleted_data:
        raise HTTPException(
            status_code=404,
            detail="Inventory record not found"
        )
    return deleted_data