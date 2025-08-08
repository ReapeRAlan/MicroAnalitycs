from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from backend.models.transaction import Transaction
from backend.schemas.transaction_schema import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
    TransactionWithRelations
)

#obtiene una transacción por ID
def get_transaction(db: Session, transaction_id: int) -> Optional[TransactionRead]:
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    return TransactionRead.model_validate(db_transaction) if db_transaction else None

# Obtiene una transacción con sus relaciones (negocio y detalles)
def get_transaction_with_relations(db: Session, transaction_id: int) -> Optional[TransactionWithRelations]:
    db_transaction = (
        db.query(Transaction)
        .options(
            joinedload(Transaction.business),
            joinedload(Transaction.detalles)
        )
        .filter(Transaction.id == transaction_id)
        .first()
    )
    
    if not db_transaction:
        return None
    
    transaction_data = {
        **db_transaction.__dict__,
        "business": {
            "id": db_transaction.business.id,
            "nombre": db_transaction.business.nombre
        } if db_transaction.business else None,
        "detalles": [
            {
                "id": detalle.id,
                "product_id": detalle.product_id,
                "cantidad": detalle.cantidad,
                "precio_unitario": float(detalle.precio_unitario)
            }
            for detalle in db_transaction.detalles
        ]
    }
    
    transaction_data.pop('_sa_instance_state', None)
    if transaction_data['business']:
        transaction_data['business'].pop('_sa_instance_state', None)
    
    return TransactionWithRelations.model_validate(transaction_data)

#Obtiene una lista de transacciones con paginación y filtrado opcional por ID de negocio
def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 1000,
    business_id: Optional[int] = None
) -> List[TransactionRead]:
    query = db.query(Transaction)
    
    if business_id:
        query = query.filter(Transaction.business_id == business_id)
        
    return [
        TransactionRead.model_validate(t)
        for t in query.offset(skip).limit(limit).all()
    ]

# Crea una nueva transacción en la base de datos y retorna la transacción creada
def create_transaction(db: Session, transaction: TransactionCreate) -> TransactionRead:
    db_transaction = Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return TransactionRead.model_validate(db_transaction)

# Actualiza una transacción existente
def update_transaction(
    db: Session,
    transaction_id: int,
    transaction: TransactionUpdate
) -> Optional[TransactionRead]:
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        return None
    
    update_data = transaction.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    
    db.commit()
    db.refresh(db_transaction)
    return TransactionRead.model_validate(db_transaction)

# Elimina una transacción por su ID
def delete_transaction(db: Session, transaction_id: int) -> bool:
    db_transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not db_transaction:
        return False
    
    db.delete(db_transaction)
    db.commit()
    return True