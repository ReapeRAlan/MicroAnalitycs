import pandas as pd
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.venta import Venta
from sklearn.linear_model import LinearRegression
import joblib
import os


def train(producto_id: int):
    db: Session = SessionLocal()
    try:
        ventas = db.query(Venta).filter(Venta.producto_id == producto_id).all()
        if not ventas:
            print("No hay datos de ventas")
            return
        data = pd.DataFrame([{"fecha": v.fecha.toordinal(), "cantidad": v.cantidad} for v in ventas])
        X = data[["fecha"]]
        y = data["cantidad"]
        model = LinearRegression().fit(X, y)
        os.makedirs("models/artifacts", exist_ok=True)
        joblib.dump(model, f"models/artifacts/regresion_producto_{producto_id}.pkl")
        print("Modelo guardado")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    pid = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    train(pid)
