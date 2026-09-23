from dataclasses import dataclass

from app.services.topic_classifier import (
    TopicCategory,
    classify_question,
)


@dataclass(frozen=True)
class GuardrailResult:
    """
    Result returned by the guardrail layer.
    """

    blocked: bool
    category: TopicCategory
    message: str | None = None


PERSONAL_ADVICE_RESPONSE = (
    "I can provide general educational information about investments, "
    "but I can't recommend a specific investment or make a personalized "
    "investment decision for you. You may want to consult a qualified "
    "financial professional for advice based on your individual situation."
)


def check_guardrail(question: str) -> GuardrailResult:
    """
    Apply safety guardrails before the question reaches the LLM.

    Personal-advice questions are blocked.
    Other supported topics continue through the normal pipeline.
    """

    category = classify_question(question)

    if category == TopicCategory.PERSONAL_ADVICE:
        return GuardrailResult(
            blocked=True,
            category=category,
            message=PERSONAL_ADVICE_RESPONSE,
        )

    return GuardrailResult(
        blocked=False,
        category=category,
        message=None,
    )