# PaiseWise News Sector Classifier

from transformers import pipeline


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


def classify_article(
    title,
    description=""
):

    text = title

    if description:

        text = (
            title +
            ". " +
            description
        )

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