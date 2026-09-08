import os
import mlflow

from churn_training import train_churn_model

from churn_deployment import deploy_new_model


# ============================================================
# MLFLOW EXPERIMENT
# ============================================================

EXPERIMENT_NAME = "PaiseWise-Churn-Retraining"


# ============================================================
# MODEL ARTIFACT
# ============================================================

NEW_MODEL_PATH = "../data/churn/models/new_churn_model.pkl"


# ============================================================
# RETRAINING PIPELINE
# ============================================================

def run_churn_retraining():

    print("\n" + "=" * 60)

    print(
        "PAISEWISE CHURN MODEL RETRAINING"
    )

    print("=" * 60)

    print(
        "\nStarting monthly retraining process..."
    )

    # ========================================================
    # MLFLOW EXPERIMENT
    # ========================================================

    mlflow.set_experiment(

        EXPERIMENT_NAME

    )

    # ========================================================
    # START MLFLOW RUN
    # ========================================================

    with mlflow.start_run(

        run_name="monthly_churn_retraining"

    ):

        print(
            "\nMLflow run started."
        )

        # ====================================================
        # TRAIN MODEL
        # ====================================================

        training_result = train_churn_model()

        # ====================================================
        # LOG PARAMETERS
        # ====================================================

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

        mlflow.log_param(

            "retraining_window",

            "90_days_when_date_available"

        )

        # ====================================================
        # LOG TRAINING METRICS
        # ====================================================

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

        # ====================================================
        # LOG MODEL AS ARTIFACT
        # ====================================================

        print(
            "\nLogging model to MLflow..."
        )

        if os.path.exists(NEW_MODEL_PATH):

            try:

                mlflow.log_artifact(

                    NEW_MODEL_PATH,

                    artifact_path="churn_model"

                )

                print(
                    "Model artifact logged successfully."
                )

            except Exception as e:

                print(
                    "Warning: Model artifact logging failed."
                )

                print(
                    "Reason:",
                    e
                )

        else:

            print(
                "Warning: New model file not found."
            )

        # ====================================================
        # MODEL COMPARISON + DEPLOYMENT
        # ====================================================

        deployment_result = deploy_new_model(

            training_result

        )

        # ====================================================
        # LOG DEPLOYMENT DECISION
        # ========================================================

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

        # ====================================================
        # FINAL OUTPUT
        # ====================================================

        print("\n" + "=" * 60)

        print(
            "RETRAINING PIPELINE COMPLETED"
        )

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

        print(
            "\nMLflow run completed."
        )


# ============================================================
# MANUAL EXECUTION
# ============================================================

if __name__ == "__main__":

    run_churn_retraining()