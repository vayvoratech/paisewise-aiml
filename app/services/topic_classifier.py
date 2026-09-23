from enum import Enum
import re
import unicodedata


class TopicCategory(str, Enum):
    JARGON = "jargon"
    PRODUCT = "product"
    MARKET = "market"
    PERSONAL_ADVICE = "personal_advice"


# ------------------------------------------------------------------
# NORMALIZATION
# ------------------------------------------------------------------

def normalize_text(question: str) -> str:
    """
    Normalize user input before classification.

    Handles:
    - uppercase/lowercase
    - Unicode characters
    - punctuation
    - repeated whitespace
    - common apostrophes
    """

    if not isinstance(question, str):
        raise TypeError("question must be a string")

    text = unicodedata.normalize("NFKC", question)

    text = text.lower().strip()

    # Normalize apostrophes.
    text = text.replace("’", "'").replace("`", "'")

    # Convert punctuation to spaces.
    text = re.sub(r"[^a-z0-9\s']", " ", text)

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def contains_phrase(text: str, phrase: str) -> bool:
    """
    Match a phrase as a complete word sequence.

    Prevents accidental substring matches such as:
    'sip' matching an unrelated word.
    """

    pattern = rf"\b{re.escape(phrase)}\b"

    return re.search(pattern, text) is not None


def contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(contains_phrase(text, phrase) for phrase in phrases)


# ------------------------------------------------------------------
# PERSONAL ADVICE
# ------------------------------------------------------------------

DIRECT_ADVICE_PATTERNS = (
    # Buy / sell / hold
    "should i buy",
    "should i invest",
    "should i sell",
    "should i hold",
    "where would you put my savings",
    "where would you put my money",
    "what should someone like me invest in",
    "what should someone like me buy",
    "what would someone like me invest in",
        "which investment fits my goals",
    "which fund fits my goals",
    "which stock fits my goals",
    "which etf fits my goals",

    "which investment is suitable for me",
    "which fund is suitable for me",
    "which stock is suitable for me",

    "which investment is right for me",
    "which fund is right for me",
    "which stock is right for me",

    "would this investment suit my financial situation",
    "would this investment suit me",
    "would this fund suit me",
    "would this stock suit me",

    "shall i buy",
    "shall i invest",
    "shall i sell",
    "shall i hold",

    "can i buy",
    "can i invest",

    "is it a good time to buy",
    "is it a good time to invest",

    # Selection
    "which stock should i buy",
    "which stocks should i buy",
    "which share should i buy",
    "which shares should i buy",
    "what would you invest in if you were me",
    "what would you buy if you were me",
    "what would you choose if you were me",
    "what would you recommend for me",

    "which stock should i choose",
    "which stocks should i choose",

    "which mutual fund should i buy",
    "which mutual fund should i choose",

    "which etf should i buy",
    "which bond should i buy",

    # Recommendations
    "recommend a stock",
    "recommend stocks",
    "recommend a share",
    "recommend shares",
    "recommend a mutual fund",
    "recommend mutual funds",
    "recommend an etf",
    "recommend an investment",

    "suggest a stock",
    "suggest stocks",
    "suggest a mutual fund",
    "suggest mutual funds",
    "suggest an etf",
    "suggest an investment",

    "advise me on a stock",
    "advise me on stocks",
    "advise me on a mutual fund",
    "advise me on an investment",

    # Personalized selection
    "which investment is best for me",
    "which stock is best for me",
    "which mutual fund is best for me",
    "which etf is best for me",

    "what should i invest in",
    "what should i buy",
    "what should i sell",
    "what should i choose",

    "where should i invest",
    "where should i put my money",
    "where should i put my savings",

    "what should i do with my money",
    "what should i do with my portfolio",
    "what should i do with my investments",

    # Personalized suitability
    "is this investment right for me",
    "is this stock right for me",
    "is this fund right for me",
    "is this etf right for me",

    "is this suitable for me",
    "is this suitable for my goals",
    "is this suitable for my situation",

    "would this investment suit me",
    "would this stock suit me",
    "would this fund suit me",

    # Portfolio decisions
    "should i change my portfolio",
    "should i change my investments",
    "should i change my holdings",

    "should i add this stock",
    "should i add this fund",
    "should i add this etf",

    "should i remove this stock",
    "should i sell this stock",
    "should i sell this fund",

    "should i switch funds",
    "should i switch mutual funds",

    # Personal goals
    "what should i invest for retirement",
    "what should i invest for my retirement",
    "where should i invest for retirement",

    "what should i invest for my child",
    "where should i invest for my child",

    "what should i invest for my education",
    "where should i invest for my education",

    # Explicit assistance
    "help me choose an investment",
    "help me choose a stock",
    "help me choose a fund",
    "help me choose an etf",

    "help me decide where to invest",
    "help me decide what to invest in",

    "choose an investment for me",
    "choose a stock for me",
    "choose a mutual fund for me",

    "pick an investment for me",
    "pick a stock for me",
    "pick a fund for me",

    # Personal situation
    "for my situation",
    "for my financial situation",
    "for my goals",
    "for my portfolio",
    "for my risk profile",
    "for my retirement",
)


