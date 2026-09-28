from app.schemas.chat import UserContext
from app.services.rag.vector_store import SearchResult
from app.services.ai_prompt_service import AIPromptService


SYSTEM_PROMPT = """
You are a friendly financial learning assistant.

Answer only using the provided knowledge context.

If the provided context does not contain enough information
to answer the question, say that you do not have enough
information in the available knowledge.

Never invent financial facts.

Never provide specific personalized investment advice,
including personalized buy, sell, or portfolio-allocation
recommendations.

Provide general financial education only.
""".strip()


class PromptBuilder:
    """
    Builds grounded prompts from retrieved RAG context
    and user profile context.

    The existing SYSTEM_PROMPT remains the default so
    existing callers continue to work without requiring
    PostgreSQL.

    When an AIPromptService is explicitly supplied,
    the active database-backed prompt is used instead.

    User profile information is supplied by the calling
    application or retrieved from the session context.

    This class does not fetch user information
    from PostgreSQL.
    """

    def __init__(
        self,
        max_context_chunks: int = 5,
        max_context_characters: int = 12000,
        prompt_service: AIPromptService | None = None,
        prompt_key: str = "chat_system_prompt",
    ):
        if max_context_chunks <= 0:
            raise ValueError(
                "max_context_chunks must be greater than 0"
            )

        if max_context_characters <= 0:
            raise ValueError(
                "max_context_characters must be greater than 0"
            )

        if not isinstance(prompt_key, str):
            raise TypeError(
                "prompt_key must be a string"
            )

        if not prompt_key.strip():
            raise ValueError(
                "prompt_key cannot be empty"
            )

        self.max_context_chunks = max_context_chunks
        self.max_context_characters = max_context_characters

        # Optional DB-backed prompt service.
        #
        # If this is None, the existing SYSTEM_PROMPT
        # continues to be used exactly as before.
        self.prompt_service = prompt_service

        self.prompt_key = prompt_key.strip()

    def build(
        self,
        question: str,
        results: list[SearchResult],
        user_context: UserContext | None = None,
    ) -> str:
        """
        Build the final grounded prompt.

        The existing prompt-building behavior is preserved.

        If a prompt service is configured, the active prompt
        is retrieved from the database at runtime.
        Otherwise, the existing SYSTEM_PROMPT is used.
        """

        if not isinstance(question, str):
            raise TypeError(
                "question must be a string"
            )

        if not question.strip():
            raise ValueError(
                "question cannot be empty"
            )

        # --------------------------------------------------
        # System prompt
        # --------------------------------------------------

        system_prompt = SYSTEM_PROMPT

        if self.prompt_service is not None:
            active_prompt = (
                self.prompt_service.get_active_prompt(
                    self.prompt_key
                )
            )

            system_prompt = active_prompt.prompt_text

        # --------------------------------------------------
        # RAG context
        # --------------------------------------------------

        selected_results = results[
            :self.max_context_chunks
        ]

        context_parts = []
        total_characters = 0

        for index, result in enumerate(
            selected_results,
            start=1,
        ):
            content = result.content.strip()

            if not content:
                continue

            remaining = (
                self.max_context_characters
                - total_characters
            )

            if remaining <= 0:
                break

            content = content[:remaining]

            context_parts.append(
                f"[Context {index}]\n"
                f"Source: {result.source}\n"
                f"{content}"
            )

            total_characters += len(content)

        if context_parts:
            context = "\n\n".join(
                context_parts
            )
        else:
            context = (
                "[No relevant knowledge context "
                "was retrieved.]"
            )

        # --------------------------------------------------
        # User profile
        # --------------------------------------------------

        profile_parts = []

        if user_context is not None:

            if user_context.goal:
                profile_parts.append(
                    f"Goal: {user_context.goal}"
                )

            if user_context.level:
                profile_parts.append(
                    f"Level: {user_context.level}"
                )

            if user_context.kycStatus:
                profile_parts.append(
                    "KYC Status: "
                    f"{user_context.kycStatus}"
                )

            if user_context.holdingSummary:
                profile_parts.append(
                    "Holding Summary: "
                    f"{user_context.holdingSummary}"
                )

        if profile_parts:
            user_profile = "\n".join(
                profile_parts
            )
        else:
            user_profile = (
                "[No user profile context "
                "was provided.]"
            )

        # --------------------------------------------------
        # Final prompt
        # --------------------------------------------------

        return (
            f"SYSTEM INSTRUCTIONS:\n"
            f"{system_prompt}\n\n"
            f"USER PROFILE:\n"
            f"{user_profile}\n\n"
            f"KNOWLEDGE CONTEXT:\n"
            f"{context}\n\n"
            f"USER QUESTION:\n"
            f"{question.strip()}\n\n"
            f"ANSWER:"
        )