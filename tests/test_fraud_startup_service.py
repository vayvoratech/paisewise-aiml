import pytest

from app.services.fraud_startup_service import FraudStartupService
from app.services.fraud_runtime import FraudRuntime


class FakeModel:
    def predict_proba(self, rows):
        return [[0.9, 0.1]]


def test_skips_initialization_when_artifact_is_not_configured(
    monkeypatch,
):
    monkeypatch.delenv(
        "FRAUD_MODEL_ARTIFACT_PATH",
        raising=False,
    )

    assert FraudStartupService.initialize() is True


def test_initializes_runtime_from_artifact(
    monkeypatch,
    tmp_path,
):
    from app.services.fraud_model_artifact_service import (
        FraudModelArtifactService,
    )

    artifact_path = tmp_path / "fraud_model.joblib"

    artifact_service = FraudModelArtifactService(
        artifact_path
    )

    artifact_service.save(FakeModel())

    monkeypatch.setenv(
        "FRAUD_MODEL_ARTIFACT_PATH",
        str(artifact_path),
    )

    # Use a fresh runtime for the isolated test.
    import app.services.fraud_startup_service as startup_module

    startup_module.fraud_runtime = FraudRuntime()

    result = startup_module.FraudStartupService.initialize()

    assert result is True
    assert startup_module.fraud_runtime.get_runtime().model is not None


def test_missing_configured_artifact_fails_startup(
    monkeypatch,
    tmp_path,
):
    artifact_path = (
        tmp_path / "missing_fraud_model.joblib"
    )

    monkeypatch.setenv(
        "FRAUD_MODEL_ARTIFACT_PATH",
        str(artifact_path),
    )

    with pytest.raises(FileNotFoundError):
        FraudStartupService.initialize()