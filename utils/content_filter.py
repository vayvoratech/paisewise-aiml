PROHIBITED_PHRASES = [
    "buy this stock",
    "sell this stock",
    "guaranteed returns",
    "you should invest",
    "will definitely increase",
    "will definitely decrease"
]


def check_content(response):

    response_lower = response.lower()

    for phrase in PROHIBITED_PHRASES:
        if phrase in response_lower:
            return {
                "blocked": True,
                "message": "I can only provide educational information and cannot give investment advice."
            }

    return {
        "blocked": False,
        "content": response
    }