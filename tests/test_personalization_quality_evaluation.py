from app.schemas.chat import UserContext
from app.services.rag.prompt_builder import PromptBuilder
from app.services.rag.vector_store import SearchResult


def test_prompt_includes_available_user_context():
    builder = PromptBuilder()

    results = [
        SearchResult(
            chunk_id="finance:0",
            source="finance.txt",
            content="Diversification means spreading investments across different assets.",
            score=0.95,
        )
    ]

    user_context = UserContext(
        goal="Learn investing basics",
        level="beginner",
        kycStatus="verified",
        holdingSummary="Equity and mutual fund holdings",
    )

    prompt = builder.build(
        question="What is diversification?",
        results=results,
        user_context=user_context,
    )

    assert "Goal: Learn investing basics" in prompt
    assert "Level: beginner" in prompt
    assert "KYC Status: verified" in prompt
    assert "Holding Summary: Equity and mutual fund holdings" in prompt


def test_prompt_handles_missing_user_context():
    builder = PromptBuilder()

    results = [
        SearchResult(
            chunk_id="finance:0",
            source="finance.txt",
            content="Diversification means spreading investments across different assets.",
            score=0.95,
        )
    ]

    prompt = builder.build(
        question="What is diversification?",
        results=results,
    )

    assert "[No user profile context was provided.]" in prompt


def test_personalization_does_not_remove_existing_safety_instructions():
    builder = PromptBuilder()

    results = [
        SearchResult(
            chunk_id="finance:0",
            source="finance.txt",
            content="Diversification means spreading investments across different assets.",
            score=0.95,
        )
    ]

    user_context = UserContext(
        goal="Learn investing",
        level="beginner",
    )

    prompt = builder.build(
        question="What is diversification?",
        results=results,
        user_context=user_context,
    )

    assert "Never invent financial facts." in prompt
    assert "Never provide specific personalized investment advice" in prompt
    assert "Provide general financial education only." in prompt