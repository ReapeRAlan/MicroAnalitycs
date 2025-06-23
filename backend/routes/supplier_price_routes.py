from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.schemas.supplier_price_schema import (
    SupplierPriceCreate,
    SupplierPriceRead,
    SupplierPriceUpdate,
    SupplierPriceWithRelations
)
from backend.crud.supplier_price_crud import (
    get_supplier_price,
    get_supplier_price_with_relations,
    get_supplier_prices,
    create_supplier_price,
    update_supplier_price,
    delete_supplier_price
)
from backend.base import get_db

router = APIRouter(
    prefix="/supplier-prices",
    tags=["Supplier Prices"]
)

# Obtener todos los precios de proveedores
@router.get("/", response_model=List[SupplierPriceRead],
           summary="Listar precios de proveedores",
           description="Obtiene una lista paginada de precios de proveedores")
def read_prices(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    supplier_id: Optional[int] = Query(None, description="Filtrar por ID de proveedor"),
    db: Session = Depends(get_db)
):
    return get_supplier_prices(
        db,
        skip=skip,
        limit=limit,
        product_id=product_id,
        supplier_id=supplier_id
    )

#ruta GET para obtener un precio por su ID
@router.get("/{price_id}", response_model=SupplierPriceRead,
           summary="Obtener precio por ID",
           description="Obtiene los detalles básicos de un precio de proveedor")
def read_price(price_id: int, db: Session = Depends(get_db)):
    price = get_supplier_price(db, price_id=price_id)
    if not price:
        raise HTTPException(status_code=404, detail="Supplier price not found")
    return price

# Ruta GET para obtener detalles completos de un precio con relaciones
@router.get("/{price_id}/details", response_model=SupplierPriceWithRelations,
           summary="Obtener detalles completos del precio",
           description="Obtiene los detalles completos de un precio de proveedor incluyendo información relacionada")
def read_price_details(price_id: int, db: Session = Depends(get_db)):
    price = get_supplier_price_with_relations(db, price_id=price_id)
    if not price:
        raise HTTPException(status_code=404, detail="Supplier price not found")
    return price

# Ruta POST para crear un nuevo precio de proveedor
@router.post("/", response_model=SupplierPriceRead, status_code=201,
            summary="Crear nuevo precio",
            description="Registra un nuevo precio de proveedor para un producto")
def create_price(price: SupplierPriceCreate, db: Session = Depends(get_db)):
    return create_supplier_price(db=db, price=price)

# Ruta PUT para actualizar un precio de proveedor existente
@router.put("/{price_id}", response_model=SupplierPriceRead,
           summary="Actualizar precio",
           description="Actualiza los datos de un precio de proveedor")
def update_price(
    price_id: int,
    price: SupplierPriceUpdate,
    db: Session = Depends(get_db)
):
    updated_price = update_supplier_price(db, price_id=price_id, price=price)
    if not updated_price:
        raise HTTPException(status_code=404, detail="Supplier price not found")
    return updated_price

# Ruta DELETE para eliminar un precio de proveedor
@router.delete("/{price_id}", response_model=SupplierPriceRead,
              summary="Eliminar precio",
              description="Elimina un registro de precio de proveedor")
def delete_price(price_id: int, db: Session = Depends(get_db)):
    deleted_price = delete_supplier_price(db, price_id=price_id)
    if not deleted_price:
        raise HTTPException(status_code=404, detail="Supplier price not found")
    return deleted_price