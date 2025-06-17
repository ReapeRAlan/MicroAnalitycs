from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

class UserBase(BaseModel):
    nombre: Optional[str] = None
    correo: EmailStr
    rol: Optional[str] = None
    business_id: int

class UserCreate(UserBase):
    contrasena: str

class UserRead(UserBase):
    id: int
    fecha_creacion: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }