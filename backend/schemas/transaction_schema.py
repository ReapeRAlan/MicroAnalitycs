from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from .transaction_detail_schema import TransactionDetailRead  

#Base común para creación y lectura
class TransactionBase(BaseModel):
    business_id: int = Field(..., description="ID del negocio asociado")
    total: float = Field(..., gt=0, description="Total de la transacción (debe ser positivo)")

#Para crear un nuevo negocio (POST)
class TransactionCreate(TransactionBase):
    pass

#Para actualizar un negocio existente (PUT/PATCH)
class TransactionUpdate(BaseModel):
    total: Optional[float] = Field(None, gt=0, description="Nuevo total de la transacción")
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "total": 150.75
            }
        }
    )

#Para leer un negocio (GET)
class TransactionRead(TransactionBase):
    id: int
    fecha: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )

# Para leer un negocio con relaciones (GET con detalles)
class TransactionWithRelations(TransactionRead):
    business: Optional[dict] = None
    detalles: Optional[List[TransactionDetailRead]] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "business_id": 5,
                "total": 150.75,
                "fecha": "2023-01-01T12:00:00",
                "business": {
                    "id": 5,
                    "nombre": "Negocio Ejemplo"
                },
                "detalles": [
                    {
                        "id": 1,
                        "product_id": 3,
                        "cantidad": 2,
                        "precio_unitario": 50.25
                    }
                ]
            }
        }
    )