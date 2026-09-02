def format_recommendations(recommendations, run_id):
    formatted_results = []

    for item in recommendations:

        fund = item["fund"]

        formatted_results.append({
            "schemeCode": fund["scheme_code"],
            "fundName": fund["scheme_name"],

            "score": item["score"],

            "reason": item["reason"],

            "keyMetrics": {
                "riskLevel": fund.get("risk_level"),
                "category": fund.get("category"),
                "return1Y": fund.get("return_1y"),
                "return3Y": fund.get("return_3y"),
                "return5Y": fund.get("return_5y"),
                "expenseRatio": fund.get("expense_ratio"),
                "aumCrore": fund.get("aum_crore"),
            }
        })

    return {
        "recommendationRunId": run_id,
        "recommendedFunds": formatted_results
    }