from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship
from backend.database import Base

class Venta(Base):
    __tablename__ = "ventas"
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"))
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, server_default=func.now())
    total = Column(Float, nullable=False)

    producto = relationship("Producto")
