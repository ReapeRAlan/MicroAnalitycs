from fastapi import FastAPI
from sqlalchemy.orm import Session
from backend.base import SessionLocal, Base, engine
from backend.routes import (
    business_routes, 
    category_routes, 
    product_routes, 
    supplier_routes, 
    inventory_routes,
    supplier_price_routes,
    prediction_routes)

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

app.include_router(
    product_routes.router,
    prefix="/api",  # Prefijo específico para categorías
    tags=["Products"]
)

app.include_router(
    supplier_routes.router,
    prefix="/api",  # Prefijo específico para categorías
    tags=["Suppliers"]
)

app.include_router(
    inventory_routes.router,
    prefix="/api",  # Prefijo específico para categorías
    tags=["Inventory"]
)

app.include_router(
    supplier_price_routes.router,
    prefix="/api",  # Prefijo específico para categorías
    tags=["Supplier Prices"]
)

app.include_router(
    prediction_routes.router,
    prefix="/api",  # Prefijo específico para predicciones
    tags=["Predictions"]
)
