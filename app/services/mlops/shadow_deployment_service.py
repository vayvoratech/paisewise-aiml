from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ShadowComparisonResult:
    current_output: Any
    shadow_output: Any
    outputs_match: bool


class ShadowDeploymentService:
    """Runs the current and shadow models independently and compares outputs."""

    @staticmethod
    def compare(
        current_model: Callable[[Any], Any],
        shadow_model: Callable[[Any], Any],
        input_data: Any,
    ) -> ShadowComparisonResult:

        if not callable(current_model):
            raise TypeError("current_model must be callable")

        if not callable(shadow_model):
            raise TypeError("shadow_model must be callable")

        current_output = current_model(input_data)
        shadow_output = shadow_model(input_data)

        return ShadowComparisonResult(
            current_output=current_output,
            shadow_output=shadow_output,
            outputs_match=current_output == shadow_output,
        )