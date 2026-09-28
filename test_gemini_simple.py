import asyncio
import os
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()


async def main():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured"
        )

    client = genai.Client(
        api_key=api_key
    )

    print("MODEL: gemini-flash-lite-latest")

    start = time.perf_counter()

    response = await client.aio.models.generate_content(
        model="gemini-flash-lite-latest",
        contents="Say hello in one sentence.",
    )

    elapsed = (
        time.perf_counter() - start
    ) * 1000

    print(
        f"TOTAL: {elapsed:.2f} ms"
    )

    print(
        "RESPONSE:",
        response.text
    )


if __name__ == "__main__":
    asyncio.run(main())