from app.services.rag.prompt_builder import PromptBuilder


def test_prompt_handles_missing_knowledge_context():
    builder = PromptBuilder()

    prompt = builder.build(
        question="What is the exact future price of XYZ stock?",
        results=[],
    )

    assert "[No relevant knowledge context was retrieved.]" in prompt
    assert (
        "If the provided context does not contain enough information"
        in prompt
    )


def test_prompt_prevents_invented_financial_facts():
    builder = PromptBuilder()

    prompt = builder.build(
        question="Tell me something about an unknown company.",
        results=[],
    )

    assert "Never invent financial facts." in prompt
    assert "say that you do not have enough" in prompt
    assert "information in the available knowledge." in prompt


def test_prompt_preserves_general_education_boundary():
    builder = PromptBuilder()

    prompt = builder.build(
        question="Should I buy this stock?",
        results=[],
    )

    assert (
        "Never provide specific personalized investment advice"
        in prompt
    )
    assert "Provide general financial education only." in prompt