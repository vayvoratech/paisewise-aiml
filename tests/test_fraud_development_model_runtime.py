from pathlib import Path

from app.services.fraud_model_artifact_service import (
    FraudModelArtifactService,
)
from app.services.fraud_model_runtime_service import (
    FraudModelRuntimeService,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ARTIFACT_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "fraud_model_dev.joblib"
)


def test_development_model_artifact_exists():
    assert ARTIFACT_PATH.exists()


def test_development_model_can_be_loaded():
    artifact_service = FraudModelArtifactService(
        ARTIFACT_PATH
    )

    model = artifact_service.load()

    assert model is not None
    assert callable(model.predict_proba)


def test_development_model_has_seven_features():
    artifact_service = FraudModelArtifactService(
        ARTIFACT_PATH
    )

    model = artifact_service.load()

    assert model.n_features_in_ == 7


def test_development_model_has_two_classes():
    artifact_service = FraudModelArtifactService(
        ARTIFACT_PATH
    )

    model = artifact_service.load()

    assert list(model.classes_) == [0, 1]

def test_development_model_runtime_prediction():
    artifact_service = FraudModelArtifactService(
        ARTIFACT_PATH
    )

    model = artifact_service.load()

    runtime = FraudModelRuntimeService(model)

    features = [
        10.0,
        2500.0,
        25000.0,
        1.0,
        0.0,
        1.0,
        0.0,
    ]

    probability = runtime.predict_proba(
        features
    )

    assert 0.0 <= probability <= 1.0