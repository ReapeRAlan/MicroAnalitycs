from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("business.id"))
    nombre = Column(String(100))
    correo = Column(String(100), unique=True)
    contrasena = Column(Text, nullable=False)
    rol = Column(String(50))
    fecha_creacion = Column(DateTime, default=func.now())

    business = relationship("Business", back_populates="usuarios")
    # Add relationship here
    chat_logs = relationship("ChatLog", back_populates="user")