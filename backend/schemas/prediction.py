from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.base import Base

class Prediction(Base):
    __tablename__ = "prediction"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    modelo = Column(String(100))
    resultado = Column(Numeric(10, 2))
    fecha = Column(DateTime, default=func.now())

    producto = relationship("Product", back_populates="predicciones")