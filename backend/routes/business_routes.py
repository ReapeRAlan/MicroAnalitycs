from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.crud.business_crud import (
    get_business,
    get_businesses,
    create_business,
    update_business,
    delete_business
)
from backend.schemas.business_schema import (
    BusinessCreate,
    BusinessRead,
    BusinessUpdate
)
from backend.base import get_db

router = APIRouter(
    prefix="/business",
    tags=["business"]
)

# Obtener todos los negocios
@router.get("/", response_model=List[BusinessRead],
    summary="Obtener todos los negocios",
    description="Obtiene una lista de todos los negocios disponibles en la tabla business")
def read_businesses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    businesses = get_businesses(db, skip=skip, limit=limit)
    return businesses

#Ruta GET para obtener un negocio por su ID
@router.get("/{business_id}", response_model=BusinessRead,
    summary="Obtener un negocio por su ID",
    description="Obtiene los datos de un negocio específico por su ID")
def read_business(business_id: int, db: Session = Depends(get_db)):
    business = get_business(db, business_id=business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

#Ruta POST para crear un nuevo negocio
@router.post("/", response_model=BusinessRead,
    summary="Crear un nuevo negocio",
    description="Crea un nuevo negocio y lo agrega a la tabla business")
def create_new_business(business: BusinessCreate, db: Session = Depends(get_db)):
    return create_business(db=db, business=business)


# Rutas PUT para actualización completa un negocio existente
@router.put("/{business_id}", response_model=BusinessRead,
    summary="Actualizar un negocio",
    description="Actualiza todos los campos de un negocio existente")
def update_existing_business(
    business_id: int, 
    business: BusinessUpdate, 
    db: Session = Depends(get_db)
):
    updated_business = update_business(db, business_id=business_id, business=business)
    if updated_business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return updated_business

# Ruta PATCH para actualización parcial de un negocio existente
@router.patch("/{business_id}", response_model=BusinessRead,
    summary="Actualizar parcialmente un negocio",
    description="Actualiza solo los campos especificados de un negocio existente")
def partial_update_business(
    business_id: int, 
    business: BusinessUpdate, 
    db: Session = Depends(get_db)
):
    updated_business = update_business(db, business_id=business_id, business=business)
    if updated_business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return updated_business


@router.delete("/{business_id}", response_model=BusinessRead,
    summary="Eliminar un negocio",
    description="Elimina un negocio existente y devuelve sus datos")
def remove_business(business_id: int, db: Session = Depends(get_db)):
    deleted_business = delete_business(db, business_id=business_id)
    if deleted_business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return deleted_business