import os

from google import genai


def test_gemini_connection():
    """
    Manually verify that the Gemini API is reachable.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured"
        )

    client = genai.Client(
        api_key=api_key
    )

    response = client.models.generate_content(
        model=os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        ),
        contents="What is an ETF?",
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response"
        )

    print(response.text)


if __name__ == "__main__":
    test_gemini_connection()