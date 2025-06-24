from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

# Base común para creación y lectura
class CategoryBase(BaseModel):
    
    nombre: str
    descripcion: Optional[str] = None

# Para crear un nuevo producto (POST)
class CategoryCreate(CategoryBase):
    
    pass

# Para actualizar un producto existente (PUT/PATCH)
class CategoryUpdate(BaseModel):
    
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

# Para leer un producto (GET)
class CategoryRead(CategoryBase):
    
    id: int
    fecha_registro: Optional[datetime] = None

    class Config:
        
        from_attributes = True  # Permite carga desde objetos SQLAlchemy
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Formatea fechas en JSON
        }
