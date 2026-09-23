import json
import os
import shutil

from model_validation import validate_models
from fund_data import fetch_latest_fund_data
from fund_scoring import calculate_scoring_weights


MODEL_DIR = "../data/fund/models"

CURRENT_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "current_model.json"
)

NEW_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "new_model.json"
)

BACKUP_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "previous_model.json"
)


def save_model(
    weights,
    performance,
    path
):

    model = {
        "weights": weights,
        "performance": round(
            performance,
            4
        )
    }

    with open(path, "w") as file:

        json.dump(
            model,
            file,
            indent=4
        )


def deploy_new_model():

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    validation_result = validate_models()

    improvement = validation_result[
        "improvement"
    ]

    print(
        f"\nModel improvement: "
        f"{improvement:.2%}"
    )

    if improvement <= 0.02:

        print(
            "New model did not improve "
            "by more than 2%."
        )

        print(
            "Keeping current model."
        )

        return {
            "status": "rejected",
            "decision": "KEEP_CURRENT_MODEL",
            "improvement": improvement
        }

    fund_data = fetch_latest_fund_data()

    new_weights = calculate_scoring_weights(
        fund_data
    )

    new_performance = validation_result[
        "new_model_performance"
    ]

    save_model(
        new_weights,
        new_performance,
        NEW_MODEL_PATH
    )

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

    shutil.copy2(
        NEW_MODEL_PATH,
        CURRENT_MODEL_PATH
    )

    print(
        "New model deployed successfully."
    )

    return {
        "status": "deployed",
        "decision": "DEPLOY_NEW_MODEL",
        "improvement": improvement
    }

if __name__ == "__main__":
    result = deploy_new_model()

    print("\nFinal Result:")
    print(result)