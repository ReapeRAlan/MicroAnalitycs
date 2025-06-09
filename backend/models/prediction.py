from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime
from backend.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    request_json = Column(String, nullable=False)
    prediction = Column(Float, nullable=False)
