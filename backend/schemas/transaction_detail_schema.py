from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

#Base común para creación y lectura
class TransactionDetailBase(BaseModel):
    transaction_id: int = Field(..., description="ID de la transacción asociada")
    product_id: int = Field(..., description="ID del producto vendido")
    cantidad: int = Field(..., gt=0, description="Cantidad vendida (debe ser mayor que 0)")
    precio_unitario: float = Field(..., gt=0, description="Precio unitario (debe ser positivo)")

#Para crear un nuevo detalle de transacción (POST)
class TransactionDetailCreate(TransactionDetailBase):
    pass

#Para actualizar un detalle de transacción existente (PUT/PATCH)
class TransactionDetailUpdate(BaseModel):
    cantidad: Optional[int] = Field(None, gt=0)
    precio_unitario: Optional[float] = Field(None, gt=0)
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "cantidad": 3,
                "precio_unitario": 99.99
            }
        }
    )

#Para leer un detalle de transacción (GET)
class TransactionDetailRead(TransactionDetailBase):
    id: int
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )

#Para leer un detalle de transacción con relaciones (GET con relaciones)
class TransactionDetailWithRelations(TransactionDetailRead):
    producto: Optional[dict] = None
    transaccion: Optional[dict] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "transaction_id": 5,
                "product_id": 3,
                "cantidad": 2,
                "precio_unitario": 50.25,
                "producto": {
                    "id": 3,
                    "nombre": "Producto Ejemplo",
                    "precio_base": 45.00
                },
                "transaccion": {
                    "id": 5,
                    "business_id": 1,
                    "total": 150.75,
                    "fecha": "2023-01-01T12:00:00"
                }
            }
        }
    )