from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PredictionBase(BaseModel):
    product_id: int
    modelo: str
    resultado: float

class PredictionCreate(PredictionBase):
    pass

class PredictionRead(PredictionBase):
    id: int
    fecha: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }