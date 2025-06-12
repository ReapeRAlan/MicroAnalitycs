from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    nombre: Optional[str] = None
    correo: EmailStr
    rol: Optional[str] = None
    business_id: int

class UserCreate(UserBase):
    contrasena: str

class UserRead(UserBase):
    id: int
    fecha_creacion: Optional[str]

    class Config:
        orm_mode = True