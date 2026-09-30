import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EvaluationCase:
    """Represents one versioned AI evaluation case."""

    case_id: str
    theme: str
    question: str
    expected_behavior: str
    required_terms: list[str]
    forbidden_terms: list[str]
    personalization_requirements: dict[str, bool]
    classification_requirements: dict[str, Any]


class FeedbackAnalysisService:
    """
    Loads the versioned pre-deployment evaluation dataset.

    The evaluation cases are stored externally as JSON so that
    evaluation data can be updated without modifying application code.
    """

    def __init__(self, dataset_path: str | Path) -> None:
        self.dataset_path = Path(dataset_path)

    def load_cases(self) -> list[EvaluationCase]:
        """Load evaluation cases from the configured JSON dataset."""

        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Evaluation dataset not found: {self.dataset_path}"
            )

        with self.dataset_path.open("r", encoding="utf-8") as file:
            data: dict[str, Any] = json.load(file)

        cases = data.get("cases")

        if not isinstance(cases, list):
            raise ValueError(
                "Evaluation dataset must contain a 'cases' list."
            )

        evaluation_cases: list[EvaluationCase] = []

        for case in cases:
            if not isinstance(case, dict):
                raise ValueError(
                    "Each evaluation case must be an object."
                )

            personalization_requirements = case.get(
                "personalization_requirements",
                {},
            )

            if not isinstance(personalization_requirements, dict):
                raise ValueError(
                    "Evaluation case field "
                    "'personalization_requirements' must be an object."
                )

            classification_requirements = case.get(
                "classification_requirements",
                {},
            )

            if not isinstance(classification_requirements, dict):
                raise ValueError(
                    "Evaluation case field "
                    "'classification_requirements' must be an object."
                )

            evaluation_cases.append(
                EvaluationCase(
                    case_id=self._required_string(case, "id"),
                    theme=self._required_string(case, "theme"),
                    question=self._required_string(case, "question"),
                    expected_behavior=self._required_string(
                        case,
                        "expected_behavior",
                    ),
                    required_terms=self._string_list(
                        case,
                        "required_terms",
                    ),
                    forbidden_terms=self._string_list(
                        case,
                        "forbidden_terms",
                    ),
                    personalization_requirements={
                        key: value
                        for key, value in personalization_requirements.items()
                        if isinstance(key, str)
                        and isinstance(value, bool)
                    },
                    classification_requirements={
                        key: value
                        for key, value in classification_requirements.items()
                    },
                )
            )

        return evaluation_cases

    def get_cases_by_theme(
        self,
        theme: str,
    ) -> list[EvaluationCase]:
        """Return evaluation cases belonging to a specific improvement theme."""

        if not theme or not theme.strip():
            raise ValueError("theme cannot be empty")

        normalized_theme = theme.strip().lower()

        return [
            case
            for case in self.load_cases()
            if case.theme.lower() == normalized_theme
        ]

    def analyze_feedback_dataset(self, records):
        """
        Analyze validated Task 10 feedback records.

        Returns feedback counts grouped by theme.
        """

        analysis = {}

        for record in records:
            theme = record.theme

            if theme not in analysis:
                analysis[theme] = {
                    "total": 0,
                    "up": 0,
                    "down": 0,
                    "records": [],
                }

            analysis[theme]["total"] += 1
            analysis[theme][record.feedback] += 1
            analysis[theme]["records"].append(record.record_id)

        return analysis

    @staticmethod
    def _required_string(
        case: dict[str, Any],
        field_name: str,
    ) -> str:
        value = case.get(field_name)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"Evaluation case field '{field_name}' "
                "must be a non-empty string."
            )

        return value.strip()

    @staticmethod
    def _string_list(
        case: dict[str, Any],
        field_name: str,
    ) -> list[str]:
        value = case.get(field_name, [])

        if not isinstance(value, list):
            raise ValueError(
                f"Evaluation case field '{field_name}' "
                "must be a list."
            )

        if not all(
            isinstance(item, str) and item.strip()
            for item in value
        ):
            raise ValueError(
                f"All values in '{field_name}' "
                "must be non-empty strings."
            )

        return [item.strip() for item in value]