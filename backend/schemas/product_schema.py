from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# Base común para creación y lectura
class ProductBase(BaseModel):
    
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float
    category_id: int  # FK a categoría
    business_id: int  # FK a negocio

# Para crear un nuevo producto (POST)
class ProductCreate(ProductBase):
    
    pass

# Para actualizar un producto existente (PUT/PATCH)
class ProductUpdate(BaseModel):
   
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = None
    category_id: Optional[int] = None
    business_id: Optional[int] = None

# Para leer un producto (GET)
class ProductRead(ProductBase):
    
    id: int
    fecha_registro: Optional[datetime] = None

    class Config:
        
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()  
        }

# Para leer un producto con relaciones (GET con relaciones)
class ProductWithRelations(ProductRead):
   
    categoria: Optional[dict] = None  
    business: Optional[dict] = None   

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat()}
    )