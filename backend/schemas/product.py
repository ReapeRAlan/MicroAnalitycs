from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    category_id: int
    business_id: int

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int

    class Config:
        orm_mode = True