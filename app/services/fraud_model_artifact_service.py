from pathlib import Path
from typing import Any

import joblib


class FraudModelArtifactService:
    """
    Persists and loads the validated fraud model artifact.

    This service is responsible only for artifact storage.
    Runtime inference should load the artifact once at startup
    and keep the resulting model in memory.
    """

    def __init__(self, artifact_path: str | Path):
        if artifact_path is None:
            raise ValueError("artifact_path is required")

        path = Path(artifact_path)

        if path.suffix != ".joblib":
            raise ValueError(
                "Fraud model artifact must use the .joblib format"
            )

        self._artifact_path = path

    @property
    def artifact_path(self) -> Path:
        return self._artifact_path

    def save(self, model: Any) -> Path:
        if model is None:
            raise ValueError("model is required")

        self._artifact_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        joblib.dump(
            model,
            self._artifact_path,
        )

        return self._artifact_path

    def load(self) -> Any:
        if not self._artifact_path.exists():
            raise FileNotFoundError(
                f"Fraud model artifact not found: "
                f"{self._artifact_path}"
            )

        return joblib.load(self._artifact_path)