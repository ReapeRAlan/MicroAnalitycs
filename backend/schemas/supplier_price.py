from pydantic import BaseModel
from typing import Optional

class SupplierPriceBase(BaseModel):
    product_id: int
    supplier_id: int
    precio: float

class SupplierPriceCreate(SupplierPriceBase):
    pass

class SupplierPriceRead(SupplierPriceBase):
    id: int
    fecha: Optional[str]

    class Config:
        orm_mode = True