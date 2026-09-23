from model_deployment import deploy_new_model


def run_retraining_pipeline():

    print("=" * 60)
    print("AUTOMATED FUND MODEL RETRAINING PIPELINE")
    print("=" * 60)

    print("\nStarting weekly retraining process...")

    result = deploy_new_model()

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED")
    print("=" * 60)

    print("Status:", result["status"])
    print("Decision:", result["decision"])
    print(
        "Improvement:",
        f'{result["improvement"]:.2%}'
    )


if __name__ == "__main__":
    run_retraining_pipeline()