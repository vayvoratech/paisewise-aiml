import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BetaGoldenSetCase:
    case_id: str
    theme: str
    question: str
    expected_behavior: str
    required_terms: list[str]
    forbidden_terms: list[str]
    personalization_requirements: dict[str, Any] | None = None


class BetaGoldenSetService:
    """
    Manages validated beta-user questions that can be added
    to the Task 10 golden set.

    This service intentionally does not modify any existing
    Task 10 services.
    """

    ALLOWED_SOURCE = "beta_user"

    REQUIRED_FIELDS = {
        "id",
        "theme",
        "question",
        "expected_behavior",
        "required_terms",
        "forbidden_terms",
        "source",
    }

    def __init__(self, golden_set_path: str):
        self.golden_set_path = Path(golden_set_path)

    def load_golden_set(self) -> dict[str, Any]:
        """Load the existing golden-set JSON file."""
        if not self.golden_set_path.exists():
            raise FileNotFoundError(
                f"Golden set file not found: {self.golden_set_path}"
            )

        try:
            with self.golden_set_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid golden set JSON: {self.golden_set_path}"
            ) from exc

        if not isinstance(data, dict):
            raise ValueError("Golden set must contain a JSON object.")

        cases = data.get("cases")

        if not isinstance(cases, list):
            raise ValueError(
                "Golden set must contain a 'cases' list."
            )

        return data

    def validate_beta_case(
        self,
        record: dict[str, Any],
    ) -> BetaGoldenSetCase:
        """Validate one beta-user record."""
        if not isinstance(record, dict):
            raise ValueError("Beta golden-set record must be an object.")

        missing_fields = self.REQUIRED_FIELDS - set(record.keys())

        if missing_fields:
            raise ValueError(
                "Missing required fields: "
                + ", ".join(sorted(missing_fields))
            )

        if record["source"] != self.ALLOWED_SOURCE:
            raise ValueError(
                "Only records with source='beta_user' "
                "can be added to the golden set."
            )

        string_fields = [
            "id",
            "theme",
            "question",
            "expected_behavior",
            "source",
        ]

        for field in string_fields:
            value = record[field]

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"'{field}' must be a non-empty string."
                )

        if not isinstance(record["required_terms"], list):
            raise ValueError(
                "'required_terms' must be a list."
            )

        if not isinstance(record["forbidden_terms"], list):
            raise ValueError(
                "'forbidden_terms' must be a list."
            )

        for field in ("required_terms", "forbidden_terms"):
            if not all(
                isinstance(term, str) and term.strip()
                for term in record[field]
            ):
                raise ValueError(
                    f"All values in '{field}' must be "
                    "non-empty strings."
                )

        personalization_requirements = record.get(
            "personalization_requirements"
        )

        if personalization_requirements is not None:
            if not isinstance(
                personalization_requirements,
                dict,
            ):
                raise ValueError(
                    "'personalization_requirements' must be "
                    "an object when provided."
                )

        return BetaGoldenSetCase(
            case_id=record["id"],
            theme=record["theme"],
            question=record["question"],
            expected_behavior=record["expected_behavior"],
            required_terms=record["required_terms"],
            forbidden_terms=record["forbidden_terms"],
            personalization_requirements=(
                personalization_requirements
            ),
        )

    def validate_beta_dataset(
        self,
        records: list[dict[str, Any]],
    ) -> list[BetaGoldenSetCase]:
        """Validate a complete beta-user dataset."""
        if not isinstance(records, list):
            raise ValueError(
                "Beta dataset must contain a list of records."
            )

        validated_cases = []
        case_ids = set()

        for record in records:
            case = self.validate_beta_case(record)

            if case.case_id in case_ids:
                raise ValueError(
                    f"Duplicate beta case ID: {case.case_id}"
                )

            case_ids.add(case.case_id)
            validated_cases.append(case)

        return validated_cases

    def add_beta_cases(
        self,
        records: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Validate beta-user cases and add them to the existing
        golden set in memory.

        The original golden-set file is not modified.
        """
        golden_set = self.load_golden_set()

        existing_cases = golden_set["cases"]

        existing_case_ids = {
            case.get("id")
            for case in existing_cases
            if isinstance(case, dict)
        }

        beta_cases = self.validate_beta_dataset(records)

        for case in beta_cases:
            if case.case_id in existing_case_ids:
                raise ValueError(
                    f"Case ID already exists in golden set: "
                    f"{case.case_id}"
                )

        for case in beta_cases:
            case_data = {
                "id": case.case_id,
                "theme": case.theme,
                "question": case.question,
                "expected_behavior": case.expected_behavior,
                "required_terms": case.required_terms,
                "forbidden_terms": case.forbidden_terms,
            }

            if case.personalization_requirements is not None:
                case_data[
                    "personalization_requirements"
                ] = case.personalization_requirements

            existing_cases.append(case_data)

        return golden_set

    def save_golden_set(
        self,
        golden_set: dict[str, Any],
        output_path: str,
    ) -> Path:
        """
        Save an updated golden set to a separate output file.

        The original golden-set file remains untouched.
        """
        output = Path(output_path)

        output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                golden_set,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return output