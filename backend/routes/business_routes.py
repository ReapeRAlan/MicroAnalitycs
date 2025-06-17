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
@router.get("/", response_model=List[BusinessRead])
def read_businesses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    businesses = get_businesses(db, skip=skip, limit=limit)
    return businesses

#Ruta GET para obtener un negocio por su ID
@router.get("/{business_id}", response_model=BusinessRead)
def read_business(business_id: int, db: Session = Depends(get_db)):
    business = get_business(db, business_id=business_id)
    if business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

#Ruta POST para crear un nuevo negocio
@router.post("/", response_model=BusinessRead)
def create_new_business(business: BusinessCreate, db: Session = Depends(get_db)):
    return create_business(db=db, business=business)


# Rutas PUT para actualización completa un negocio existente
@router.put("/business/update/{business_id}", response_model=BusinessRead)
def update_existing_business(
    business_id: int, 
    business: BusinessUpdate, 
    db: Session = Depends(get_db)
):
    db_business = update_business(db=db, business_id=business_id, business=business)
    if db_business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return db_business

# Ruta PATCH para actualización parcial de un negocio existente
@router.patch("/business/partial/update/{business_id}", response_model=BusinessRead)
def partial_update_business(
    business_id: int, 
    business: BusinessUpdate, 
    db: Session = Depends(get_db)
):
    db_business = update_business(db=db, business_id=business_id, business=business)
    if db_business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return db_business


@router.delete("/business/delete/{business_id}", response_model=BusinessRead)
def delete_existing_business(business_id: int, db: Session = Depends(get_db)):
    db_business = delete_business(db=db, business_id=business_id)
    if db_business is None:
        raise HTTPException(status_code=404, detail="Business not found")
    return db_business