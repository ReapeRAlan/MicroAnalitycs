import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.predict import predict_demanda

def test_predict_empty():
    assert predict_demanda(999, 3) == []
