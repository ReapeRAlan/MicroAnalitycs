from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.base import Base

class Business(Base):
    __tablename__ = "business"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha_registro = Column(DateTime, default=func.now())

    usuarios = relationship("User", back_populates="business")
    productos = relationship("Product", back_populates="business")
    transacciones = relationship("Transaction", back_populates="business")