import json

from pathlib import Path


class QualityStorage:

    def __init__(self, file_path=None):
        """
        Store quality evaluation records in evaluation_data.json.
        The file is always created inside the ai_quality_monitoring folder.
        """

        if file_path is None:

            self.file_path = (
                Path(__file__).resolve().parent
                / "evaluation_data.json"
            )

        else:

            self.file_path = Path(file_path)

        if not self.file_path.exists():

            self.file_path.write_text(
                "[]",
                encoding="utf-8"
            )

    # ============================================================
    # ADD RECORD
    # ============================================================

    def add_record(self, record):
        """
        Add one evaluation record to storage.
        """

        records = self.get_records()

        records.append(record)

        self.file_path.write_text(
            json.dumps(
                records,
                indent=4
            ),
            encoding="utf-8"
        )

    # ============================================================
    # ADD EVALUATION
    # ============================================================

    def add_evaluation(
        self,
        evaluation,
        quality_tracker,
        user_id=None,
        response_id=None
    ):
        """
        Convert the Gemini evaluation into a tracking record
        and save it.
        """

        record = quality_tracker.create_record_from_evaluation(
            evaluation=evaluation,
            user_id=user_id,
            response_id=response_id
        )

        self.add_record(record)

        return record

    # ============================================================
    # GET ALL RECORDS
    # ============================================================

    def get_records(self):
        """
        Read all stored evaluation records.
        """

        try:

            return json.loads(
                self.file_path.read_text(
                    encoding="utf-8"
                )
            )

        except (
            FileNotFoundError,
            json.JSONDecodeError
        ):

            return []

    # ============================================================
    # DELETE USER RECORDS
    # ============================================================

    def delete_user_records(self, user_id):
        """
        Delete all quality evaluation records belonging
        to the specified user.

        Only records with an exact matching user_id
        are deleted.
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

        self.file_path.write_text(
            json.dumps(
                remaining_records,
                indent=4
            ),
            encoding="utf-8"
        )

        return deleted_count

    # ============================================================
    # GET FILE PATH
    # ============================================================

    def get_file_path(self):
        """
        Return the exact storage file path.
        """

        return str(self.file_path)


# ================================================================
# LOCAL TEST
# ================================================================

if __name__ == "__main__":

    from quality_evaluator import QualityEvaluator
    from quality_tracker import QualityTracker

    print("=" * 60)
    print("QUALITY EVALUATION STORAGE")
    print("=" * 60)

    evaluator = QualityEvaluator()

    tracker = QualityTracker()

    storage = QualityStorage()

    prompt = "What is diversification in investing?"

    ai_response = (
        "Diversification means spreading your investments "
        "across different assets or sectors so that the impact "
        "of poor performance in one investment can be reduced."
    )

    # ------------------------------------------------------------
    # 1. Evaluating response
    # ------------------------------------------------------------

    print("\n1. Evaluating response with Gemini...")

    evaluation = evaluator.evaluate(
        feature="jargon",
        prompt=prompt,
        response=ai_response
    )

    print(
        "Gemini Score:",
        evaluation["score"],
        "/ 5"
    )

    print(
        "Gemini Reason:",
        evaluation["reason"]
    )

    # ------------------------------------------------------------
    # 2. Creating quality record
    # ------------------------------------------------------------

    print("\n2. Creating quality record...")

    record = storage.add_evaluation(
        evaluation=evaluation,
        quality_tracker=tracker,
        user_id="U001",
        response_id="R001"
    )

    print("Record created successfully.")

    # ------------------------------------------------------------
    # 3. Display stored record
    # ------------------------------------------------------------

    print("\n3. Stored Record")

    print(
        "Feature:",
        record["feature"]
    )

    print(
        "Score:",
        record["score"],
        "/ 5"
    )

    print(
        "Reason:",
        record["reason"]
    )

    print(
        "User ID:",
        record["user_id"]
    )

    print(
        "Response ID:",
        record["response_id"]
    )

    # ------------------------------------------------------------
    # 4. Storage information
    # ------------------------------------------------------------

    print("\n4. Storage Information")

    print(
        "File:",
        storage.get_file_path()
    )

    records = storage.get_records()

    print(
        "Total stored evaluations:",
        len(records)
    )

    # ------------------------------------------------------------
    # 5. Latest stored evaluation
    # ------------------------------------------------------------

    print("\n5. Latest Stored Evaluation")

    if records:

        print(
            json.dumps(
                records[-1],
                indent=4
            )
        )

    else:

        print("No evaluations found.")

    # ------------------------------------------------------------
    # 6. Right-to-deletion
    # ------------------------------------------------------------

    print("\n6. Right-to-Deletion")

    print(
        "delete_user_records() is available "
        "for account deletion."
    )

    print("\n" + "=" * 60)

    print(
        "QUALITY STORAGE TEST COMPLETED."
    )

    print("=" * 60)