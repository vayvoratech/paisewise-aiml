import os
import shutil

from churn_validation import validate_models

# Model paths

MODEL_DIR = "../data/churn/models"

CURRENT_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "current_churn_model.pkl"
)

NEW_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "new_churn_model.pkl"
)

BACKUP_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "previous_churn_model.pkl"
)

# Deploy New Model

def deploy_new_model(training_result):

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    # Validate current vs new model

    validation = validate_models(
        training_result
    )

    print("\n" + "=" * 60)
    print("CHURN MODEL DEPLOYMENT")
    print("=" * 60)

    # Reject new model

    if not validation["deploy"]:

        print(
            "New model is not better."
        )

        print(
            "Keeping current model."
        )

        return {
            "status": "rejected",
            "decision": "KEEP_CURRENT_MODEL",
            "current_f1": validation["current_f1"],
            "new_f1": validation["new_f1"],
            "improvement": validation["improvement"]
        }


    # Backup current model

    if os.path.exists(
        CURRENT_MODEL_PATH
    ):

        shutil.copy2(
            CURRENT_MODEL_PATH,
            BACKUP_MODEL_PATH
        )

        print(
            "Previous model backed up."
        )

    # Deploy new model

    shutil.copy2(
        NEW_MODEL_PATH,
        CURRENT_MODEL_PATH
    )

    print(
        "New churn model deployed successfully."
    )

    return {
        "status": "deployed",
        "decision": "DEPLOY_NEW_MODEL",
        "current_f1": validation["current_f1"],
        "new_f1": validation["new_f1"],
        "improvement": validation["improvement"]
    }