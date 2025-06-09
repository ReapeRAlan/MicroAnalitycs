import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.train_regression import train_model
from pathlib import Path


def test_train_creates_artifact(tmp_path):
    model_path = tmp_path / "model.joblib"
    train_model(output_model=model_path, metric_path=tmp_path/"metrics.json")
    assert model_path.exists()
