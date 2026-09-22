import json

from pathlib import Path
from datetime import datetime, timedelta


class CostStorage:

    RETENTION_DAYS = 90

    def __init__(self):

        self.file_path = (
            Path(__file__).parent /
            "cost_records.json"
        )

        if not self.file_path.exists():

            self._save_records([])

    # ============================================================
    # LOAD RECORDS + 90-DAY RETENTION
    # ============================================================

    def _load_records(self):

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as file:

                records = json.load(file)

            # ----------------------------------------------------
            # Remove records older than 90 days
            # ----------------------------------------------------

            cutoff_date = (
                datetime.now() -
                timedelta(
                    days=self.RETENTION_DAYS
                )
            )

            recent_records = []

            for record in records:

                timestamp = record.get("timestamp")

                if not timestamp:
                    continue

                try:

                    record_date = datetime.fromisoformat(
                        timestamp
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    # Keep records with invalid timestamps
                    # instead of deleting them automatically.

                    recent_records.append(record)

                    continue

                if record_date >= cutoff_date:

                    recent_records.append(record)

            # ----------------------------------------------------
            # Save cleaned records if anything changed
            # ----------------------------------------------------

            if len(recent_records) != len(records):

                self._save_records(
                    recent_records
                )

            return recent_records

        except (
            json.JSONDecodeError,
            FileNotFoundError
        ):

            return []

    # ============================================================
    # SAVE RECORDS
    # ============================================================

    def _save_records(self, records):

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                records,
                file,
                indent=4,
                default=str
            )

    # ============================================================
    # ADD RECORD
    # ============================================================

    def add_record(self, record):

        records = self._load_records()

        records.append(record)

        self._save_records(
            records
        )

        return record

    # ============================================================
    # GET ALL RECORDS
    # ============================================================

    def get_records(self):

        return self._load_records()

    # ============================================================
    # GET TOTAL COST
    # ============================================================

    def get_total_cost(self):

        records = self._load_records()

        total = sum(
            record["cost_inr"]
            for record in records
        )

        return round(
            total,
            4
        )

    # ============================================================
    # DELETE USER RECORDS
    # ============================================================

    def delete_user_records(self, user_id):
        """
        Delete all LLM cost records belonging
        to the specified user.

        Only records with an exact matching
        user_id are deleted.
        """

        records = self._load_records()

        original_count = len(records)

        remaining_records = [
            record
            for record in records
            if record.get("user_id") != user_id
        ]

        deleted_count = (
            original_count -
            len(remaining_records)
        )

        self._save_records(
            remaining_records
        )

        return deleted_count