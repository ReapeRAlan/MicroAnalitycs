from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional

#base comun para creación y lectura
class SupplierPriceBase(BaseModel):
    product_id: int
    supplier_id: int
    precio: float

#para crear un nuevo precio de proveedor (POST)
class SupplierPriceCreate(SupplierPriceBase):
    pass

#para actualizar un precio de proveedor existente (PUT/PATCH)
class SupplierPriceUpdate(BaseModel):
    precio: Optional[float] = None
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "precio": 150.50
            }
        }
    )

#para leer un precio de proveedor (GET)
class SupplierPriceRead(SupplierPriceBase):
    id: int
    fecha: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )

# para leer un precio de proveedor con relaciones (GET con detalles)
class SupplierPriceWithRelations(SupplierPriceRead):
    producto: Optional[dict] = None
    proveedor: Optional[dict] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "product_id": 5,
                "supplier_id": 3,
                "precio": 150.50,
                "fecha": "2023-01-01T12:00:00",
                "producto": {
                    "id": 5,
                    "nombre": "Producto Ejemplo"
                },
                "proveedor": {
                    "id": 3,
                    "nombre": "Proveedor Ejemplo"
                }
            }
        }
    )