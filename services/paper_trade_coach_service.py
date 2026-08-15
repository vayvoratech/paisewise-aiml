import json
import logging

from database.database import get_db_connection
from cache.redis_cache import RedisCache
from services.llm_client import LLMClient

from prompts.prompt_templates import (
    PAPER_TRADE_COACH_PROMPT,
    FINANCIAL_GUARDRAILS,
)


logger = logging.getLogger("ai-service")

cache = RedisCache()
llm_client = LLMClient()


def find_related_lesson(cursor, topic):
    """
    Find a lesson related to the coach feedback topic.

    First tries to match the topic directly against lesson content.
    If no direct match exists, falls back to a lesson related to
    common paper-trading concepts such as market movement, price
    movement, and trend.
    """

    # 1. Try direct topic matching
    lesson_query = """
    SELECT
        id,
        title
    FROM learn.lessons
    WHERE
        LOWER(title) LIKE LOWER(%s)
        OR LOWER(chapter) LIKE LOWER(%s)
        OR LOWER(segments_json) LIKE LOWER(%s)
        OR LOWER(jargon_words_json) LIKE LOWER(%s)
    ORDER BY chapter_no, index
    LIMIT 1
    """

    topic_pattern = f"%{topic}%"

    cursor.execute(
        lesson_query,
        (
            topic_pattern,
            topic_pattern,
            topic_pattern,
            topic_pattern,
        )
    )

    result = cursor.fetchone()

    if result:
        return {
            "id": result[0],
            "title": result[1],
        }

    # 2. Fallback for paper-trading concepts
    fallback_query = """
    SELECT
        id,
        title
    FROM learn.lessons
    WHERE
        LOWER(title) LIKE '%price movement%'
        OR LOWER(chapter) LIKE '%market movement%'
        OR LOWER(segments_json) LIKE '%market movement%'
        OR LOWER(jargon_words_json) LIKE '%price movement%'
        OR LOWER(jargon_words_json) LIKE '%trend%'
    ORDER BY chapter_no, index
    LIMIT 1
    """

    cursor.execute(fallback_query)

    result = cursor.fetchone()

    if result:
        return {
            "id": result[0],
            "title": result[1],
        }

    # 3. No related lesson available
    return {
        "id": "",
        "title": "No related lesson found",
    }


def get_paper_trade_coach(order_id):
    """
    Generate an educational coaching response for a completed paper trade.

    The response is cached by order_id so the same trade does not
    trigger repeated LLM generation.
    """

    cache_key = f"paper_trade_coach:{order_id}"

    # ---------------------------------------------------------
    # 1. Check Redis cache
    # ---------------------------------------------------------

    cached_result = cache.get(cache_key)

    if cached_result:
        print(
            f"CACHE HIT: {cache_key}"
        )
        return cached_result

    print(
        f"CACHE MISS: {cache_key}"
    )

    connection = None
    cursor = None

    try:

        # -----------------------------------------------------
        # 2. Load trade details + market context
        # -----------------------------------------------------

        connection = get_db_connection()
        cursor = connection.cursor()

        order_query = """
        SELECT
            o.id,
            o.user_id,
            o.symbol,
            o.side,
            o.shares,
            o.price_per_share,
            o.total_amount,
            o.order_type,
            o.created_at,
            s.name,
            s.price,
            s.change_pct,
            s.trend_json
        FROM practice.orders o
        JOIN practice.stocks s
            ON o.symbol = s.symbol
        WHERE o.id = %s
        LIMIT 1
        """

        cursor.execute(
            order_query,
            (str(order_id),)
        )

        order_result = cursor.fetchone()

        if order_result is None:
            raise ValueError(
                f"Paper trade order not found: {order_id}"
            )

        (
            order_id_db,
            user_id,
            symbol,
            side,
            shares,
            price_per_share,
            total_amount,
            order_type,
            created_at,
            stock_name,
            current_price,
            change_pct,
            trend_json,
        ) = order_result

        # -----------------------------------------------------
        # 3. Load user learning context
        # -----------------------------------------------------

        feature_query = """
        SELECT
            quiz_attempts_total,
            quiz_pass_rate,
            avg_quiz_score
        FROM public.user_features
        WHERE user_id = %s
        LIMIT 1
        """

        cursor.execute(
            feature_query,
            (user_id,)
        )

        feature_result = cursor.fetchone()

        if feature_result:

            (
                quiz_attempts_total,
                quiz_pass_rate,
                avg_quiz_score,
            ) = feature_result

        else:

            quiz_attempts_total = 0
            quiz_pass_rate = 0
            avg_quiz_score = 0

        # -----------------------------------------------------
        # 4. Prepare trade context
        # -----------------------------------------------------

        trade_context = f"""
Order ID: {order_id_db}
Symbol: {symbol}
Trade Side: {side}
Shares: {shares}
Price Per Share: ₹{price_per_share}
Total Amount: ₹{total_amount}
Order Type: {order_type}
Trade Time: {created_at}
"""

        # -----------------------------------------------------
        # 5. Prepare market context
        # -----------------------------------------------------

        market_context = f"""
Stock: {stock_name}
Symbol: {symbol}
Current Price: ₹{current_price}
Daily Change: {change_pct}%
Recent Price Trend: {trend_json}
"""

        # -----------------------------------------------------
        # 6. Prepare user learning context
        # -----------------------------------------------------

        user_learning_context = f"""
Quiz Attempts: {quiz_attempts_total}
Quiz Pass Rate: {float(quiz_pass_rate)}
Average Quiz Score: {float(avg_quiz_score)}
"""

        # -----------------------------------------------------
        # 7. Build educational prompt
        # -----------------------------------------------------

        prompt = PAPER_TRADE_COACH_PROMPT.format(
            guardrails=FINANCIAL_GUARDRAILS,
            trade_context=trade_context,
            market_context=market_context,
            user_learning_context=user_learning_context,
        )

        # -----------------------------------------------------
        # 8. Generate coach response
        # -----------------------------------------------------

        llm_response = llm_client.generate_response(prompt)

        # -----------------------------------------------------
        # 9. Parse LLM JSON
        # -----------------------------------------------------

        try:

            coach_data = json.loads(llm_response)

        except json.JSONDecodeError as error:

            logger.exception(
                f"Invalid JSON returned by LLM: {error}"
            )

            raise ValueError(
                "LLM returned an invalid coach response."
            )

        learning_point = coach_data.get(
            "learning_point"
        )

        topic = coach_data.get(
            "topic"
        )

        print("COACH TOPIC:", topic)

        if not learning_point or not topic:

            raise ValueError(
                "LLM coach response is missing "
                "learning_point or topic."
            )

        # -----------------------------------------------------
        # 10. Find related lesson
        # -----------------------------------------------------

        lesson = find_related_lesson(
            cursor,
            topic
        )

        # -----------------------------------------------------
        # 11. Build final response
        # -----------------------------------------------------

        response = {
            "order_id": str(order_id_db),
            "learning_point": learning_point,
            "lesson": lesson,
        }

        # -----------------------------------------------------
        # 12. Cache response by order ID
        # -----------------------------------------------------

        cache.set(
            cache_key,
            response,
            expiry=86400
        )

        logger.info(
            f"Paper trade coach response cached: {cache_key}"
        )

        return response

    except Exception as error:

        logger.exception(
            f"Paper trade coach generation failed: {error}"
        )

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()