from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.base import SessionLocal, Base, engine
#from models.predict import predict_demanda
from backend.routes import business_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MicroAnalitycs")

app.include_router(business_routes.router)

#importar model.predictor