ADVICE_VERBS = (
    "recommend",
    "recommendation",
    "suggest",
    "suggestion",
    "advise",
    "advice",
    "choose",
    "pick",
    "select",
)


INVESTMENT_OBJECTS = (
    "stock",
    "stocks",
    "share",
    "shares",
    "mutual fund",
    "mutual funds",
    "etf",
    "etfs",
    "bond",
    "bonds",
    "investment",
    "investments",
    "portfolio",
    "fund",
    "funds",
    "sip",
    "sips",
)


PERSONAL_PRONOUNS = (
    "i",
    "me",
    "my",
    "mine",
    "myself",
)


def is_personal_advice(text: str) -> bool:
    """
    High-precision personal investment advice detector.
    Personal-advice detection has highest priority.
    """

    # 1. Explicit high-confidence patterns.
    if contains_any(text, DIRECT_ADVICE_PATTERNS):
        return True

    # 2. Advice verb + investment object.
    has_advice_verb = contains_any(text, ADVICE_VERBS)
    has_investment_object = contains_any(text, INVESTMENT_OBJECTS)

    if has_advice_verb and has_investment_object:
        return True

    # 3. Personal language.
    has_personal_language = contains_any(
        text,
        PERSONAL_PRONOUNS,
    )

    # 4. Investment decision language.
    decision_words = (
        "buy",
        "sell",
        "hold",
        "invest",
        "choose",
        "select",
        "pick",
        "switch",
        "add",
        "remove",
        "put",
        "allocate",
    )

    has_decision_language = contains_any(
        text,
        decision_words,
    )

    # 5. Personal + investment + decision.
    if (
        has_personal_language
        and has_investment_object
        and has_decision_language
    ):
        return True

    # 6. Personal goals/situation + investment decision.
    personal_context = (
        "my savings",
        "my money",
        "my goals",
        "my situation",
        "my financial situation",
        "my portfolio",
        "my risk profile",
        "my retirement",
        "my future",
        "someone like me",
        "someone in my situation",
        "someone in my position",
    )

    if (
        contains_any(text, personal_context)
        and (
            has_decision_language
            or contains_any(
                text,
                (
                    "recommend",
                    "suggest",
                    "suitable",
                    "appropriate",
                    "right for",
                    "best for",
                ),
            )
        )
    ):
        return True

    # 7. "What would you..." personalized hypothetical.
    hypothetical_advice = (
        "what would you invest",
        "what would you buy",
        "what would you choose",
        "what would you recommend",
    )

    if contains_any(text, hypothetical_advice):
        return True
        # 8. Personalized suitability / goal matching.
    #
    # Examples:
    # "Which fund fits my goals?"
    # "Which investment fits my goals?"
    # "Would this investment suit my financial situation?"

    suitability_context = (
        "my goals",
        "my financial goals",
        "my situation",
        "my financial situation",
        "my needs",
        "my risk profile",
        "my portfolio",
        "my circumstances",
        "my requirements",
    )

    suitability_language = (
        "suit",
        "suits",
        "suitable",
        "fit",
        "fits",
        "appropriate",
        "right for",
        "best for",
        "match",
        "matches",
    )

    if (
        contains_any(text, suitability_context)
        and contains_any(text, suitability_language)
        and has_investment_object
    ):
        return True

    return False


# ------------------------------------------------------------------
# MARKET
# ------------------------------------------------------------------

MARKET_PATTERNS = (
    "stock market",
    "share market",
    "equity market",
    "financial market",
    "broader market",
    "overall market",
    "markets volatile",
    "market volatile",
    "markets rising",
    "markets falling",
    "markets moving",
    "markets trending",
    "markets volatile",
    "market volatile",
    "markets rising",
    "markets falling",
    "markets moving",
    "markets trending",
    "markets performing",
    "markets doing",
    "across the markets",
    "happening across the markets",

    "market trend",
    "market trends",
    "market performance",
    "market outlook",
    "market movement",
    "market movements",
    "market condition",
    "market conditions",
    "market sentiment",
    "market direction",
    "market rally",
    "market crash",
    "market correction",
    "market recovery",
    "market sell off",
    "market selloff",

    "market today",
    "market this week",
    "market this month",

    "nifty",
    "nifty 50",
    "sensex",
    "bank nifty",

    "market index",
    "market indices",
    "market indexes",
    "stock index",
    "stock indices",
    "stock indexes",

    "index performance",
    "index trend",

    "why is the market falling",
    "why is the market rising",
    "why did the market fall",
    "why did the market rise",

    "how is the market performing",
    "how is the market doing",
    "how is the stock market performing",
    "how is the stock market doing",

    "what is happening in the market",
    "what is happening with the market",

    "why are markets falling",
    "why are markets rising",

    "market is falling",
    "market is rising",
)


