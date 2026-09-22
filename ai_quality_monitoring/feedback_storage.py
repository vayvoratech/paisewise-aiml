import json
from pathlib import Path


class FeedbackStorage:

    def __init__(self, file_path=None):

        if file_path is None:

            self.file_path = (
                Path(__file__).resolve().parent
                / "feedback_data.json"
            )

        else:

            self.file_path = Path(file_path)

    # ============================================================
    # GET ALL FEEDBACK
    # ============================================================

    def get_records(self):

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as file:

                records = json.load(file)

            if isinstance(records, list):
                return records

            return []

        except (
            FileNotFoundError,
            json.JSONDecodeError
        ):

            return []

    # ============================================================
    # DELETE USER FEEDBACK
    # ============================================================

    def delete_user_records(self, user_id):
        """
        Delete all feedback records belonging
        to the specified user.
        """

        records = self.get_records()

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

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                remaining_records,
                file,
                indent=4
            )

        return deleted_count