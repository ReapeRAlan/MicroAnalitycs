from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.base import Base

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text)

    productos = relationship("Product", back_populates="categoria")