from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.schemas.transaction_detail_schema import (
    TransactionDetailCreate,
    TransactionDetailRead,
    TransactionDetailUpdate,
    TransactionDetailWithRelations
)
from backend.crud.transaction_detail_crud import (
    get_transaction_detail,
    get_transaction_detail_with_relations,
    get_transaction_details,
    create_transaction_detail,
    update_transaction_detail,
    delete_transaction_detail
)
from backend.base import get_db

router = APIRouter(
    prefix="/transaction-details",
    tags=["Transaction Details"]
)

#obtiene todos los detalles de transacción
@router.get("/", response_model=List[TransactionDetailRead],
           summary="Listar detalles de transacción",
           description="Obtiene una lista paginada de detalles de transacción")
def read_transaction_details(
    skip: int = 0,
    limit: int = 1000,
    transaction_id: Optional[int] = Query(None, description="Filtrar por ID de transacción"),
    product_id: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    db: Session = Depends(get_db)
):
    return get_transaction_details(
        db,
        skip=skip,
        limit=limit,
        transaction_id=transaction_id,
        product_id=product_id
    )

# Ruta GET para obtener un detalle de transacción por su ID
@router.get("/{detail_id}", response_model=TransactionDetailRead,
           summary="Obtener detalle por ID",
           description="Obtiene los detalles básicos de un item de transacción")
def read_transaction_detail(detail_id: int, db: Session = Depends(get_db)):
    detail = get_transaction_detail(db, detail_id=detail_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Transaction detail not found")
    return detail

# Ruta GET para obtener detalles completos de un detalle de transacción con relaciones
@router.get("/{detail_id}/details", response_model=TransactionDetailWithRelations,
           summary="Obtener detalle completo con relaciones",
           description="Obtiene los detalles completos incluyendo información de producto y transacción")
def read_transaction_detail_full(detail_id: int, db: Session = Depends(get_db)):
    detail = get_transaction_detail_with_relations(db, detail_id=detail_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Transaction detail not found")
    return detail

# Ruta POST para crear un nuevo detalle de transacción
@router.post("/new", response_model=TransactionDetailRead, status_code=201,
            summary="Crear nuevo detalle",
            description="Agrega un nuevo item a una transacción existente")
def create_new_transaction_detail(
    detail: TransactionDetailCreate,
    db: Session = Depends(get_db)
):
    return create_transaction_detail(db=db, detail=detail)

# Ruta PUT para actualizar un detalle de transacción existente
@router.put("/{detail_id}", response_model=TransactionDetailRead,
           summary="Actualizar detalle",
           description="Actualiza los datos de un item de transacción existente")
def update_existing_transaction_detail(
    detail_id: int,
    detail: TransactionDetailUpdate,
    db: Session = Depends(get_db)
):
    updated_detail = update_transaction_detail(
        db,
        detail_id=detail_id,
        detail=detail
    )
    if not updated_detail:
        raise HTTPException(status_code=404, detail="Transaction detail not found")
    return updated_detail

# Ruta DELETE para eliminar un detalle de transacción existente
@router.delete("/{detail_id}",
              summary="Eliminar detalle",
              description="Elimina un item de transacción existente",
              responses={
                  200: {"description": "Detalle eliminado exitosamente"},
                  404: {"description": "Detalle no encontrado"}
              })
def delete_existing_transaction_detail(detail_id: int, db: Session = Depends(get_db)):
    success = delete_transaction_detail(db, detail_id=detail_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction detail not found")
    return {"status": "success", "message": "Transaction detail deleted"}