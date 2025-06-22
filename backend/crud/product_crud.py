from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload
from backend.models.product import Product
from backend.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductRead,
    ProductWithRelations
)

# Obtiene una lista de negocios con paginación
def get_product(db: Session, product_id: int) -> ProductRead | None:
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    return ProductRead.model_validate(db_product) if db_product else None

# Obtiene un producto con sus relaciones (categoría y negocio)
def get_product_with_relations(db: Session, product_id: int):
    db_product = db.query(Product).\
        options(
            joinedload(Product.categoria),
            joinedload(Product.business)
        ).\
        filter(Product.id == product_id).\
        first()
    
    if not db_product:
        return None
    
    
    product_data = {
        **db_product.__dict__,
        "categoria": db_product.categoria.__dict__ if db_product.categoria else None,
        "business": db_product.business.__dict__ if db_product.business else None
    }
    
    
    product_data.pop('_sa_instance_state', None)
    if product_data['categoria']:
        product_data['categoria'].pop('_sa_instance_state', None)
    if product_data['business']:
        product_data['business'].pop('_sa_instance_state', None)
    
    return ProductWithRelations.model_validate(product_data)

# Obtiene una lista de productos con paginación
def get_products(db: Session, skip: int = 0, limit: int = 100) -> list[ProductRead]:
   
    return [ProductRead.model_validate(p) for p in db.query(Product).offset(skip).limit(limit).all()]

# Crea un nuevo producto en la base de datos y retorna el producto creado
def create_product(db: Session, product: ProductCreate) -> ProductRead:
    
    db_product = Product(**product.model_dump())  
    db.add(db_product)
    db.commit()
    db.refresh(db_product)  
    return ProductRead.model_validate(db_product)

# Actualiza un producto existente (actualización parcial)
def update_product(db: Session, product_id: int, product: ProductUpdate) -> ProductRead | None:

    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return None
    
   
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return ProductRead.model_validate(db_product)

# Elimina un producto por su ID
def delete_product(db: Session, product_id: int) -> ProductRead | None:
    
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if not db_product:
        return None
    
    db.delete(db_product)
    db.commit()
    return ProductRead.model_validate(db_product)