import time
import asyncio
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../.."
        )
    )
)

from services.batch_insight_generator import generate_batch_insights

def test_portfolio_batch_load():

    user_ids = [
        f"user_{i}"
        for i in range(1, 1001)
    ]

    start_time = time.time()

    results = asyncio.run(
        generate_batch_insights(user_ids)
    )

    end_time = time.time()

    execution_time = end_time - start_time

    # Estimated cost calculation
    # Replace with actual provider token cost after LLM integration
    
    estimated_cost_per_request = 0.01

    total_cost = (
        len(user_ids)
        *
        estimated_cost_per_request
    )

    print(
        f"Generated insights for {len(user_ids)} users"
    )

    print(
        f"Total execution time: {execution_time:.2f} seconds"
    )

    print(
        f"Estimated LLM cost: ₹{total_cost:.2f}"
    )

    assert len(results) == 1000