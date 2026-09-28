from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.services.ai_request_replay_repository import AIRequestReplayRepository


@dataclass(frozen=True)
class AIRequestRecord:
    """Stores the inputs required to replay an AI request."""

    request_id: str
    service_name: str
    model: str
    inputs: Any
    recorded_at: datetime


class AIRequestReplayService:
    """Stores and retrieves AI requests for production debugging."""

    def __init__(
        self,
        repository: AIRequestReplayRepository | None = None,
    ) -> None:
        self.repository = repository or AIRequestReplayRepository()

    def record_request(
        self,
        request_id: str,
        service_name: str,
        model: str,
        inputs: Any,
        recorded_at: datetime | None = None,
    ) -> AIRequestRecord:
        """Persist an AI request so it can be replayed later."""

        if not request_id or not request_id.strip():
            raise ValueError("request_id cannot be empty")

        if not service_name or not service_name.strip():
            raise ValueError("service_name cannot be empty")

        if not model or not model.strip():
            raise ValueError("model cannot be empty")

        if recorded_at is None:
            recorded_at = datetime.now(timezone.utc)

        persisted = self.repository.create_request(
            request_id=request_id,
            service_name=service_name,
            model=model,
            inputs=inputs,
            recorded_at=recorded_at,
        )

        return AIRequestRecord(
            request_id=persisted["request_id"],
            service_name=persisted["service_name"],
            model=persisted["model"],
            inputs=persisted["inputs"],
            recorded_at=persisted["recorded_at"],
        )

    def get_request(self, request_id: str) -> AIRequestRecord:
        """Retrieve a persisted AI request."""

        if not request_id or not request_id.strip():
            raise ValueError("request_id cannot be empty")

        persisted = self.repository.get_request(request_id)

        return AIRequestRecord(
            request_id=persisted["request_id"],
            service_name=persisted["service_name"],
            model=persisted["model"],
            inputs=persisted["inputs"],
            recorded_at=persisted["recorded_at"],
        )

    def get_replay_inputs(self, request_id: str) -> Any:
        """Return the exact inputs from a persisted AI request."""

        record = self.get_request(request_id)
        return record.inputs