from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.base import SessionLocal, Base, engine
from models.predict import predict_demanda
from backend.routes import business_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MicroAnalitycs")

app.include_router(business_routes.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# Simple prediction endpoint using a serialized model if available
@app.post("/predicciones/")
def predicciones(producto_id: int, dias_adelante: int):
    pred = predict_demanda(producto_id, dias_adelante)
    return {"predicciones": pred, "fechas": []}

# Dummy chatbot endpoint
@app.post("/chatbot/")
def chatbot(mensaje: str):
    return {"respuesta": f"Echo: {mensaje}"}
