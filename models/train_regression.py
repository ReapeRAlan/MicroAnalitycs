"""Train a demand regression model and save metrics."""
from __future__ import annotations

from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.datasets import load_diabetes
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "simulated.csv"
MODEL_PATH = Path(__file__).resolve().parent / "model.joblib"
METRIC_PATH = Path(__file__).resolve().parent.parent / "reports" / "metrics.json"


def load_datasets() -> tuple[pd.DataFrame, pd.Series]:
    """Load public diabetes dataset and custom simulated data."""
    X, y = load_diabetes(return_X_y=True, as_frame=True)
    sim = pd.read_csv(DATA_PATH)
    sim_y = sim.pop("target")
    X = pd.concat([X, sim], ignore_index=True)
    y = pd.concat([y, sim_y], ignore_index=True)
    return X, y


def clean_data(X: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Impute missing values and remove outliers. Returns cleaned X and mask."""
    X = X.copy()
    X = X.fillna(X.median())
    z = (X - X.mean()) / X.std(ddof=0)
    mask = (np.abs(z) <= 3).all(axis=1)
    X = X[mask]
    return X, mask


def train_model(output_model: Path = MODEL_PATH, metric_path: Path = METRIC_PATH) -> Path:
    """Train model and persist the pipeline and metrics."""
    X, y = load_datasets()
    X, mask = clean_data(X)
    y = y[mask].reset_index(drop=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", RandomForestRegressor(n_estimators=100, random_state=42)),
    ])
    pipeline.fit(X_train, y_train)
    joblib.dump(pipeline, output_model)

    preds = pipeline.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    metrics = {
        "mae": mean_absolute_error(y_test, preds),
        "rmse": float(mse ** 0.5),
        "r2": r2_score(y_test, preds),
    }
    metric_path.parent.mkdir(exist_ok=True)
    with metric_path.open("w") as f:
        json.dump(metrics, f, indent=2)

    return output_model


if __name__ == "__main__":
    path = train_model()
    print(f"Model saved to {path}")
