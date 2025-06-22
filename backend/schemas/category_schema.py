from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from .product_schema import ProductRead

"""
Esquemas Pydantic para el modelo Category:
- Define cómo se estructuran los datos de entrada/salida
- Valida los datos antes de interactuar con la BD
"""

class CategoryBase(BaseModel):
    """Base común con campos mínimos requeridos"""
    nombre: str
    descripcion: Optional[str] = None

class CategoryCreate(CategoryBase):
    """Esquema específico para creación (POST) - Hereda de Base"""
    pass

class CategoryUpdate(BaseModel):
    """Esquema para actualización (PUT/PATCH) - Todos los campos opcionales"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class CategoryRead(CategoryBase):
    """Esquema para lectura (GET) - Incluye campos autogenerados"""
    id: int
    fecha_registro: Optional[datetime] = None

    class Config:
        """Configuración especial para compatibilidad con ORM"""
        from_attributes = True  # Permite carga desde objetos SQLAlchemy
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Formatea fechas en JSON
        }

class CategoryWithProducts(CategoryRead):
    """Esquema extendido que incluye productos relacionados"""
    productos: List[ProductRead] = []

    class Config:
        from_attributes = True