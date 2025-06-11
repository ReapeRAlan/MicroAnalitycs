from sqlalchemy import Column, Integer, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.base import Base

class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key=True)
    business_id = Column(Integer, ForeignKey("business.id"))
    fecha = Column(DateTime, default=func.now())
    total = Column(Numeric(10, 2))

    business = relationship("Business", back_populates="transacciones")
    detalles = relationship("TransactionDetail", back_populates="transaccion")