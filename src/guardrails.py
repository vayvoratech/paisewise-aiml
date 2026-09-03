import re


GUARDRAIL_PATTERNS = [

    # Buy / sell recommendations
    r"\bbuy\b.*\bstock\b",
    r"\bsell\b.*\bstock\b",
    r"\bbuy\b.*\bshares?\b",
    r"\bsell\b.*\bshares?\b",
    r"\bshares?\b.*\bbuy\b",
    r"\bstock\b.*\bbuy\b",

    # Mutual fund recommendations
    r"\bbest\b.*\bmutual fund\b",
    r"\bmutual fund\b.*\bbest\b",
    r"\bwhich\b.*\bmutual fund\b",
    r"\brecommend\b.*\bmutual fund\b",
    r"\bchoose\b.*\bmutual fund\b",
    r"\bswitch\b.*\bmutual fund\b",

    # SIP recommendations
    r"\bbest\b.*\bsip\b",
    r"\bwhich\b.*\bsip\b",
    r"\bchoose\b.*\bsip\b",
    r"\brecommend\b.*\bsip\b",

    # Investment recommendations
    r"\bwhere\b.*\binvest\b",
    r"\bwhat\b.*\binvest\b",
    r"\bwhich\b.*\binvest\b",
    r"\bwhere\b.*\bput\b.*\bmoney\b",
    r"\bwhat\b.*\bshould i invest\b",

    # Personal recommendations
    r"\bwhat would you\b.*\binvest\b",
    r"\bwhat would you personally\b",
    r"\bif you had\b.*\bchoose\b",
    r"\bfor my age\b",
    r"\bfor me\b.*\binvest\b",
    r"\bchoose\b.*\bfor me\b",

    # High-return / profit promises
    r"\bhighest\b.*\breturn\b",
    r"\bmaximum\b.*\breturn\b",
    r"\bmaximum\b.*\bprofit\b",
    r"\bdouble\b.*\bmoney\b",
    r"\bdoubl(e|ing)\b.*\bnext\b",
    r"\bguaranteed\b.*\bprofit\b",
    r"\bguaranteed\b.*\breturn\b",
    r"\bmake me rich\b",
    r"\brich quickly\b",

    # Specific recommendation requests
    r"\bspecific\b.*\brecommendation\b",
    r"\bone stock\b.*\bbuy\b",
    r"\bjust give me\b.*\bstock\b",
    r"\btell me exactly\b",
    r"\bexactly where\b.*\binvest\b",

    # Timing recommendations
    r"\bbuy\b.*\btoday\b",
    r"\bbuy\b.*\bright now\b",
    r"\bbuy\b.*\bthis week\b",
    r"\bsell\b.*\btoday\b",
    r"\bsell\b.*\bbefore\b.*\bmarket\b",
    r"\bbefore\b.*\bmarket\b.*\bfall\b",
    r"\bbefore tomorrow\b",

    # Advice bypass / jailbreak attempts
    r"\bignore\b.*\brules\b",
    r"\bforget\b.*\binstructions\b",
    r"\bpretend\b.*\bfinancial advisor\b",
    r"\bact as\b.*\binvestor\b",
    r"\bfor educational purposes\b.*\bbuy\b",
    r"\bnot financial advice\b",
    r"\bi accept all the risk\b",
    r"\bsecretly\b.*\binvest",

]


def is_guardrail_question(question: str) -> bool:

    question = question.lower().strip()

    for pattern in GUARDRAIL_PATTERNS:

        if re.search(pattern, question):
            return True

    return False