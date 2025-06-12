from pydantic import BaseModel
from typing import Optional

class TransactionBase(BaseModel):
    business_id: int
    total: float

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int
    fecha: Optional[str]

    class Config:
        orm_mode = True