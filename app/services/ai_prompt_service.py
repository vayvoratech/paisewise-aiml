from dataclasses import dataclass
from typing import Any

from app.services.ai_prompt_repository import AIPromptRepository


@dataclass(frozen=True)
class AIPrompt:
    """Represents a versioned AI prompt."""

    prompt_key: str
    version: int
    prompt_text: str
    is_active: bool


class AIPromptService:
    """Manages versioned AI prompts and runtime activation."""

    def __init__(
        self,
        repository: AIPromptRepository | None = None,
    ) -> None:
        self.repository = repository or AIPromptRepository()

    def get_active_prompt(
        self,
        prompt_key: str,
    ) -> AIPrompt:
        self._validate_prompt_key(prompt_key)

        record = self.repository.get_active_prompt(
            prompt_key
        )

        return self._to_prompt(record)

    def create_prompt_version(
        self,
        prompt_key: str,
        prompt_text: str,
        activate: bool = False,
    ) -> AIPrompt:
        self._validate_prompt_key(prompt_key)
        self._validate_prompt_text(prompt_text)

        version = self.repository.get_next_version(
            prompt_key
        )

        record = self.repository.create_prompt(
            prompt_key=prompt_key,
            version=version,
            prompt_text=prompt_text.strip(),
            is_active=False,
        )

        prompt = self._to_prompt(record)

        if activate:
            return self.activate_prompt(
                prompt_key=prompt_key,
                version=version,
            )

        return prompt

    def activate_prompt(
        self,
        prompt_key: str,
        version: int,
    ) -> AIPrompt:
        self._validate_prompt_key(prompt_key)

        if not isinstance(version, int):
            raise TypeError(
                "version must be an integer"
            )

        if version <= 0:
            raise ValueError(
                "version must be greater than 0"
            )

        record = self.repository.activate_prompt(
            prompt_key=prompt_key,
            version=version,
        )

        return self._to_prompt(record)

    def get_prompt_version(
        self,
        prompt_key: str,
        version: int,
    ) -> AIPrompt:
        self._validate_prompt_key(prompt_key)

        if not isinstance(version, int):
            raise TypeError(
                "version must be an integer"
            )

        if version <= 0:
            raise ValueError(
                "version must be greater than 0"
            )

        record = self.repository.get_prompt_version(
            prompt_key=prompt_key,
            version=version,
        )

        return self._to_prompt(record)

    @staticmethod
    def _validate_prompt_key(prompt_key: str) -> None:
        if not isinstance(prompt_key, str):
            raise TypeError(
                "prompt_key must be a string"
            )

        if not prompt_key.strip():
            raise ValueError(
                "prompt_key cannot be empty"
            )

    @staticmethod
    def _validate_prompt_text(prompt_text: str) -> None:
        if not isinstance(prompt_text, str):
            raise TypeError(
                "prompt_text must be a string"
            )

        if not prompt_text.strip():
            raise ValueError(
                "prompt_text cannot be empty"
            )

    @staticmethod
    def _to_prompt(
        record: dict[str, Any],
    ) -> AIPrompt:
        return AIPrompt(
            prompt_key=record["prompt_key"],
            version=record["version"],
            prompt_text=record["prompt_text"],
            is_active=record["is_active"],
        )