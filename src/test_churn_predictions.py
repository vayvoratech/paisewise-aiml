import joblib
import pandas as pd
from pathlib import Path


# ==================================================
# Project Paths
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "data"
    / "churn"
    / "models"
    / "new_churn_model.pkl"
)


# ==================================================
# Model Features
# ==================================================

FEATURES = [
    "d7_lesson_count",
    "d7_quiz_count",
    "d7_paper_trade_count",
    "d7_streak_days",
    "d7_xp_earned",
    "d7_notification_open_rate",
    "onboarding_goal_set",
    "kyc_completed_d7",
    "first_paper_trade_d7",
]


# ==================================================
# Risk Level Function
# ==================================================

def get_risk_level(probability):

    if probability >= 0.70:
        return "High"

    elif probability >= 0.40:
        return "Medium"

    else:
        return "Low"


# ==================================================
# Churn Prediction Test
# ==================================================

def test_churn_predictions():

    print("\n" + "=" * 60)
    print("CHURN PREDICTION TEST")
    print("=" * 60)

    # --------------------------------------------------
    # Check model exists
    # --------------------------------------------------

    print("\nModel path:")
    print(MODEL_PATH)

    assert MODEL_PATH.exists(), (
        f"Churn model not found: {MODEL_PATH}"
    )

    # --------------------------------------------------
    # Load model
    # --------------------------------------------------

    model = joblib.load(str(MODEL_PATH))

    print("\nChurn model loaded successfully.")

    # --------------------------------------------------
    # LOW-RISK USER
    # --------------------------------------------------

    low_risk = pd.DataFrame([
        {
            "d7_lesson_count": 20,
            "d7_quiz_count": 15,
            "d7_paper_trade_count": 10,
            "d7_streak_days": 7,
            "d7_xp_earned": 500,
            "d7_notification_open_rate": 0.95,
            "onboarding_goal_set": 1,
            "kyc_completed_d7": 1,
            "first_paper_trade_d7": 1,
        }
    ])

    # --------------------------------------------------
    # HIGH-RISK USER
    # --------------------------------------------------

    high_risk = pd.DataFrame([
        {
            "d7_lesson_count": 0,
            "d7_quiz_count": 0,
            "d7_paper_trade_count": 0,
            "d7_streak_days": 0,
            "d7_xp_earned": 0,
            "d7_notification_open_rate": 0.0,
            "onboarding_goal_set": 0,
            "kyc_completed_d7": 0,
            "first_paper_trade_d7": 0,
        }
    ])

    # --------------------------------------------------
    # Validate feature columns
    # --------------------------------------------------

    assert list(low_risk.columns) == FEATURES

    assert list(high_risk.columns) == FEATURES

    print("\nFeature validation passed.")

    # --------------------------------------------------
    # LOW-RISK PREDICTION
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("LOW RISK USER")
    print("=" * 60)

    low_prediction = model.predict(low_risk)

    low_probability = model.predict_proba(low_risk)

    print("Prediction:", low_prediction)
    print("Probability:", low_probability)

    # --------------------------------------------------
    # HIGH-RISK PREDICTION
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("HIGH RISK USER")
    print("=" * 60)

    high_prediction = model.predict(high_risk)

    high_probability = model.predict_proba(high_risk)

    print("Prediction:", high_prediction)
    print("Probability:", high_probability)

    # --------------------------------------------------
    # Extract churn probabilities
    # --------------------------------------------------

    low_churn_probability = float(
        low_probability[0][1]
    )

    high_churn_probability = float(
        high_probability[0][1]
    )

    # --------------------------------------------------
    # Risk levels
    # --------------------------------------------------

    low_risk_level = get_risk_level(
        low_churn_probability
    )

    high_risk_level = get_risk_level(
        high_churn_probability
    )

    # --------------------------------------------------
    # Validate probabilities
    # --------------------------------------------------

    assert 0.0 <= low_churn_probability <= 1.0

    assert 0.0 <= high_churn_probability <= 1.0

    # --------------------------------------------------
    # Validate risk levels
    # --------------------------------------------------

    assert low_risk_level in [
        "Low",
        "Medium",
        "High",
    ]

    assert high_risk_level in [
        "Low",
        "Medium",
        "High",
    ]

    # --------------------------------------------------
    # Final results
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL CHURN RESULTS")
    print("=" * 60)

    print(
        f"\nLow-risk user churn probability: "
        f"{low_churn_probability:.4f}"
    )

    print(
        f"Low-risk user risk level: "
        f"{low_risk_level}"
    )

    print(
        f"\nHigh-risk user churn probability: "
        f"{high_churn_probability:.4f}"
    )

    print(
        f"High-risk user risk level: "
        f"{high_risk_level}"
    )

    print("\n" + "=" * 60)
    print("CHURN PREDICTION TEST PASSED")
    print("=" * 60)
