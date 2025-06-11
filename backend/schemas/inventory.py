from pydantic import BaseModel
from typing import Optional

class InventoryBase(BaseModel):
    product_id: int
    stock_actual: int

class InventoryCreate(InventoryBase):
    pass

class InventoryRead(InventoryBase):
    id: int
    ultimo_ingreso: Optional[str]

    class Config:
        orm_mode = True