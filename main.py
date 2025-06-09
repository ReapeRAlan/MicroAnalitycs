"""Command line interface for MicroAnalytics."""

import argparse
import json
import subprocess

from models.predict import predict

parser = argparse.ArgumentParser(description="MicroAnalytics CLI")
parser.add_argument("--train", action="store_true", help="Train regression model")
parser.add_argument("--predict", type=str, help="JSON string with features for prediction")
args = parser.parse_args()

if args.train:
    subprocess.run(["python", "models/train_regression.py"], check=True)

if args.predict:
    features = json.loads(args.predict)
    print(predict(features))
