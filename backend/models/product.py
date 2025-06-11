from sqlalchemy import Column, Integer, String, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from backend.base import Base

class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("business.id"))
    category_id = Column(Integer, ForeignKey("category.id"))
    nombre = Column(String(100))
    descripcion = Column(Text)
    precio_base = Column(Numeric(10, 2))

    business = relationship("Business", back_populates="productos")
    categoria = relationship("Category", back_populates="productos")
    inventario = relationship("Inventory", back_populates="producto", uselist=False)
    detalles_venta = relationship("TransactionDetail", back_populates="producto")
    precios_proveedor = relationship("SupplierPrice", back_populates="producto")
    predicciones = relationship("Prediction", back_populates="producto")