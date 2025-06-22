from sqlalchemy.orm import Session
from backend.models.category import Category
from backend.schemas.category_schema import (
    CategoryCreate, 
    CategoryUpdate, 
    CategoryRead,
    CategoryWithProducts
)

#Obtiene una categoría por ID
def get_category(db: Session, category_id: int) -> CategoryRead | None:
    db_category = db.query(Category).filter(Category.id == category_id).first()
    return CategoryRead.model_validate(db_category) if db_category else None

#Obtiene una categoría incluyendo sus productos relacionados
def get_category_with_products(db: Session, category_id: int) -> CategoryWithProducts | None:
    db_category = db.query(Category).filter(Category.id == category_id).first()
    return CategoryWithProducts.model_validate(db_category) if db_category else None

#Lista todas las categorías con paginación
def get_categories(db: Session, skip: int = 0, limit: int = 100) -> list[CategoryRead]:
    return [CategoryRead.model_validate(c) for c in db.query(Category).offset(skip).limit(limit).all()]

#Crea una nueva categoría en la base de datos
def create_category(db: Session, category: CategoryCreate) -> CategoryRead:
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return CategoryRead.model_validate(db_category)

#Actualiza una categoría existente
def update_category(db: Session, category_id: int, category: CategoryUpdate) -> CategoryRead | None:
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        return None
    
    update_data = category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return CategoryRead.model_validate(db_category, from_attributes=True)


#Elimina una categoría por su ID
def delete_category(db: Session, category_id: int) -> CategoryRead | None:
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        return None
    
    db.delete(db_category)
    db.commit()
    return CategoryRead.model_validate(db_category)