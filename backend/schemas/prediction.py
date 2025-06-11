from pydantic import BaseModel
from typing import Optional

class PredictionBase(BaseModel):
    product_id: int
    modelo: str
    resultado: float

class PredictionCreate(PredictionBase):
    pass

class PredictionRead(PredictionBase):
    id: int
    fecha: Optional[str]

    class Config:
        orm_mode = True