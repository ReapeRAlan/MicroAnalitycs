from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List

# Base común para creación y lectura
class SupplierBase(BaseModel):

    nombre: str = Field(..., max_length=100, description="Nombre del proveedor")
    contacto: Optional[str] = Field(
        None, 
        description="Información de contacto del proveedor"
    )

#Para crear un nuevo proveedor (POST)
class SupplierCreate(SupplierBase):
    
    pass

# Para actualizar un proveedor existente (PUT/PATCH)
class SupplierUpdate(BaseModel):
    
    nombre: Optional[str] = Field(None, max_length=100)
    contacto: Optional[str] = None

    model_config = ConfigDict(extra="forbid")  


# Para leer un proveedor (GET)
class SupplierRead(SupplierBase):
    
    id: int
    fecha_registro: Optional[datetime] = None

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }