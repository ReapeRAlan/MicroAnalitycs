import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.train_regression import train_model
from models.predict import predict


def test_predict_float(tmp_path):
    model_path = tmp_path / "model.joblib"
    train_model(output_model=model_path, metric_path=tmp_path/"metrics.json")
    sample = {
        "age": 0.05,
        "sex": 0.02,
        "bmi": 0.03,
        "bp": 0.04,
        "s1": 0.05,
        "s2": 0.06,
        "s3": 0.07,
        "s4": 0.08,
        "s5": 0.09,
        "s6": 0.1,
    }
    pred = predict(sample, model_path=model_path)
    assert isinstance(pred, float)
    assert -10.0 <= pred <= 500.0
