from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryRead,
)
from backend.crud.category_crud import (
    get_category,
    get_categories,
    create_category,
    update_category,
    delete_category,
)
from backend.base import get_db


router = APIRouter(
    prefix="/categories",  # Prefijo base para todas las rutas
    tags=["Categories"]   # Grupo en la documentación Swagger/OpenAPI
)

#ruta GET Lista de categorías (paginada)
@router.get("/", response_model=List[CategoryRead],
           summary="Lista todas las categorías",
           description="Obtiene una lista paginada de todas las categorías existentes")
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
   
    return get_categories(db, skip=skip, limit=limit)


#ruta GET, Detalles de una Categoría por ID
@router.get("/{category_id}", response_model=CategoryRead,
           summary="Obtiene una categoría específica",
           description="Recupera los detalles de una categoría por su ID")
def read_category(category_id: int, db: Session = Depends(get_db)):
    category = get_category(db, category_id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

    
# Ruta POST para crear una nueva categoría
@router.post("/new", response_model=CategoryRead,
            status_code=201,
            summary="Crea una nueva categoría",
            description="Registra una nueva categoría en el sistema")
def create_new_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db=db, category=category)

# Ruta PUT para actualizar una categoría existente
@router.put("/update/{category_id}", response_model=CategoryRead,
           summary="Actualiza una categoría completamente",
           description="Reemplaza todos los campos de una categoría existente")
def update_existing_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):

    updated_category = update_category(db, category_id=category_id, category=category)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category

# Ruta PATCH para actualizar parcialmente una categoría existente
@router.patch("/partial/update/{category_id}", response_model=CategoryRead,
             summary="Actualización parcial de categoría",
             description="Actualiza solo los campos especificados de una categoría")
def partial_update_category(
    category_id: int, 
    category: CategoryUpdate, 
    db: Session = Depends(get_db)
):
    updated_category = update_category(db, category_id=category_id, category=category)
    if updated_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category


# Ruta DELETE para eliminar una categoría por su ID
@router.delete("/delete/{category_id}", response_model=CategoryRead,
              summary="Elimina una categoría",
              description="Borra una categoría existente y devuelve sus datos")
def remove_category(category_id: int, db: Session = Depends(get_db)):
    deleted_category = delete_category(db, category_id=category_id)
    if not deleted_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return deleted_category