from pydantic import BaseModel

class ProductoBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    precio_base: float
    stock_actual: int

class ProductoCreate(ProductoBase):
    pass

class ProductoRead(ProductoBase):
    id: int

    class Config:
        orm_mode = True
