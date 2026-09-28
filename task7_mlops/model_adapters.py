from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ModelAdapter:
    name: str
    version: str
    predictor: Callable[[Any], Any]
    model_type: str

    def predict(self, input_data: Any) -> Any:
        if not callable(self.predictor):
            raise TypeError(f"Predictor for {self.name} must be callable")

        return self.predictor(input_data)

    def metadata(self) -> dict[str, str]:
        return {
            "model_name": self.name,
            "model_version": self.version,
            "model_type": self.model_type,
        }


class ModelAdapterRegistry:
    def __init__(self) -> None:
        self._models: dict[str, ModelAdapter] = {}

    def add(self, adapter: ModelAdapter) -> None:
        if not adapter.name.strip():
            raise ValueError("model name cannot be empty")

        self._models[adapter.name] = adapter

    def get(self, model_name: str) -> ModelAdapter:
        if model_name not in self._models:
            raise KeyError(f"Model not registered: {model_name}")

        return self._models[model_name]

    def list_models(self) -> list[str]:
        return list(self._models.keys())