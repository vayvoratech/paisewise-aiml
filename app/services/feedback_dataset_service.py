import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_FEEDBACK = {"up", "down"}

ALLOWED_SOURCES = {
    "simulated_pre_deployment",
    "beta_user",
}


@dataclass(frozen=True)
class FeedbackRecord:
    record_id: str
    case_id: str
    theme: str
    feedback: str
    category: str
    comment: str
    source: str


class FeedbackDatasetService:
    """
    Loads and validates external Task 10 feedback datasets.

    The dataset is intentionally kept separate from the production
    public.chat_feedback table so synthetic pre-deployment feedback
    cannot be mistaken for real user feedback.
    """

    def __init__(self, dataset_path: str | Path):
        self.dataset_path = Path(dataset_path)

    def load_dataset(self) -> dict[str, Any]:
        if not self.dataset_path.exists():
            raise FileNotFoundError(
                f"Feedback dataset not found: {self.dataset_path}"
            )

        try:
            with self.dataset_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON feedback dataset: {self.dataset_path}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError("Feedback dataset root must be a JSON object.")

        return data

    def load_records(self) -> list[FeedbackRecord]:
        data = self.load_dataset()

        records = data.get("records")

        if not isinstance(records, list):
            raise ValueError("'records' must be a list.")

        parsed_records: list[FeedbackRecord] = []
        seen_ids: set[str] = set()

        for index, record in enumerate(records):
            if not isinstance(record, dict):
                raise ValueError(
                    f"Record at index {index} must be a JSON object."
                )

            parsed = self._parse_record(record, index)

            if parsed.record_id in seen_ids:
                raise ValueError(
                    f"Duplicate feedback record ID: {parsed.record_id}"
                )

            seen_ids.add(parsed.record_id)
            parsed_records.append(parsed)

        return parsed_records

    def get_records_by_theme(
        self,
        theme: str,
    ) -> list[FeedbackRecord]:
        return [
            record
            for record in self.load_records()
            if record.theme == theme
        ]

    def get_records_by_source(
        self,
        source: str,
    ) -> list[FeedbackRecord]:
        return [
            record
            for record in self.load_records()
            if record.source == source
        ]

    def _parse_record(
        self,
        record: dict[str, Any],
        index: int,
    ) -> FeedbackRecord:
        record_id = self._required_string(
            record,
            "id",
            index,
        )

        case_id = self._required_string(
            record,
            "case_id",
            index,
        )

        theme = self._required_string(
            record,
            "theme",
            index,
        )

        feedback = self._required_string(
            record,
            "feedback",
            index,
        )

        category = self._required_string(
            record,
            "category",
            index,
        )

        comment = self._required_string(
            record,
            "comment",
            index,
        )

        source = self._required_string(
            record,
            "source",
            index,
        )

        if feedback not in ALLOWED_FEEDBACK:
            raise ValueError(
                f"Invalid feedback '{feedback}' "
                f"for record '{record_id}'. "
                f"Allowed values: {sorted(ALLOWED_FEEDBACK)}"
            )

        if source not in ALLOWED_SOURCES:
            raise ValueError(
                f"Invalid source '{source}' "
                f"for record '{record_id}'. "
                f"Allowed values: {sorted(ALLOWED_SOURCES)}"
            )

        if not theme:
            raise ValueError(
                f"Theme cannot be empty for record '{record_id}'."
            )

        if not category:
            raise ValueError(
                f"Category cannot be empty for record '{record_id}'."
            )

        return FeedbackRecord(
            record_id=record_id,
            case_id=case_id,
            theme=theme,
            feedback=feedback,
            category=category,
            comment=comment,
            source=source,
        )

    @staticmethod
    def _required_string(
        record: dict[str, Any],
        field_name: str,
        index: int,
    ) -> str:
        value = record.get(field_name)

        if not isinstance(value, str):
            raise ValueError(
                f"Record at index {index}: "
                f"'{field_name}' must be a string."
            )

        value = value.strip()

        if not value:
            raise ValueError(
                f"Record at index {index}: "
                f"'{field_name}' cannot be empty."
            )

        return value