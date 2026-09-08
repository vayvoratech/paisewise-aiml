from app.config.settings import GEMINI_API_KEY


def main():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set.")

    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)

    for model in client.models.list():
        print(model.name)


if __name__ == "__main__":
    main()
