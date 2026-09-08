import os
import mlflow

from fund_training import train_fund_recommendation_model
from fund_deployment import validate_and_deploy


# ============================================================
# CONFIGURATION
# ============================================================

EXPERIMENT_NAME = "PaiseWise-Fund-Retraining"

NEW_MODEL_PATH = (
    "../data/funds/models/"
    "new_fund_recommendation_model.pkl"
)


# ============================================================
# FUND RETRAINING PIPELINE
# ============================================================

def run_fund_retraining():

    print("\n" + "=" * 60)
    print("PAISEWISE FUND RECOMMENDATION RETRAINING")
    print("=" * 60)

    print("\nStarting weekly fund retraining process...")

    # --------------------------------------------------------
    # Set MLflow experiment
    # --------------------------------------------------------

    mlflow.set_experiment(
        EXPERIMENT_NAME
    )

    # --------------------------------------------------------
    # Start MLflow run
    # --------------------------------------------------------

    with mlflow.start_run(
        run_name="weekly_fund_retraining"
    ):

        print("\nMLflow run started.")

        # ----------------------------------------------------
        # Step 1: Train new fund recommendation model
        # ----------------------------------------------------

        training_result = (
            train_fund_recommendation_model()
        )

        # ----------------------------------------------------
        # Step 2: Log scoring weights
        # ----------------------------------------------------

        weights = training_result["weights"]

        mlflow.log_metric(
            "return_weight",
            weights["return_weight"]
        )

        mlflow.log_metric(
            "risk_weight",
            weights["risk_weight"]
        )

        mlflow.log_metric(
            "consistency_weight",
            weights["consistency_weight"]
        )

        # ----------------------------------------------------
        # Step 3: Log model information
        # ----------------------------------------------------

        mlflow.log_param(
            "model_type",
            "Dynamic Fund Scoring Model"
        )

        mlflow.log_param(
            "retraining_frequency",
            "Weekly"
        )

        mlflow.log_param(
            "retraining_day",
            "Sunday"
        )

        mlflow.log_param(
            "retraining_time",
            "02:00 AM"
        )

        mlflow.log_param(
            "evaluation_metric",
            "ranking_accuracy"
        )

        mlflow.log_param(
            "deployment_threshold",
            "2%"
        )

        # ----------------------------------------------------
        # Step 4: Log model artifact
        # ----------------------------------------------------

        print("\nLogging model artifact to MLflow...")

        if os.path.exists(
            NEW_MODEL_PATH
        ):

            try:

                mlflow.log_artifact(
                    NEW_MODEL_PATH,
                    artifact_path="fund_model"
                )

                print(
                    "Fund model artifact "
                    "logged successfully."
                )

            except Exception as e:

                print(
                    "Warning: Model artifact "
                    "logging failed."
                )

                print(
                    "Reason:",
                    e
                )

        else:

            print(
                "Warning: New fund model "
                "file not found."
            )

        # ----------------------------------------------------
        # Step 5: Validate and deploy
        # ----------------------------------------------------

        print(
            "\nValidating new fund "
            "recommendation model..."
        )

        deployment_result = validate_and_deploy(
            training_result["model"]
        )

        # ----------------------------------------------------
        # Step 6: Log deployment result
        # ----------------------------------------------------

        mlflow.log_param(
            "deployment_decision",
            deployment_result["decision"]
        )

        mlflow.log_metric(
            "current_score",
            deployment_result["current_score"]
        )

        mlflow.log_metric(
            "new_score",
            deployment_result["new_score"]
        )

        mlflow.log_metric(
            "improvement",
            deployment_result["improvement"]
        )

        # ----------------------------------------------------
        # Final result
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("FUND RETRAINING PIPELINE COMPLETED")
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
            "Current Score:",
            f'{deployment_result["current_score"]:.2%}'
        )

        print(
            "New Score:",
            f'{deployment_result["new_score"]:.2%}'
        )

        print(
            "Improvement:",
            f'{deployment_result["improvement"]:.2%}'
        )

        print("\nMLflow run completed.")


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    run_fund_retraining()