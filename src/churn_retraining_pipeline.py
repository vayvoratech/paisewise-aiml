import mlflow

from churn_deployment import deploy_new_model
from churn_training import train_churn_model


EXPERIMENT_NAME = "PaiseWise-Churn-Retraining"


def run_churn_retraining():

    print("=" * 60)
    print("PAISEWISE CHURN MODEL RETRAINING")
    print("=" * 60)

    print("\nStarting monthly retraining process...")

    # --------------------------------------------------
    # MLflow experiment
    # --------------------------------------------------

    mlflow.set_experiment(
        EXPERIMENT_NAME
    )

    # --------------------------------------------------
    # Start MLflow run
    # --------------------------------------------------

    with mlflow.start_run(
        run_name="monthly_churn_retraining"
    ):

        # --------------------------------------------------
        # Train model
        # --------------------------------------------------

        training_result = train_churn_model()

        # --------------------------------------------------
        # Log parameters
        # --------------------------------------------------

        mlflow.log_param(
            "model",
            "XGBClassifier"
        )

        mlflow.log_param(
            "n_estimators",
            100
        )

        mlflow.log_param(
            "max_depth",
            4
        )

        mlflow.log_param(
            "learning_rate",
            0.1
        )

        mlflow.log_param(
            "test_size",
            0.20
        )

        # Log training metrics
        # --------------------------------------------------

        mlflow.log_metric(
            "accuracy",
            training_result["accuracy"]
        )

        mlflow.log_metric(
            "precision",
            training_result["precision"]
        )

        mlflow.log_metric(
            "recall",
            training_result["recall"]
        )

        mlflow.log_metric(
            "f1_score",
            training_result["f1"]
        )

        # --------------------------------------------------
        # Validate and deploy
        # --------------------------------------------------

        deployment_result = deploy_new_model(
            training_result
        )

        # --------------------------------------------------
        # Log deployment result
        # --------------------------------------------------

        mlflow.log_param(
            "deployment_decision",
            deployment_result["decision"]
        )

        mlflow.log_metric(
            "current_f1",
            deployment_result["current_f1"]
        )

        mlflow.log_metric(
            "new_f1",
            deployment_result["new_f1"]
        )

        mlflow.log_metric(
            "improvement",
            deployment_result["improvement"]
        )

        # --------------------------------------------------
        # Final output
        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("RETRAINING PIPELINE COMPLETED")
        print("=" * 60)

        print(
            "Status:",
            deployment_result["status"]
        )

        print(
            "Decision:",
            deployment_result["decision"]
        )

        print(
            "Improvement:",
            f'{deployment_result["improvement"]:.2%}'
        )


if __name__ == "__main__":

    run_churn_retraining()