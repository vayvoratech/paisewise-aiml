from pathlib import Path

import pytest
from sklearn.linear_model import LogisticRegression

from app.services.fraud_model_artifact_service import (
    FraudModelArtifactService,
)


def test_saves_and_loads_model(tmp_path: Path):
    artifact_path = tmp_path / "fraud_model.joblib"

    service = FraudModelArtifactService(
        artifact_path
    )

    model = LogisticRegression()

    saved_path = service.save(model)

    assert saved_path == artifact_path
    assert artifact_path.exists()

    loaded_model = service.load()

    assert isinstance(
        loaded_model,
        LogisticRegression,
    )


def test_creates_missing_parent_directory(tmp_path: Path):
    artifact_path = (
        tmp_path
        / "models"
        / "fraud"
        / "fraud_model.joblib"
    )

    service = FraudModelArtifactService(
        artifact_path
    )

    service.save(LogisticRegression())

    assert artifact_path.exists()


def test_load_fails_when_artifact_does_not_exist(tmp_path: Path):
    artifact_path = (
        tmp_path / "missing_fraud_model.joblib"
    )

    service = FraudModelArtifactService(
        artifact_path
    )

    with pytest.raises(
        FileNotFoundError,
        match="Fraud model artifact not found",
    ):
        service.load()


def test_rejects_non_joblib_artifact(tmp_path: Path):
    artifact_path = tmp_path / "fraud_model.pkl"

    with pytest.raises(
        ValueError,
        match="\\.joblib",
    ):
        FraudModelArtifactService(
            artifact_path
        )


def test_rejects_missing_model(tmp_path: Path):
    service = FraudModelArtifactService(
        tmp_path / "fraud_model.joblib"
    )

    with pytest.raises(
        ValueError,
        match="model is required",
    ):
        service.save(None)


def test_rejects_missing_artifact_path():
    with pytest.raises(
        ValueError,
        match="artifact_path is required",
    ):
        FraudModelArtifactService(None)