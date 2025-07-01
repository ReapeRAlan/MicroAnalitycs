from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from backend.models.transaction_detail import TransactionDetail
from backend.schemas.transaction_detail_schema import (
    TransactionDetailCreate,
    TransactionDetailRead,
    TransactionDetailUpdate,
    TransactionDetailWithRelations
)

#obtiene un detalle de transacción por ID
def get_transaction_detail(db: Session, detail_id: int) -> Optional[TransactionDetailRead]:
    db_detail = db.query(TransactionDetail).filter(TransactionDetail.id == detail_id).first()
    return TransactionDetailRead.model_validate(db_detail) if db_detail else None

#Obtiene un detalle de transacción con relaciones (producto y transacción)
def get_transaction_detail_with_relations(db: Session, detail_id: int) -> Optional[TransactionDetailWithRelations]:
    db_detail = (
        db.query(TransactionDetail)
        .options(
            joinedload(TransactionDetail.producto),
            joinedload(TransactionDetail.transaccion)
        )
        .filter(TransactionDetail.id == detail_id)
        .first()
    )
    
    if not db_detail:
        return None
    
    detail_data = {
        **db_detail.__dict__,
        "producto": {
            "id": db_detail.producto.id,
            "nombre": db_detail.producto.nombre,
            "precio_base": float(db_detail.producto.precio_base)
        } if db_detail.producto else None,
        "transaccion": {
            "id": db_detail.transaccion.id,
            "business_id": db_detail.transaccion.business_id,
            "total": float(db_detail.transaccion.total),
            "fecha": db_detail.transaccion.fecha
        } if db_detail.transaccion else None
    }
    
    # Limpiar atributos de SQLAlchemy
    detail_data.pop('_sa_instance_state', None)
    if detail_data['producto']:
        detail_data['producto'].pop('_sa_instance_state', None)
    if detail_data['transaccion']:
        detail_data['transaccion'].pop('_sa_instance_state', None)
    
    return TransactionDetailWithRelations.model_validate(detail_data)

# Obtiene una lista de detalles de transacción con paginación y filtros opcionales
def get_transaction_details(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    transaction_id: Optional[int] = None,
    product_id: Optional[int] = None
) -> List[TransactionDetailRead]:
    query = db.query(TransactionDetail)
    
    if transaction_id:
        query = query.filter(TransactionDetail.transaction_id == transaction_id)
    if product_id:
        query = query.filter(TransactionDetail.product_id == product_id)
        
    return [
        TransactionDetailRead.model_validate(d)
        for d in query.offset(skip).limit(limit).all()
    ]

# Crea un nuevo detalle de transacción en la base de datos y retorna el detalle creado
def create_transaction_detail(db: Session, detail: TransactionDetailCreate) -> TransactionDetailRead:
    db_detail = TransactionDetail(**detail.model_dump())
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    return TransactionDetailRead.model_validate(db_detail)

# Actualiza un detalle de transacción existente
def update_transaction_detail(
    db: Session,
    detail_id: int,
    detail: TransactionDetailUpdate
) -> Optional[TransactionDetailRead]:
    db_detail = db.query(TransactionDetail).filter(TransactionDetail.id == detail_id).first()
    if not db_detail:
        return None
    
    update_data = detail.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_detail, field, value)
    
    db.commit()
    db.refresh(db_detail)
    return TransactionDetailRead.model_validate(db_detail)

# Elimina un detalle de transacción existente por su ID
def delete_transaction_detail(db: Session, detail_id: int) -> bool:
    db_detail = db.query(TransactionDetail).filter(TransactionDetail.id == detail_id).first()
    if not db_detail:
        return False
    
    db.delete(db_detail)
    db.commit()
    return True