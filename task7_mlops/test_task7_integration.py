import os

from task7_mlops.model_lifecycle import ModelLifecycle
from task7_mlops.metrics_tracker import MetricsTracker
from task7_mlops.mlflow_metrics_tracker import MLflowMetricsTracker
from task7_mlops.model_comparison import ModelComparison
from task7_mlops.retraining_scheduler import RetrainingScheduler


def main():
    print("\n=== TASK 7 INTEGRATION TEST ===\n")

    # 1. Create model versions
    lifecycle = ModelLifecycle(rollback_threshold=0.05)

    version = lifecycle.create_version(
        model_name="Churn Score",
        version="v2",
        metrics={
            "accuracy": 0.87,
            "precision": 0.84,
        },
        dataset_version="dataset-v2",
    )

    print("1. Model Version:")
    print(version)

    # 2. Create metrics
    metrics = MetricsTracker.create_metrics(
        model_name="Churn Score",
        version="v2",
        metrics={
            "accuracy": 0.87,
            "precision": 0.84,
        },
    )

    print("\n2. Metrics:")
    print(metrics)

    # 3. Compare previous and new model
    comparison = ModelComparison.compare(
        model_name="Churn Score",
        previous_version="v1",
        new_version="v2",
        previous_metric=0.82,
        new_metric=0.87,
    )

    print("\n3. Model Comparison:")
    print(comparison)

    # 4. Track metrics in MLflow
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")

    if tracking_uri:
        tracker = MLflowMetricsTracker(tracking_uri)

        run_id = tracker.log_metrics(
            metrics,
            dataset_version="dataset-v2",
        )

        print("\n4. MLflow Run:")
        print(run_id)
    else:
        print("\n4. MLflow:")
        print("MLFLOW_TRACKING_URI is not configured")

    # 5. Test automatic rollback
    rollback = lifecycle.evaluate_rollback(
        total_users=100,
        anomalous_users=6,
        current_version="v2",
        previous_version="v1",
    )

    print("\n5. Rollback Decision:")
    print(rollback)

    # 6. Retraining schedule
    scheduler = RetrainingScheduler()

    print("\n6. Retraining Schedules:")

    for schedule in scheduler.get_all_schedules():
        print(
            f"{schedule.model_name}: "
            f"{schedule.frequency}, "
            f"review_required={schedule.review_required}"
        )

    print("\n=== TASK 7 INTEGRATION TEST COMPLETE ===")


if __name__ == "__main__":
    main()