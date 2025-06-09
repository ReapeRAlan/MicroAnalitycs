from datetime import datetime
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import Base, engine, SessionLocal
from backend.models.prediction import Prediction
from models.predict import predict, InputData

Base.metadata.create_all(bind=engine)
app = FastAPI(title="MicroAnalytics API", version="1.0")


class DemandRequest(InputData):
    """Request schema inheriting from prediction InputData."""


class PredictionResponse(BaseModel):
    prediction: float


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/predict", response_model=PredictionResponse)
async def predict_endpoint(req: DemandRequest, db: Session = Depends(get_db)):
    pred = predict(req.dict())
    record = Prediction(timestamp=datetime.utcnow(), request_json=req.json(), prediction=pred)
    db.add(record)
    db.commit()
    return {"prediction": pred}
