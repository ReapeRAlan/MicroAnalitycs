from sqlalchemy import Column, Integer, String, Float
from backend.database import Base

class Producto(Base):
    __tablename__ = "productos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    precio_base = Column(Float, nullable=False)
    stock_actual = Column(Integer, default=0)