MARKET_TERMS = (
    "nifty",
    "sensex",
    "bank nifty",
    "market",
    "markets",
    "index",
    "indices",
    "indexes",
    "equity market",
    "equity markets",
    "stock market",
    "stock markets",
)

MARKET_ACTIONS = (
    "performing",
    "performance",
    "trend",
    "trending",
    "rising",
    "falling",
    "moving",
    "movement",
    "outlook",
    "direction",
    "rally",
    "crash",
    "correction",
    "recovery",
    "volatile",
    "volatility",
    "sentiment",
     "doing",
    "happening",
    "reacting",
    "react",
    "changing",
    "behaviour",
    "behavior",
)


def is_market_question(text: str) -> bool:
    """
    Detect questions about market-wide behaviour.

    Important:
    'stock' alone does NOT mean market.
    """

    if contains_any(text, MARKET_PATTERNS):
        return True

    has_market_term = contains_any(text, MARKET_TERMS)
    has_market_action = contains_any(text, MARKET_ACTIONS)

    return has_market_term and has_market_action


# ------------------------------------------------------------------
# PRODUCT
# ------------------------------------------------------------------

PRODUCT_PATTERNS = (
    "mutual fund",
    "mutual funds",

    "exchange traded fund",
    "exchange traded funds",
    "etf",
    "etfs",

    "stock",
    "stocks",
    "share",
    "shares",

    "bond",
    "bonds",

    "ipo",
    "ipos",

    "sip",
    "sips",

    "index fund",
    "index funds",

    "equity fund",
    "equity funds",

    "debt fund",
    "debt funds",

    "hybrid fund",
    "hybrid funds",

    "bond fund",
    "bond funds",

    "gold etf",
    "bond etf",

    "reit",
    "invIT",
    "investment product",
    "investment products",

    "demat account",
    "brokerage account",
)


PRODUCT_EDUCATIONAL_PATTERNS = (
    "what is",
    "what are",
    "what does",
    "what do",
    "explain",
    "tell me about",
    "how does",
    "how do",
    "meaning of",
    "define",
    "definition",
    "difference between",
    "compare",
)


def is_product_question(text: str) -> bool:
    """
    Detect investment-product questions.

    Market classification is executed before this function,
    so 'stock market' is not incorrectly classified as PRODUCT.
    """

    return (
        contains_any(text, PRODUCT_PATTERNS)
        and (
            contains_any(text, PRODUCT_EDUCATIONAL_PATTERNS)
            or "tell me about" in text
        )
    )


# ------------------------------------------------------------------
# JARGON
# ------------------------------------------------------------------

JARGON_TERMS = (
    "diversification",
    "volatility",
    "liquidity",
    "nav",
    "expense ratio",
    "market capitalization",
    "market cap",
    "p/e ratio",
    "pe ratio",
    "compounding",
    "compound interest",
    "inflation",
    "risk",
    "return",
    "risk tolerance",
    "asset allocation",
    "portfolio allocation",
    "rebalancing",
    "capital gain",
    "capital gains",
    "dividend yield",
    "benchmark",
    "tracking error",
    "credit risk",
    "interest rate risk",
    "systematic risk",
    "unsystematic risk",
    "cagr",
    "drawdown",
    "valuation",
    "yield",
    "bond maturity",
    "portfolio turnover",
    "concentration risk",
    "investment horizon",
    "risk adjusted return",
)


def is_jargon_question(text: str) -> bool:
    """
    Detect educational/terminology questions.
    """

    if contains_any(text, JARGON_TERMS):
        return True

    return contains_any(
        text,
        (
            "what does this term mean",
            "what does this mean",
            "explain this concept",
            "explain this term",
            "what is the meaning",
            "define this",
            "help me understand",
        ),
    )


# ------------------------------------------------------------------
# PUBLIC CLASSIFIER
# ------------------------------------------------------------------

def classify_question(question: str) -> TopicCategory:
    """
    Production-oriented deterministic topic classifier.

    Priority:
        1. Personal advice
        2. Market
        3. Product
        4. Jargon
        5. Jargon fallback

    The fallback is intentional because Task 2 exposes four
    required categories.
    """

    text = normalize_text(question)

    if not text:
        raise ValueError("question cannot be empty")

    # Safety first.
    if is_personal_advice(text):
        return TopicCategory.PERSONAL_ADVICE

    # Market before product because 'stock market' contains 'stock'.
    if is_market_question(text):
        return TopicCategory.MARKET

    if is_product_question(text):
        return TopicCategory.PRODUCT

    if is_jargon_question(text):
        return TopicCategory.JARGON

    # Required four-category interface.
    return TopicCategory.JARGON