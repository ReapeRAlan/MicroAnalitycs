from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SupplierPriceBase(BaseModel):
    product_id: int
    supplier_id: int
    precio: float

class SupplierPriceCreate(SupplierPriceBase):
    pass

class SupplierPriceRead(SupplierPriceBase):
    id: int
    fecha: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }