from models.recommendation import RecommendationRequest
from services.fund_catalogue import get_catalogue
from services.result_formatter import format_recommendations
from services.explanation_generator import generate_fund_explanation
from services.recommendation_ab import assign_recommendation_variant
from database.database import get_db_connection
from services.recommendation_cache import (
    get_cached_recommendation,
    cache_recommendation,
)


def create_recommendation_run(user_id, variant):
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO recommendation_runs (
                user_id,
                experiment_name,
                variant
            )
            VALUES (%s, %s, %s)
            RETURNING id;
        """

        cursor.execute(
            query,
            (
                str(user_id),
                "fund_recommendation_v1",
                variant
            )
        )

        run_id = cursor.fetchone()[0]

        connection.commit()

        return run_id

    finally:
        cursor.close()
        connection.close()


def recommend_funds(request: RecommendationRequest):
    # Check whether recommendations are already cached
    cached = get_cached_recommendation(request.userId)

    if cached:
        return cached

    # Assign the user to an A/B experiment variant
    variant = assign_recommendation_variant(request.userId)

    run_id = create_recommendation_run(
        request.userId,
        variant
    )

    # Load the complete fund catalogue
    funds = get_catalogue()

    recommendations = []

    # Calculate scores for all funds
    for fund in funds:

        score = 0

        # Risk profile match
        if (
            fund.get("risk_level")
            and fund["risk_level"].lower() == request.riskProfile.lower()
        ):
            score += 50

        # Historical one-year return
        score += float(fund.get("return_1y") or 0)

        # Long-term investment bonus
        if request.investmentHorizon >= 5:
            score += 20

        # Higher investment amount bonus
        if request.investmentAmount >= 100000:
            score += 10

        recommendations.append({
            "fund": fund,
            "score": score
        })

    # Sort by score (highest first)
    recommendations.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Only take the top 3 before calling the LLM
    top_recommendations = recommendations[:3]

    # Generate explanations only for the top 3 funds
    for item in top_recommendations:

        item["reason"] = generate_fund_explanation(
            item["fund"],
            request.riskProfile
        )

    # Format the final API response
    result = format_recommendations(
        top_recommendations,
        run_id
    )

    # Cache the result for future requests
    cache_recommendation(
        request.userId,
        result
    )

    return result


def record_recommendation_click(
    user_id,
    recommendation_run_id,
    scheme_code
):
    

    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO recommendation_clicks (
                recommendation_run_id,
                user_id,
                scheme_code
            )
            VALUES (%s, %s, %s)
            RETURNING id;
        """

        cursor.execute(
            query,
            (
                str(recommendation_run_id),
                str(user_id),
                scheme_code
            )
        )

        click_id = cursor.fetchone()[0]

        connection.commit()

        return click_id

    finally:
        cursor.close()
        connection.close()


def has_recommendation_converted(
    user_id,
    recommendation_run_id,
    scheme_code
):
    
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        query = """
            SELECT EXISTS (
                SELECT 1
                FROM public.mf_investments mi
                JOIN recommendation_runs rr
                  ON rr.id = %s
                WHERE mi.user_id = %s
                  AND mi.scheme_code = %s
                  AND mi.transaction_type IN ('PURCHASE', 'SIP')
                  AND mi.status = 'ALLOTTED'
                  AND mi.allotment_date >= rr.created_at::date
            );
        """

        cursor.execute(
            query,
            (
                str(recommendation_run_id),
                str(user_id),
                scheme_code
            )
        )

        result = cursor.fetchone()[0]

        return result

    finally:
        cursor.close()
        connection.close()