from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from app.services.fraud_model_artifact_service import (
    FraudModelArtifactService,
)
from app.services.fraud_runtime import fraud_runtime


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class FraudStartupService:
    """
    Loads the fraud model once during application startup.

    Fraud model initialization remains optional when no
    artifact path is configured.
    """

    ENV_VAR = "FRAUD_MODEL_ARTIFACT_PATH"

    @classmethod
    def initialize(cls) -> bool:
        """
        Load the configured fraud model and initialize the
        in-memory fraud runtime.

        Returns:
            True when the model is successfully initialized.
            False when no model artifact is configured.
        """

        load_dotenv()

        artifact_path = os.getenv(cls.ENV_VAR)

        if not artifact_path:
            return False

        artifact = Path(artifact_path)

        if not artifact.is_absolute():
            artifact = PROJECT_ROOT / artifact

        artifact_service = FraudModelArtifactService(
            artifact
        )

        model = artifact_service.load()

        fraud_runtime.initialize(model)

        return True