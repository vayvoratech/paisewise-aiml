from transformers import pipeline
import json
import os

print("=" * 60)
print("PaiseWise News Sector Classifier")
print("=" * 60)

print("\nLoading zero-shot classification model...")
print("This may take some time on the first run...")

classifier = pipeline(
    "zero-shot-classification",
    model="valhalla/distilbart-mnli-12-3"
)

print("Model loaded successfully!")

SECTORS = [
    "IT",
    "Banking",
    "Pharma",
    "Auto",
    "Energy",
    "FMCG",
    "Metals",
    "Telecom",
    "Financial Services",
    "Market Index",
    "Other"
]


def classify_article(title, description=""):

    text = title

    if description:
        text = title + ". " + description

    result = classifier(
        text,
        candidate_labels=SECTORS
    )

    return {
        "sector": result["labels"][0],
        "confidence": round(
            float(result["scores"][0]),
            4
        )
    }


if __name__ == "__main__":

    test_articles = [
        {
            "title": "TCS reports strong quarterly growth",
            "description": "The IT company reported improved revenue."
        },
        {
            "title": "HDFC Bank reports quarterly results",
            "description": "The bank announced its latest financial results."
        },
        {
            "title": "Sun Pharma receives regulatory approval",
            "description": "The pharmaceutical company received approval for a new product."
        },
        {
            "title": "Reliance shares rise after energy project announcement",
            "description": "The company announced a major energy investment."
        }
    ]

    print("\nClassifying test articles...")

    for number, article in enumerate(test_articles, start=1):

        result = classify_article(
            article["title"],
            article["description"]
        )

        print("\nArticle", number)
        print("Title:", article["title"])
        print("Sector:", result["sector"])
        print("Confidence:", result["confidence"])

    print("\n" + "=" * 60)
    print("News classification completed successfully.")
    print("=" * 60)