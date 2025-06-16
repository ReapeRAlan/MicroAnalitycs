from sqlalchemy.orm import Session
from backend.models.business_model import Business
from backend.schemas.business_schema import BusinessCreate, BusinessUpdate

#Busca un negocio por su ID en la base de datos
def get_business(db: Session, business_id: int):
    return db.query(Business).filter(Business.id == business_id).first()

# Obtiene una lista de negocios con paginación
def get_businesses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Business).offset(skip).limit(limit).all()

# Crea un nuevo negocio en la base de datos y retorna el negocio creado
def create_business(db: Session, business: BusinessCreate):
    db_business = Business(
        nombre=business.nombre,
        descripcion=business.descripcion
    )
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return db_business

#Actualiza un negocio
def update_business(db: Session, business_id: int, business: BusinessUpdate):
    db_business = get_business(db, business_id)
    if not db_business:
        return None
    
    update_data = business.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_business, field, value)
    
    db.commit()
    db.refresh(db_business)
    return db_business

# Elimina un negocio por su ID
def delete_business(db: Session, business_id: int):
    db_business = get_business(db, business_id)
    if not db_business:
        return None
    
    db.delete(db_business)
    db.commit()
    return db_business