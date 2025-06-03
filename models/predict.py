import joblib
from pathlib import Path
from datetime import datetime, timedelta


def predict_demanda(producto_id: int, dias_adelante: int):
    artifact = Path(f"models/artifacts/regresion_producto_{producto_id}.pkl")
    if not artifact.exists():
        return []
    model = joblib.load(artifact)
    start = datetime.now().toordinal()
    X_future = [[start + i] for i in range(1, dias_adelante + 1)]
    preds = model.predict(X_future)
    return preds.tolist()
