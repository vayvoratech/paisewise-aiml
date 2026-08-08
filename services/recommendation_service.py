from models.recommendation import RecommendationRequest
from services.fund_catalogue import get_catalogue
from services.result_formatter import format_recommendations
from services.explanation_generator import generate_fund_explanation

def recommend_funds(request: RecommendationRequest):

    funds = get_catalogue()

    recommendations = []

    for fund in funds:

        score = 0

        # Risk profile match
        if fund.get("risk_level") and fund["risk_level"].lower() == request.riskProfile.lower():
            score += 50

        # Historical returns
        score += float(fund.get("return_1y") or 0)

        # Long-term investment bonus
        if request.investmentHorizon >= 5:
            score += 20

        # Higher investment amount bonus
        if request.investmentAmount >= 100000:
            score += 10

        recommendations.append({

            # Store complete fund data for formatter
            "fund": fund,

            "score": score,

            "reason": generate_fund_explanation(
                fund,
                request.riskProfile
            )

        })

    # Sort by score (highest first)
    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Return top 3 formatted recommendations
    return format_recommendations(
        recommendations[:3]
    )