from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductRead,
    ProductWithRelations
)
from backend.crud.product_crud import (
    get_product,
    get_products,
    create_product,
    update_product,
    delete_product,
    get_product_with_relations
)
from backend.base import get_db


router = APIRouter(
    prefix="/products",  
    tags=["Products"]    
)

# Obtener todos los negocios
@router.get("/", response_model=List[ProductRead],
            summary="Obtener todos los productos",
            description="Obtiene una lista de todos los productos disponibles en la tabla products")
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    
    return get_products(db, skip=skip, limit=limit)

#Ruta GET para obtener un negocio por su ID
@router.get("/{product_id}", response_model=ProductRead,
            summary="Obtener un producto por su ID",
            description="Obtiene los datos de un producto específico por su ID")
def read_product(product_id: int, db: Session = Depends(get_db)):
    
    product = get_product(db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

#Ruta GET para obtener detalles completos de un producto con relaciones
@router.get("/{product_id}/details", response_model=ProductWithRelations,
            summary="Obtener detalles completos de un producto",
            description="Obtiene los detalles completos de un producto, incluyendo relaciones con categoría y negocio",
            responses={
              404: {"description": "Producto no encontrado"},
              200: {"description": "Detalles completos del producto con relaciones"}
          })
def read_product_details(product_id: int, db: Session = Depends(get_db)):
    product = get_product_with_relations(db, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )
    return product

#Ruta POST para crear un nuevo negocio
@router.post("/new", response_model=ProductRead)
def create_new_product(product: ProductCreate, db: Session = Depends(get_db)):
    
    return create_product(db=db, product=product)

# Rutas PUT para actualización completa un negocio existente
@router.put("/update/{product_id}", response_model=ProductRead)
def update_existing_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
 
    updated_product = update_product(db, product_id=product_id, product=product)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

# Ruta PATCH para actualización parcial de un negocio existente
@router.patch("/partial/update/{product_id}", response_model=ProductRead,
    summary="Actualizar parcialmente un negocio",
    description="Actualiza solo los campos especificados de un negocio existente")
def partial_update_product(
    product_id: int, 
    product: ProductUpdate, 
    db: Session = Depends(get_db)
):
    updated_product = update_product(db, product_id=product_id, product=product)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

# Ruta DELETE para eliminar un producto por su ID
@router.delete("/{product_id}", response_model=ProductRead)
def remove_product(product_id: int, db: Session = Depends(get_db)):

    deleted_product = delete_product(db, product_id=product_id)
    if not deleted_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return deleted_product