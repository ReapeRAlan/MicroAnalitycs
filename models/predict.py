"""Utilities to run predictions using the trained pipeline."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from pydantic import BaseModel, ValidationError

MODEL_PATH = Path(__file__).resolve().parent / "model.joblib"


class InputData(BaseModel):
    age: float
    sex: float
    bmi: float
    bp: float
    s1: float
    s2: float
    s3: float
    s4: float
    s5: float
    s6: float


def predict(input_dict: dict, model_path: Path = MODEL_PATH) -> float:
    """Validate input dictionary, load pipeline and return prediction."""
    try:
        data = InputData(**input_dict)
    except ValidationError as e:
        raise ValueError(str(e))

    pipeline = joblib.load(model_path)
    df = pd.DataFrame([data.dict()])
    pred = pipeline.predict(df)[0]
    return float(pred)


if __name__ == "__main__":
    import json, sys
    features = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    print(predict(features))
