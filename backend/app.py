from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal, Base, engine
from backend.models import producto as producto_model
from backend.models import venta as venta_model
from backend.schemas.producto import ProductoCreate, ProductoRead
from backend.schemas.venta import VentaCreate, VentaRead
from backend.crud import producto_crud, venta_crud
from models.predict import predict_demanda

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MicroAnalitycs")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/productos/", response_model=list[ProductoRead])
def list_productos(db: Session = Depends(get_db)):
    return producto_crud.get_productos(db)

@app.post("/productos/", response_model=ProductoRead)
def create_producto(prod: ProductoCreate, db: Session = Depends(get_db)):
    return producto_crud.create_producto(db, prod)

@app.get("/productos/{producto_id}", response_model=ProductoRead)
def get_producto(producto_id: int, db: Session = Depends(get_db)):
    prod = producto_crud.get_producto(db, producto_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return prod

@app.put("/productos/{producto_id}", response_model=ProductoRead)
def update_producto(producto_id: int, prod: ProductoCreate, db: Session = Depends(get_db)):
    updated = producto_crud.update_producto(db, producto_id, prod)
    if not updated:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return updated

@app.delete("/productos/{producto_id}", response_model=ProductoRead)
def delete_producto(producto_id: int, db: Session = Depends(get_db)):
    deleted = producto_crud.delete_producto(db, producto_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return deleted

@app.post("/ventas/", response_model=VentaRead)
def registrar_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    created = venta_crud.create_venta(db, venta)
    if not created:
        raise HTTPException(status_code=400, detail="Stock insuficiente o producto inexistente")
    return created

@app.get("/ventas/", response_model=list[VentaRead])
def listar_ventas(db: Session = Depends(get_db)):
    return venta_crud.get_ventas(db)

@app.get("/inventario/")
def inventario(db: Session = Depends(get_db)):
    prods = producto_crud.get_productos(db)
    return [{"id": p.id, "nombre": p.nombre, "stock_actual": p.stock_actual, "precio_base": p.precio_base} for p in prods]

# Simple prediction endpoint using a serialized model if available
@app.post("/predicciones/")
def predicciones(producto_id: int, dias_adelante: int):
    pred = predict_demanda(producto_id, dias_adelante)
    return {"predicciones": pred, "fechas": []}

# Dummy chatbot endpoint
@app.post("/chatbot/")
def chatbot(mensaje: str):
    return {"respuesta": f"Echo: {mensaje}"}
