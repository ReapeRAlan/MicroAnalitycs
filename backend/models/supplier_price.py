from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.base import Base

class SupplierPrice(Base):
    __tablename__ = "supplier_price"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    supplier_id = Column(Integer, ForeignKey("supplier.id"))
    precio = Column(Numeric(10, 2))
    fecha = Column(DateTime, default=func.now())

    producto = relationship("Product", back_populates="precios_proveedor")
    proveedor = relationship("Supplier", back_populates="precios")