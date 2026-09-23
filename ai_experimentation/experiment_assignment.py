# ============================================================
# PaiseWise AI Experimentation
# Experiment Assignment Service
# ============================================================

import hashlib


# ============================================================
# Active Experiments
# ============================================================

EXPERIMENTS = {
    "jargon": {
        "experiment_id": "jargon_prompt_test_01",
        "variants": ["A", "B"],
        "status": "running"
    },

    "portfolio_diversification": {
        "experiment_id": "portfolio_prompt_test_01",
        "variants": ["A", "B"],
        "status": "running"
    },

    "news_classify": {
        "experiment_id": "news_classification_test_01",
        "variants": ["A", "B"],
        "status": "running"
    }
}


# ============================================================
# Experiment Assignment
# ============================================================

def get_experiment_assignment(
    user_id: str,
    feature_name: str
):
    """
    Assign a user to an A/B experiment variant.

    The assignment is deterministic.

    This means the same user + feature combination
    will always receive the same variant while the
    experiment configuration remains unchanged.
    """

    user_id = str(user_id).strip()
    feature_name = str(feature_name).strip()

    # --------------------------------------------------------
    # Validate user ID
    # --------------------------------------------------------

    if not user_id:
        raise ValueError(
            "user_id is required."
        )

    # --------------------------------------------------------
    # Validate feature
    # --------------------------------------------------------

    if not feature_name:
        raise ValueError(
            "feature_name is required."
        )

    # --------------------------------------------------------
    # Check whether experiment exists
    # --------------------------------------------------------

    experiment = EXPERIMENTS.get(
        feature_name
    )

    if experiment is None:
        return {
            "user_id": user_id,
            "feature": feature_name,
            "experiment_id": None,
            "variant_id": None,
            "status": "not_configured",
            "message": (
                "No active experiment is configured "
                "for this feature."
            )
        }

    # --------------------------------------------------------
    # Check experiment status
    # --------------------------------------------------------

    if experiment["status"] != "running":
        return {
            "user_id": user_id,
            "feature": feature_name,
            "experiment_id": experiment[
                "experiment_id"
            ],
            "variant_id": None,
            "status": experiment["status"],
            "message": (
                "Experiment is not currently running."
            )
        }

    # --------------------------------------------------------
    # Create deterministic assignment key
    # --------------------------------------------------------

    assignment_key = (
        f"{experiment['experiment_id']}:"
        f"{feature_name}:"
        f"{user_id}"
    )

    # --------------------------------------------------------
    # Generate stable hash
    # --------------------------------------------------------

    hash_value = hashlib.sha256(
        assignment_key.encode("utf-8")
    ).hexdigest()

    # Convert hash to integer
    hash_number = int(
        hash_value,
        16
    )

    # --------------------------------------------------------
    # Assign variant
    #
    # Even hash  -> A
    # Odd hash   -> B
    # --------------------------------------------------------

    variant_index = (
        hash_number %
        len(experiment["variants"])
    )

    variant_id = experiment[
        "variants"
    ][variant_index]

    # --------------------------------------------------------
    # Return assignment
    # --------------------------------------------------------

    return {
        "user_id": user_id,
        "feature": feature_name,
        "experiment_id": experiment[
            "experiment_id"
        ],
        "variant_id": variant_id,
        "status": "assigned"
    }


# ============================================================
# Simple Local Test
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PaiseWise AI Experiment Assignment")
    print("=" * 60)

    test_users = [
        "U001",
        "U002",
        "U003",
        "U004",
        "U005"
    ]

    print()
    print("Jargon experiment assignments:")
    print()

    for user_id in test_users:

        result = get_experiment_assignment(
            user_id=user_id,
            feature_name="jargon"
        )

        print(result)

    print()
    print("Consistency test:")
    print()

    first_result = get_experiment_assignment(
        user_id="U001",
        feature_name="jargon"
    )

    second_result = get_experiment_assignment(
        user_id="U001",
        feature_name="jargon"
    )

    print(
        "First assignment:",
        first_result["variant_id"]
    )

    print(
        "Second assignment:",
        second_result["variant_id"]
    )

    print(
        "Same variant:",
        first_result["variant_id"]
        == second_result["variant_id"]
    )

    print()
    print("=" * 60)
    print("Experiment assignment test completed.")
    print("=" * 60)