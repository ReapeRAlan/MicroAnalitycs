from fastapi import FastAPI
from sqlalchemy.orm import Session
from backend.base import SessionLocal, Base, engine
from backend.routes import business_routes, category_routes  # Añade category_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MicroAnalitycs", debug=True)


app.include_router(
    business_routes.router,
    prefix="/api",  # Recomiendo añadir el recurso al prefijo
    tags=["Business"]
)

app.include_router(
    category_routes.router,
    prefix="/api",  # Prefijo específico para categorías
    tags=["Categories"]
)