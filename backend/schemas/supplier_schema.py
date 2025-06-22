from pydantic import BaseModel
from typing import Optional

class SupplierBase(BaseModel):
    nombre: str
    contacto: Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierRead(SupplierBase):
    id: int

    class Config:
        orm_mode = True