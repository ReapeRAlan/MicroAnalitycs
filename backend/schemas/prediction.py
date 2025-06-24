from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PredictionBase(BaseModel):
    product_id: int
    dias_prediccion: int
    
class PredictionCreate(PredictionBase):
    business_id: int
    user_id: int

class PredictionResponse(PredictionBase):
    id: int
    fecha: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }