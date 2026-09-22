# ============================================================
# PAISEWISE TRANSLATION SERVICE
# ============================================================

import sys
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# GEMINI SERVICE
# ============================================================

from llm_cost_management.gemini_service import GeminiService


# ============================================================
# SUPPORTED LANGUAGES
# ============================================================

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
}


# ============================================================
# TRANSLATION SERVICE
# ============================================================

class TranslationService:

    def __init__(self):

        self.gemini = GeminiService()

    # ========================================================
    # SINGLE TEXT TRANSLATION
    # ========================================================

    def translate(
        self,
        text: str,
        target_language: str
    ) -> dict:

        """
        Translate English educational content
        into the requested supported language.
        """

        target_language = (
            target_language
            .lower()
            .strip()
        )

        # ----------------------------------------------------
        # English
        # ----------------------------------------------------

        if target_language == "en":

            return {

                "text":
                    text,

                "language":
                    "en",

                "language_name":
                    "English",

                "translated":
                    False,

                "model":
                    None
            }

        # ----------------------------------------------------
        # Validate language
        # ----------------------------------------------------

        if target_language not in LANGUAGE_NAMES:

            raise ValueError(
                "Unsupported translation language: "
                f"{target_language}"
            )

        language_name = LANGUAGE_NAMES[
            target_language
        ]

        # ----------------------------------------------------
        # Translation prompt
        # ----------------------------------------------------

        prompt = f"""
You are the translation assistant for PaiseWise,
a financial education application.

Translate the following educational content from English
to {language_name}.

Rules:

1. Preserve the original meaning accurately.
2. Use simple and natural language.
3. Do not add new financial advice.
4. Do not remove important information.
5. Keep financial terms understandable.
6. Do not translate company names, stock symbols,
   numbers, percentages, or technical abbreviations
   unnecessarily.
7. Return ONLY the translated text.
8. Do not add explanations about the translation.

English content:

{text}
"""

        # ----------------------------------------------------
        # Gemini request
        # ----------------------------------------------------

        result = self.gemini.generate_response(
            prompt
        )

        translated_text = (
            result["text"]
            .strip()
        )

        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return {

            "text":
                translated_text,

            "language":
                target_language,

            "language_name":
                language_name,

            "translated":
                True,

            "model":
                result["model"]
        }

    # ========================================================
    # BATCH NEWS TRANSLATION
    # ========================================================

    def translate_news_articles(
        self,
        articles: list,
        target_language: str
    ) -> dict:

        """
        Translate all news article titles and descriptions
        using a single Gemini request.

        This avoids making separate Gemini requests for
        every article title and description.
        """

        target_language = (
            target_language
            .lower()
            .strip()
        )

        # ----------------------------------------------------
        # English
        # ----------------------------------------------------

        if target_language == "en":

            return {

                "articles":
                    articles,

                "language":
                    "en",

                "language_name":
                    "English",

                "translated":
                    False,

                "model":
                    None
            }

        # ----------------------------------------------------
        # Validate language
        # ----------------------------------------------------

        if target_language not in LANGUAGE_NAMES:

            raise ValueError(
                "Unsupported translation language: "
                f"{target_language}"
            )

        language_name = LANGUAGE_NAMES[
            target_language
        ]

        # ----------------------------------------------------
        # Empty articles
        # ----------------------------------------------------

        if not articles:

            return {

                "articles":
                    [],

                "language":
                    target_language,

                "language_name":
                    language_name,

                "translated":
                    False,

                "model":
                    None
            }

        # ====================================================
        # Prepare articles
        # ====================================================

        news_text_parts = []

        for index, article in enumerate(
            articles
        ):

            title = article.get(
                "title",
                ""
            )

            description = article.get(
                "description",
                ""
            )

            news_text_parts.append(

                f"ARTICLE {index + 1}\n"
                f"TITLE: {title}\n"
                f"DESCRIPTION: {description}\n"
            )

        news_text = "\n".join(
            news_text_parts
        )

        # ====================================================
        # Batch translation prompt
        # ====================================================

        prompt = f"""
You are the translation assistant for PaiseWise,
a financial education application.

Translate ALL the following market news articles
from English to {language_name}.

IMPORTANT:

- Translate every TITLE.
- Translate every DESCRIPTION.
- Keep the same article order.
- Do not skip any article.
- Do not combine articles.
- Do not add new information.
- Do not provide financial advice.
- Preserve the original meaning.
- Use simple and natural {language_name}.
- Keep company names unchanged when appropriate.
- Keep stock symbols such as TCS, NSE, NIFTY,
  Sensex, FMCG, IT, etc. unchanged when appropriate.
- Keep numbers, percentages, dates, currencies,
  and financial values accurate.
- Do not translate URLs.
- Do not translate source names unnecessarily.

Return ONLY the translated articles.

Use EXACTLY this format:

ARTICLE 1
TITLE: <translated title>
DESCRIPTION: <translated description>

ARTICLE 2
TITLE: <translated title>
DESCRIPTION: <translated description>

Continue this format for every article.

Do not add explanations.

NEWS ARTICLES:

{news_text}
"""

        # ====================================================
        # ONE Gemini request
        # ====================================================

        result = self.gemini.generate_response(
            prompt
        )

        translated_text = (
            result["text"]
            .strip()
        )

        # ====================================================
        # Parse Gemini response
        # ====================================================

        translated_articles = []

        # ----------------------------------------------------
        # Split using ARTICLE markers
        # ----------------------------------------------------

        blocks = translated_text.split(
            "ARTICLE "
        )

        for index, original_article in enumerate(
            articles
        ):

            translated_article = (
                original_article.copy()
            )

            article_number = index + 1

            matching_block = None

            # ------------------------------------------------
            # Find corresponding article block
            # ------------------------------------------------

            for block in blocks:

                block = block.strip()

                if (

                    block.startswith(
                        f"{article_number}\n"
                    )

                    or

                    block.startswith(
                        f"{article_number} "
                    )

                ):

                    matching_block = block

                    break

            # ------------------------------------------------
            # Parse title and description
            # ------------------------------------------------

            if matching_block:

                lines = (
                    matching_block
                    .splitlines()
                )

                translated_title = None

                translated_description = None

                for line in lines:

                    line = line.strip()

                    # ----------------------------------------
                    # TITLE
                    # ----------------------------------------

                    if line.startswith(
                        "TITLE:"
                    ):

                        translated_title = (
                            line[
                                len("TITLE:")
                            ].strip()
                        )

                    # ----------------------------------------
                    # DESCRIPTION
                    # ----------------------------------------

                    elif line.startswith(
                        "DESCRIPTION:"
                    ):

                        translated_description = (
                            line[
                                len(
                                    "DESCRIPTION:"
                                ):].strip()
                        )

                # --------------------------------------------
                # Update title
                # --------------------------------------------

                if translated_title:

                    translated_article[
                        "title"
                    ] = translated_title

                # --------------------------------------------
                # Update description
                # --------------------------------------------

                if translated_description:

                    translated_article[
                        "description"
                    ] = translated_description

            # ------------------------------------------------
            # Add article
            # ------------------------------------------------

            translated_articles.append(
                translated_article
            )

        # ====================================================
        # Return batch result
        # ====================================================

        return {

            "articles":
                translated_articles,

            "language":
                target_language,

            "language_name":
                language_name,

            "translated":
                True,

            "model":
                result["model"]
        }


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    service = TranslationService()

    # --------------------------------------------------------
    # Test single translation
    # --------------------------------------------------------

    print("\n====================================")
    print("SINGLE TEXT TRANSLATION TEST")
    print("====================================")

    result = service.translate(

        "Diversification means spreading "
        "investments across different assets "
        "or categories to reduce concentration risk.",

        "te"
    )

    print(
        "Language:",
        result["language_name"]
    )

    print(
        "Translated:",
        result["text"]
    )

    print(
        "Model:",
        result["model"]
    )

    print("====================================")

    # --------------------------------------------------------
    # Test batch news translation
    # --------------------------------------------------------

    print("\n====================================")
    print("BATCH NEWS TRANSLATION TEST")
    print("====================================")

    sample_articles = [

        {
            "title":
                "Sensex gains 383 points",

            "description":
                "Indian equity markets "
                "advanced during morning trading.",

            "source":
                "Business Standard",

            "published_at":
                "2026-09-16T07:20:02Z",

            "url":
                "https://example.com/article1"
        },

        {
            "title":
                "Nifty FMCG rises 2 percent",

            "description":
                "FMCG stocks gained during "
                "the trading session.",

            "source":
                "BusinessLine",

            "published_at":
                "2026-09-16T06:35:18Z",

            "url":
                "https://example.com/article2"
        }
    ]

    batch_result = (
        service.translate_news_articles(
            sample_articles,
            "te"
        )
    )

    print(
        "Language:",
        batch_result[
            "language_name"
        ]
    )

    print(
        "Translated:",
        batch_result[
            "translated"
        ]
    )

    print(
        "Model:",
        batch_result[
            "model"
        ]
    )

    print("\nTranslated Articles:")

    for article in batch_result[
        "articles"
    ]:

        print(
            "\nTitle:",
            article.get(
                "title"
            )
        )

        print(
            "Description:",
            article.get(
                "description"
            )
        )

    print("\n====================================")