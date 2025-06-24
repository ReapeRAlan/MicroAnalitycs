from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from .product_schema import ProductRead 

#Base común para creación y lectura
class InventoryBase(BaseModel):
    product_id: int = Field(..., description="ID del producto relacionado")
    stock_actual: int = Field(
        default=0,
        ge=0,
        description="Cantidad actual en stock (no puede ser negativo)"
    )

#Para crear un nuevo inventario (POST)
class InventoryCreate(InventoryBase):
    pass

#Para actualizar un inventario existente (PUT/PATCH)
class InventoryUpdate(BaseModel):
    stock_actual: Optional[int] = Field(None, ge=0)
    

    model_config = ConfigDict(extra="forbid")


#Para leer un inventario (GET)
class InventoryRead(InventoryBase):
    id: int
    ultimo_ingreso: datetime
    producto: Optional[ProductRead] = None  # Relación con producto

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )