from pathlib import Path

import joblib


MODEL_PATH = Path(__file__).resolve().parent.parent / "fraud_model_v1.pkl"

fraud_model = None


def load_fraud_model():
    """
    Load the fraud detection model into memory at application startup.
    """

    global fraud_model

    if not MODEL_PATH.exists():
        print(
            f"Fraud model not found: {MODEL_PATH}. "
            "Fraud inference is not available."
        )
        fraud_model = None
        return

    fraud_model = joblib.load(MODEL_PATH)

    print(f"Fraud model loaded from: {MODEL_PATH}")


def get_fraud_model():
    """
    Return the loaded fraud model.
    """

    return fraud_model