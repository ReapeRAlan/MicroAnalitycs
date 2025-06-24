from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TransactionBase(BaseModel):
    business_id: int
    total: float

class TransactionCreate(TransactionBase):
    pass

class TransactionRead(TransactionBase):
    id: int
    fecha: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }