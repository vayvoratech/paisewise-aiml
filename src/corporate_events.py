# PaiseWise Corporate Events


def extract_corporate_events(articles):

    corporate_events = []

    event_keywords = {
        "quarterly results": "Quarterly Results",
        "earnings": "Earnings",
        "acquisition": "Acquisition",
        "merger": "Merger",
        "regulatory approval": "Regulatory Approval",
        "partnership": "Partnership",
        "investment": "Investment",
        "dividend": "Dividend",
        "funding": "Funding",
        "expansion": "Expansion"
    }

    for article in articles:

        # Make sure article is a dictionary
        if not isinstance(article, dict):
            continue

        title = article.get("title") or ""
        description = article.get("description") or ""

        text = (title + " " + description).lower()

        for keyword, event_type in event_keywords.items():

            if keyword in text:

                corporate_events.append({
                    "title": title,
                    "event_type": event_type,
                    "source": article.get("source"),
                    "published_at": article.get("published_at"),
                    "url": article.get("url")
                })

                break

    return corporate_events