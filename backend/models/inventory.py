from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.base import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"), unique=True)
    stock_actual = Column(Integer, default=0)
    ultimo_ingreso = Column(DateTime, default=func.now())

    producto = relationship("Product", back_populates="inventario")