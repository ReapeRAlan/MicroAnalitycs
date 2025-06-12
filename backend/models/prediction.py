from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.base import Base

class Prediction(Base):
    __tablename__ = "prediction"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    business_id = Column(Integer, ForeignKey("business.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    modelo = Column(String(100))  # 'linear', 'polynomial_2', etc.
    dias_prediccion = Column(Integer)  # Número de días hacia adelante
    resultado = Column(JSON)  # Almacena predicciones y métricas
    fecha = Column(DateTime, default=func.now())
    estado = Column(String(50))  # 'success', 'error', 'processing'

    # Relaciones
    producto = relationship("Product", back_populates="predicciones")
    negocio = relationship("Business")
    usuario = relationship("User")