from datetime import datetime
from pydantic import BaseModel
from typing import Optional

# Base común para creación y lectura
class BusinessBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

# Para crear un nuevo negocio (POST)
class BusinessCreate(BusinessBase):
    pass

# Para actualizar un negocio existente (PUT/PATCH)
class BusinessUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

# Para leer un negocio (GET)
class BusinessRead(BusinessBase):
    id: int
    fecha_registro: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
