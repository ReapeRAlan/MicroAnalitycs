from sqlalchemy.orm import Session
from backend.models.business_model import Business
from backend.schemas.business_schema import BusinessCreate, BusinessUpdate, BusinessRead

# Busca un negocio por su ID en la base de datos
def get_business(db: Session, business_id: int) -> BusinessRead | None:
    db_business = db.query(Business).filter(Business.id == business_id).first()
    return BusinessRead.model_validate(db_business, from_attributes=True) if db_business else None

# Obtiene una lista de negocios con paginación
def get_businesses(db: Session, skip: int = 0, limit: int = 100) -> list[BusinessRead]:
    businesses = db.query(Business).offset(skip).limit(limit).all()
    return [BusinessRead.model_validate(b, from_attributes=True) for b in businesses]

# Crea un nuevo negocio en la base de datos y retorna el negocio creado
def create_business(db: Session, business: BusinessCreate) -> BusinessRead:
    db_business = Business(
        nombre=business.nombre,
        descripcion=business.descripcion
    )
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return BusinessRead.model_validate(db_business, from_attributes=True)

# Actualiza un negocio existente
def update_business(db: Session, business_id: int, business: BusinessUpdate) -> BusinessRead | None:
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        return None

    update_data = business.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_business, field, value)

    db.commit()
    db.refresh(db_business)
    return BusinessRead.model_validate(db_business, from_attributes=True)

# Elimina un negocio por su ID
def delete_business(db: Session, business_id: int) -> BusinessRead | None:
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        return None

    db.delete(db_business)
    db.commit()
    return BusinessRead.model_validate(db_business, from_attributes=True)
    