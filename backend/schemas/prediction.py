from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class PredictionBase(BaseModel):
    product_id: int
    dias_prediccion: int
    
class PredictionCreate(PredictionBase):
    business_id: int
    user_id: int

class PredictionResponse(PredictionBase):
    id: int
    modelo: str
    resultado: Dict[str, Any]
    estado: str
    fecha: datetime
    
    class Config:
        from_attributes = True