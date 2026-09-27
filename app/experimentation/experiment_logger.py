
import json
from pathlib import Path
from datetime import datetime


# ============================================================
# LOG FILE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

LOG_FILE = BASE_DIR / "experiment_logs.json"


# ============================================================
# CREATE LOG FILE IF IT DOES NOT EXIST
# ============================================================

def _initialize_log_file():

    if not LOG_FILE.exists():

        with open(LOG_FILE, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


# ============================================================
# LOAD EXISTING LOGS
# ============================================================

def _load_logs():

    _initialize_log_file()

    try:

        with open(LOG_FILE, "r", encoding="utf-8") as file:
            logs = json.load(file)

        if isinstance(logs, list):
            return logs

        return []

    except (json.JSONDecodeError, OSError):

        return []


# ============================================================
# LOG AI EXPERIMENT RESPONSE
# ============================================================

def log_experiment_response(
    user_id: str,
    feature_name: str,
    experiment_id: str,
    variant_id: str,
    quality_score: float | None = None,
    success: bool = True,
    response_time_ms: float | None = None
):

    # Load existing records
    logs = _load_logs()

    # Create experiment record
    record = {
        "timestamp": datetime.now().isoformat(),

        "user_id": user_id,

        "feature": feature_name,

        "experiment_id": experiment_id,

        "variant_id": variant_id,

        "quality_score": quality_score,

        "success": success,

        "response_time_ms": response_time_ms
    }

    # Add new record
    logs.append(record)

    # Save updated records
    with open(LOG_FILE, "w", encoding="utf-8") as file:

        json.dump(
            logs,
            file,
            indent=4
        )

    return record


# ============================================================
# GET ALL EXPERIMENT LOGS
# ============================================================

def get_experiment_logs():

    return _load_logs()


# ============================================================
# DELETE ALL EXPERIMENT LOGS FOR A USER
# ============================================================

def delete_user_experiment_logs(user_id: str):

    logs = _load_logs()

    original_count = len(logs)

    remaining_logs = [
        log
        for log in logs
        if log.get("user_id") != user_id
    ]

    deleted_count = original_count - len(remaining_logs)

    with open(LOG_FILE, "w", encoding="utf-8") as file:

        json.dump(
            remaining_logs,
            file,
            indent=4
        )

    return deleted_count

# ============================================================
# GET LOG COUNT
# ============================================================

def get_log_count():

    logs = _load_logs()

    return len(logs)


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PaiseWise AI Experiment Logger Test")
    print("=" * 60)

    # --------------------------------------------------------
    # Test record 1
    # --------------------------------------------------------

    record_1 = log_experiment_response(
        user_id="U001",
        feature_name="jargon",
        experiment_id="jargon_prompt_test_01",
        variant_id="A",
        quality_score=4.5,
        success=True,
        response_time_ms=850
    )

    print("\nLogged Record 1:")
    print(record_1)

    # --------------------------------------------------------
    # Test record 2
    # --------------------------------------------------------

    record_2 = log_experiment_response(
        user_id="U002",
        feature_name="jargon",
        experiment_id="jargon_prompt_test_01",
        variant_id="B",
        quality_score=3.8,
        success=True,
        response_time_ms=920
    )

    print("\nLogged Record 2:")
    print(record_2)

    # --------------------------------------------------------
    # Test record 3
    # --------------------------------------------------------

    record_3 = log_experiment_response(
        user_id="U003",
        feature_name="jargon",
        experiment_id="jargon_prompt_test_01",
        variant_id="B",
        quality_score=3.2,
        success=False,
        response_time_ms=1100
    )

    print("\nLogged Record 3:")
    print(record_3)

    # --------------------------------------------------------
    # Display total records
    # --------------------------------------------------------

    print("\nTotal experiment logs:")

    print(get_log_count())

    # --------------------------------------------------------
    # Display all logs
    # --------------------------------------------------------

    print("\nAll experiment logs:")
    print("-" * 60)

    for log in get_experiment_logs():

        print(log)

    print("\n" + "=" * 60)
    print("Experiment logger test completed.")
    print("=" * 60)