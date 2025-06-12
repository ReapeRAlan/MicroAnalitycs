from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from backend.base import Base

class Supplier(Base):
    __tablename__ = "supplier"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    contacto = Column(Text)

    precios = relationship("SupplierPrice", back_populates="proveedor")