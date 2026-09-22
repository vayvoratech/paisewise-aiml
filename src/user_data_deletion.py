import json

from pathlib import Path

from ai_experimentation.experiment_logger import (
    delete_user_experiment_logs
)

from ai_quality_monitoring.quality_storage import (
    QualityStorage
)

from ai_quality_monitoring.feedback_storage import (
    FeedbackStorage
)

from llm_cost_management.cost_storage import (
    CostStorage
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

BACKUP_COST_FILE = (
    BASE_DIR
    / "llm_cost_management"
    / "cost_records_backup.json"
)


# ============================================================
# DELETE USER DATA FROM COST BACKUP
# ============================================================

def delete_user_backup_cost_records(user_id):

    if not BACKUP_COST_FILE.exists():

        return 0

    try:

        with open(
            BACKUP_COST_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            records = json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):

        return 0

    if not isinstance(records, list):

        return 0

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
        BACKUP_COST_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            remaining_records,
            file,
            indent=4,
            default=str
        )

    return deleted_count


# ============================================================
# DELETE ALL USER AI DATA
# ============================================================

def delete_user_ai_data(user_id):
    """
    Delete all AI-generated data associated
    with the specified user.
    """

    if not user_id:

        raise ValueError(
            "user_id is required for deletion."
        )

    # --------------------------------------------------------
    # 1. Experiment logs
    # --------------------------------------------------------

    experiment_deleted = (
        delete_user_experiment_logs(
            user_id
        )
    )

    # --------------------------------------------------------
    # 2. Quality evaluations
    # --------------------------------------------------------

    quality_storage = QualityStorage()

    quality_deleted = (
        quality_storage.delete_user_records(
            user_id
        )
    )

    # --------------------------------------------------------
    # 3. User feedback
    # --------------------------------------------------------

    feedback_storage = FeedbackStorage()

    feedback_deleted = (
        feedback_storage.delete_user_records(
            user_id
        )
    )

    # --------------------------------------------------------
    # 4. LLM cost records
    # --------------------------------------------------------

    cost_storage = CostStorage()

    cost_deleted = (
        cost_storage.delete_user_records(
            user_id
        )
    )

    # --------------------------------------------------------
    # 5. Backup LLM cost records
    # --------------------------------------------------------

    backup_cost_deleted = (
        delete_user_backup_cost_records(
            user_id
        )
    )

    # --------------------------------------------------------
    # Return deletion summary
    # --------------------------------------------------------

    return {
        "user_id": user_id,
        "deleted": {
            "experiment_logs": experiment_deleted,
            "quality_evaluations": quality_deleted,
            "feedback": feedback_deleted,
            "cost_records": cost_deleted,
            "cost_records_backup": backup_cost_deleted
        }
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("USER AI DATA DELETION SERVICE")
    print("=" * 60)

    print(
        "\nService loaded successfully."
    )

    print(
        "\nNo real user data was deleted."
    )

    print(
        "Use a dedicated test user before "
        "testing the deletion process."
    )

    print("\n" + "=" * 60)