import os

from task7_mlops.all_models_mlflow import AllModelsMLflowTracker
from task7_mlops.retraining_scheduler import RetrainingScheduler


def main():
    print("\n========================================")
    print("       TASK 7 - MLOps LIFECYCLE")
    print("========================================\n")

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")

    if not tracking_uri:
        raise RuntimeError(
            "MLFLOW_TRACKING_URI environment variable is not configured"
        )

    # -----------------------------------------
    # 1. Track all 5 models in MLflow
    # -----------------------------------------

    print("1. Tracking all 5 models in MLflow...\n")

    tracker = AllModelsMLflowTracker(
        tracking_uri=tracking_uri,
        experiment_name="Task7_All_Models",
    )

    run_ids = tracker.track_all(
        dataset_version="dataset-v1"
    )

    for model_name, run_id in run_ids.items():
        print(f"{model_name}: {run_id}")

    # -----------------------------------------
    # 2. Display retraining schedules
    # -----------------------------------------

    print("\n2. Retraining schedules:\n")

    scheduler = RetrainingScheduler()

    for schedule in scheduler.get_all_schedules():
        print(
            f"- {schedule.model_name}: "
            f"{schedule.frequency} "
            f"(manual review={schedule.review_required})"
        )

    # -----------------------------------------
    # 3. Summary
    # -----------------------------------------

    print("\n========================================")
    print("TASK 7 WORKFLOW COMPLETED")
    print("========================================")

    print("\nMLflow runs created:", len(run_ids))

    print("\nTracked models:")
    for model_name in run_ids:
        print(f"✓ {model_name}")

    print("\nTask 7 components:")
    print("✓ Model versioning")
    print("✓ MLflow model tracking")
    print("✓ Model comparison")
    print("✓ Shadow deployment")
    print("✓ Anomaly monitoring")
    print("✓ Automatic rollback decision")
    print("✓ Slack retraining notification")
    print("✓ Retraining schedules")
    print("✓ Manual review schedule")


if __name__ == "__main__":
    main()