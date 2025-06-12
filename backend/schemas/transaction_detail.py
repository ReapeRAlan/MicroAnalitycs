from pydantic import BaseModel

class TransactionDetailBase(BaseModel):
    transaction_id: int
    product_id: int
    cantidad: int
    precio_unitario: float

class TransactionDetailCreate(TransactionDetailBase):
    pass

class TransactionDetailRead(TransactionDetailBase):
    id: int

    class Config:
        orm_mode = True