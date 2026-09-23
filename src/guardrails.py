import re


GUARDRAIL_PATTERNS = [

    # --------------------------------------------------
    # Buy / Sell recommendations
    # --------------------------------------------------

    r"\bbuy\b.*\bstock\b",
    r"\bsell\b.*\bstock\b",
    r"\bbuy\b.*\bshares?\b",
    r"\bsell\b.*\bshares?\b",
    r"\bshares?\b.*\bbuy\b",
    r"\bstock\b.*\bbuy\b",
    r"\bstock\b.*\bsell\b",

    # Direct buy/sell requests
    r"\bshould i buy\b",
    r"\bshould i sell\b",
    r"\bshould i hold\b",
    r"\bshould i keep\b",
    r"\bshould i invest\b",

    # --------------------------------------------------
    # Mutual fund recommendations
    # --------------------------------------------------

    r"\bbest\b.*\bmutual fund\b",
    r"\bmutual fund\b.*\bbest\b",
    r"\bwhich\b.*\bmutual fund\b",
    r"\brecommend\b.*\bmutual fund\b",
    r"\bchoose\b.*\bmutual fund\b",
    r"\bswitch\b.*\bmutual fund\b",

    # Generic fund recommendations
    r"\bbest\b.*\bfund\b",
    r"\bwhich\b.*\bfund\b",
    r"\brecommend\b.*\bfund\b",
    r"\bchoose\b.*\bfund\b",
    r"\bswitch\b.*\bfund\b",
    r"\bfund\b.*\bswitch\b",

    # --------------------------------------------------
    # Stock recommendations
    # --------------------------------------------------

    r"\bbest\b.*\bstock\b",
    r"\bwhich\b.*\bstock\b",
    r"\brecommend\b.*\bstock\b",
    r"\bchoose\b.*\bstock\b",
    r"\btop\b.*\bstock\b",

    # Questions asking for the most likely / highest chance
    r"\bwhich\b.*\bstock\b.*\bchance\b",
    r"\bstock\b.*\bhighest\b.*\bchance\b",
    r"\bhighest\b.*\bchance\b.*\bstock\b",
    r"\bwhich\b.*\bstock\b.*\blikely\b",

    # --------------------------------------------------
    # SIP recommendations
    # --------------------------------------------------

    r"\bbest\b.*\bsip\b",
    r"\bwhich\b.*\bsip\b",
    r"\bchoose\b.*\bsip\b",
    r"\brecommend\b.*\bsip\b",

    # --------------------------------------------------
    # Investment recommendations
    # --------------------------------------------------

    r"\bwhere\b.*\binvest\b",
    r"\bwhat\b.*\binvest\b",
    r"\bwhich\b.*\binvest\b",
    r"\bwhere\b.*\bput\b.*\bmoney\b",
    r"\bwhat\b.*\bshould i invest\b",
    r"\bwhere\b.*\bshould i invest\b",
    r"\bwhich\b.*\bshould i invest\b",

    # --------------------------------------------------
    # Personal recommendations
    # --------------------------------------------------

    r"\bwhat would you\b.*\binvest\b",
    r"\bwhat would you personally\b",
    r"\bif you had\b.*\bchoose\b",
    r"\bfor my age\b",
    r"\bfor me\b.*\binvest\b",
    r"\bchoose\b.*\bfor me\b",
    r"\bwhat should i do\b.*\binvest\b",
    r"\bwhat would you buy\b",
    r"\bwhat would you sell\b",

    # --------------------------------------------------
    # High-return / profit requests
    # --------------------------------------------------

    r"\bhighest\b.*\breturn\b",
    r"\bmaximum\b.*\breturn\b",
    r"\bmaximum\b.*\bprofit\b",
    r"\bhighest\b.*\bprofit\b",
    r"\bhighest\b.*\bgain\b",
    r"\bmaximum\b.*\bgain\b",

    # Highest chance / safest / most likely
    r"\bhighest\b.*\bchance\b",
    r"\bbest chance\b",
    r"\bmost likely\b.*\bprofit\b",
    r"\bmost likely\b.*\breturn\b",
    r"\bmost profitable\b",
    r"\bsafest\b.*\binvestment\b",
    r"\bsafest\b.*\bstock\b",
    r"\bsafest\b.*\bfund\b",

    # Unrealistic return promises
    r"\bdouble\b.*\bmoney\b",
    r"\bdoubl(e|ing)\b.*\bnext\b",
    r"\bguaranteed\b.*\bprofit\b",
    r"\bguaranteed\b.*\breturn\b",
    r"\bmake me rich\b",
    r"\brich quickly\b",

    # --------------------------------------------------
    # Specific recommendation requests
    # --------------------------------------------------

    r"\bspecific\b.*\brecommendation\b",
    r"\bone stock\b.*\bbuy\b",
    r"\bjust give me\b.*\bstock\b",
    r"\btell me exactly\b",
    r"\bexactly where\b.*\binvest\b",
    r"\bgive me one\b.*\bstock\b",
    r"\bgive me one\b.*\bfund\b",

    # --------------------------------------------------
    # Timing recommendations
    # --------------------------------------------------

    r"\bbuy\b.*\btoday\b",
    r"\bbuy\b.*\bright now\b",
    r"\bbuy\b.*\bthis week\b",
    r"\bsell\b.*\btoday\b",
    r"\bsell\b.*\bright now\b",
    r"\bsell\b.*\bthis week\b",
    r"\bsell\b.*\bbefore\b.*\bmarket\b",
    r"\bbefore\b.*\bmarket\b.*\bfall\b",
    r"\bbefore tomorrow\b",

    # --------------------------------------------------
    # Advice bypass / jailbreak attempts
    # --------------------------------------------------

    r"\bignore\b.*\brules\b",
    r"\bforget\b.*\binstructions\b",
    r"\bignore\b.*\binstructions\b",
    r"\bpretend\b.*\bfinancial advisor\b",
    r"\bact as\b.*\binvestor\b",
    r"\bfor educational purposes\b.*\bbuy\b",
    r"\bnot financial advice\b",
    r"\bi accept all the risk\b",
    r"\bsecretly\b.*\binvest\b",
]


def is_guardrail_question(question: str) -> bool:
    """
    Returns True when the user question appears to request
    financial advice or a specific investment recommendation.
    """

    question = question.lower().strip()

    for pattern in GUARDRAIL_PATTERNS:
        if re.search(pattern, question):
            return True

    return False
