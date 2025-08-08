from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.base import SessionLocal, Base, engine
from backend.routes import (
    business_routes, 
    category_routes, 
    product_routes, 
    supplier_routes, 
    inventory_routes,
    supplier_price_routes,
    prediction_routes,
    transaction_routes,
    transaction_detail_routes
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MicroAnalitycs", debug=True)

# Configurar CORS para permitir conexiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica las URLs permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    prefix="/api",  # Prefijo específico para inventario
    tags=["Inventory"]
)

app.include_router(
    supplier_price_routes.router,
    prefix="/api",  # Prefijo específico para precios de proveedores
    tags=["Supplier Prices"]
)

app.include_router(
    prediction_routes.router,
    prefix="/api",  # Prefijo específico para predicciones
    tags=["Predictions"]
)

app.include_router(
    transaction_routes.router,
    prefix="/api",  # Prefijo específico para transacciones
    tags=["Transactions"]
)

app.include_router(
    transaction_detail_routes.router,
    prefix="/api",  # Prefijo específico para detalles de transacciones
    tags=["Transaction Details"]    
)

# Agregar endpoint para chatbot
@app.post("/api/chatbot/message")
async def chatbot_message(message: dict):
    """Endpoint para el chatbot sin Ollama"""
    try:
        from backend.chatbot_handler import ChatbotHandler
        handler = ChatbotHandler()
        response = await handler.process_message(message)
        return response
    except Exception as e:
        return {"error": str(e), "message": "Error procesando mensaje"}

@app.get("/api/chatbot/health")
async def chatbot_health():
    """Check chatbot health"""
    return {"status": "healthy", "chatbot": "ready", "ollama_required": False}