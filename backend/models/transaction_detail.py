from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from backend.base import Base

class TransactionDetail(Base):
    __tablename__ = "transaction_detail"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey("transaction.id"))
    product_id = Column(Integer, ForeignKey("product.id"))
    cantidad = Column(Integer)
    precio_unitario = Column(Numeric(10, 2))

    transaccion = relationship("Transaction", back_populates="detalles")
    producto = relationship("Product", back_populates="detalles_venta")