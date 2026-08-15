import asyncio

from services.portfolio_service import get_portfolio_insight
from services.portfolio_fallback import get_portfolio_fallback


async def generate_single_insight(user_id: str):

    try:

        insight = await asyncio.wait_for(
            asyncio.to_thread(
                get_portfolio_insight,
                user_id,
                "english"
            ),
            timeout=15
        )

        return {
            "user_id": user_id,
            "status": "generated",
            "insight": insight
        }


    except asyncio.TimeoutError:

        return {
            "user_id": user_id,
            "status": "fallback",
            "insight": get_portfolio_fallback()
        }


async def generate_batch_insights(user_ids: list[str]):

    tasks = [
        generate_single_insight(user_id)
        for user_id in user_ids
    ]

    results = await asyncio.gather(*tasks)

    return results