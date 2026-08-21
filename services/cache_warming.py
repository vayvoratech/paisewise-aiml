from cache.redis_cache import RedisCache


cache = RedisCache()


TOP_JARGON_TERMS = [
    "Mutual Fund",
    "Stock Market",
    "SIP",
    "IPO",
    "Inflation",
    "Insurance",
    "Bitcoin",
    "Credit Score",
    "Loan",
    "Interest Rate"
]


def warm_cache():

    for term in TOP_JARGON_TERMS:

        cache_key = f"jargon:english:{term.lower()}"

        existing_data = cache.get(cache_key)

        if existing_data:
            print("Already cached:", term)
            continue


        response = {
            "term": term,
            "language": "english",
            "explanation": f"Simple explanation for {term}"
        }


        cache.set(
            cache_key,
            response,
            expiry=3600
        )

        print("Cache warmed:", term)