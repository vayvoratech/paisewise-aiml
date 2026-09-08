import argparse
import csv
from pathlib import Path

from app.services.language_service import get_languages, get_language_name
from app.services.llm_service import generate_portfolio_response


ROOT = Path(__file__).resolve().parents[1]
TERMS_FILE = ROOT / "data" / "financial_terms.csv"
OUTPUT_FILE = ROOT / "data" / "jargon_prompt_results.csv"

PROMPTS = {
    "simple": 'Explain "{term}" in simple words for a beginner Indian investor. Keep it below 100 words.',
    "analogy": 'Explain "{term}" to a beginner Indian investor using one simple real-life analogy. Keep it below 100 words.',
    "bullets": 'Explain "{term}" to a beginner Indian investor using short bullet points. Keep it below 100 words.',
    "example": 'Explain "{term}" to a beginner Indian investor and include one practical investment example. Keep it below 100 words.',
}


def load_terms(limit):
    with TERMS_FILE.open(encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))
    return rows[:limit]


def run(limit=50, language="Hindi"):
    terms = load_terms(limit)

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["term", "prompt_style", "language", "response"],
        )
        writer.writeheader()

        for row in terms:
            for style, template in PROMPTS.items():
                prompt = template.format(term=row["term"])
                prompt += f"\nRespond only in {language}."

                response = generate_portfolio_response(prompt)

                writer.writerow({
                    "term": row["term"],
                    "prompt_style": style,
                    "language": language,
                    "response": response,
                })

    print(f"Saved prompt test results to {OUTPUT_FILE}")
    print(f"Terms tested: {len(terms)}")
    print(f"Language: {language}")
    print(f"Prompt styles: {len(PROMPTS)}")


def run_all_languages(limit=1):
    terms = load_terms(limit)

    for language in get_languages():
        name = get_language_name(language["code"])
        print(f"Testing {name} ({language['code']})")
        for row in terms:
            prompt = (
                f'Explain "{row["term"]}" in simple words for a beginner Indian investor. '
                f"Keep it below 100 words. Respond only in {name}."
            )
            generate_portfolio_response(prompt)

    print(f"Completed multilingual smoke test for {len(get_languages())} languages.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--language", default="Hindi")
    parser.add_argument("--all-languages", action="store_true")
    args = parser.parse_args()

    if args.all_languages:
        run_all_languages(args.limit)
    else:
        run(args.limit, args.language)
