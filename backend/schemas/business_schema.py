from pydantic import BaseModel
from typing import Optional

class BusinessBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class BusinessCreate(BusinessBase):
    pass

class BusinessUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class BusinessRead(BusinessBase):
    id: int
    fecha_registro: Optional[str]

    class Config:
        orm_mode = True