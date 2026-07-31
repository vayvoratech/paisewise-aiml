from models.recommendation import RecommendationRequest

# Mock fund data
funds = [
    {
        "fundName": "Axis Bluechip Fund",
        "risk": "Moderate",
        "returns": 15
    },
    {
        "fundName": "Parag Parikh Flexi Cap",
        "risk": "Moderate",
        "returns": 18
    },
    {
        "fundName": "Nippon India Small Cap Fund",
        "risk": "High",
        "returns": 24
    },
    {
        "fundName": "HDFC Balanced Advantage Fund",
        "risk": "Low",
        "returns": 12
    },
    {
        "fundName": "ICICI Prudential Flexi Cap Fund",
        "risk": "Moderate",
        "returns": 16
    }
]


def recommend_funds(request: RecommendationRequest):
    recommendations = []

    for fund in funds:
        score = 0

        # Risk profile match
        if fund["risk"].lower() == request.riskProfile.lower():
            score += 50

        # Historical returns
        score += fund["returns"]

        # Long-term investment bonus
        if request.investmentHorizon >= 5:
            score += 20

        # Higher investment amount bonus
        if request.investmentAmount >= 100000:
            score += 10

        recommendations.append({
            "fundName": fund["fundName"],
            "score": score,
            "reason": f"Suitable for {request.riskProfile.lower()} risk investors"
        })

    # Sort by score (highest first)
    recommendations.sort(key=lambda x: x["score"], reverse=True)

    # Return top 3 recommendations
    return {
        "recommendedFunds": recommendations[:3]
    }