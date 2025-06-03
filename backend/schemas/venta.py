from pydantic import BaseModel
from datetime import datetime

class VentaBase(BaseModel):
    producto_id: int
    cantidad: int

class VentaCreate(VentaBase):
    pass

class VentaRead(VentaBase):
    id: int
    fecha: datetime
    total: float

    class Config:
        orm_mode = True
