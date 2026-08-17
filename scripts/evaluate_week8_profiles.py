import argparse
import json
from pathlib import Path

from app.services.fund_recommendation import get_top_recommendations


def evaluate_profiles(profiles_file: str, funds_file: str, output_file: str):
    profiles = json.loads(Path(profiles_file).read_text(encoding="utf-8"))
    funds = json.loads(Path(funds_file).read_text(encoding="utf-8"))

    results = []

    for profile in profiles:
        recommendations = get_top_recommendations(
            funds=funds,
            user_risk=profile["risk_profile"],
            investment_horizon=profile["investment_horizon"],
            investment_amount=profile["investment_amount"],
            user_goal=profile["goal"],
        )

        results.append({
            "profile": profile,
            "recommendations": [
                {
                    "scheme_name": item["fund"].get("scheme_name"),
                    "score": item["score"],
                    "category": item["fund"].get("category"),
                    "amc_name": item["fund"].get("amc_name"),
                    "expense_ratio": item["fund"].get("expense_ratio"),
                    "is_tax_saver": item["fund"].get("is_tax_saver"),
                }
                for item in recommendations
            ],
        })

    Path(output_file).write_text(
        json.dumps(results, indent=2, default=str),
        encoding="utf-8",
    )

    print(f"Evaluated {len(results)} profiles.")
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("profiles_file")
    parser.add_argument("funds_file")
    parser.add_argument("--output", default="data/week8_recommendation_results.json")
    args = parser.parse_args()
    evaluate_profiles(args.profiles_file, args.funds_file, args.output)
