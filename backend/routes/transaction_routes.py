from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.schemas.transaction_schema import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
    TransactionWithRelations
)
from backend.crud.transaction_crud import (
    get_transaction,
    get_transaction_with_relations,
    get_transactions,
    create_transaction,
    update_transaction,
    delete_transaction
)
from backend.base import get_db

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

#Obtener todas las transacciones
@router.get("/", response_model=List[TransactionRead],
           summary="Listar transacciones",
           description="Obtiene una lista paginada de transacciones")
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    business_id: Optional[int] = Query(None, description="Filtrar por ID de negocio"),
    db: Session = Depends(get_db)
):
    return get_transactions(db, skip=skip, limit=limit, business_id=business_id)

#Ruta GET para obtener una transacción por su ID
@router.get("/{transaction_id}", response_model=TransactionRead,
           summary="Obtener transacción por ID",
           description="Obtiene los detalles básicos de una transacción")
def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = get_transaction(db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

#Ruta GET para obtener detalles completos de una transacción con relaciones
@router.get("/{transaction_id}/details", response_model=TransactionWithRelations,
           summary="Obtener detalles completos de transacción",
           description="Obtiene los detalles completos de una transacción incluyendo negocio y items")
def read_transaction_details(transaction_id: int, db: Session = Depends(get_db)):
    transaction = get_transaction_with_relations(db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

#Ruta POST para crear una nueva transacción
@router.post("/new", response_model=TransactionRead, status_code=201,
            summary="Crear nueva transacción",
            description="Registra una nueva transacción en el sistema")
def create_new_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    return create_transaction(db=db, transaction=transaction)

#Ruta PUT para actualizar una transacción existente
@router.put("/update/{transaction_id}", response_model=TransactionRead,
           summary="Actualizar transacción",
           description="Actualiza los datos de una transacción existente")
def update_existing_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db)
):
    updated_transaction = update_transaction(
        db, 
        transaction_id=transaction_id, 
        transaction=transaction
    )
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction

#ruta DELETE para eliminar una transacción existente
@router.delete("/delete/{transaction_id}",
              summary="Eliminar transacción",
              description="Elimina una transacción existente",
              responses={
                  200: {"description": "Transacción eliminada exitosamente"},
                  404: {"description": "Transacción no encontrada"}
              })
def delete_existing_transaction(transaction_id: int, db: Session = Depends(get_db)):
    success = delete_transaction(db, transaction_id=transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"status": "success", "message": "Transaction deleted"}