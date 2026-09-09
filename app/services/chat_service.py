from typing import AsyncIterator
from uuid import uuid4

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    UserContext,
)
from app.services.llm.gemini_provider import (
    GeminiProvider,
)
from app.services.rag.rag_service import (
    RAGService,
)
from app.services.rag.prompt_builder import (
    PromptBuilder,
)
from app.services.response_validator import (
    validate_response,
)
from app.services.guardrail_service import (
    check_guardrail,
)
from app.services.conversation_service import (
    ConversationService,
)


class ChatService:
    """
    Database-independent AI chat service.

    Flow:

        JSON Request
            ↓
        Validation
            ↓
        Guardrail
            ↓
        Redis Profile
            ↓
        Redis Conversation History
            ↓
        RAG
            ↓
        User Profile Injection
            ↓
        Prompt Builder
            ↓
        LLM
            ↓
        Response Validator
            ↓
        JSON Response

    PostgreSQL is not accessed by this service.

    User profile is supplied through JSON on the first
    request and persisted in Redis for the session.

    Subsequent requests can omit userContext. The profile
    will automatically be retrieved from Redis.
    """

    def __init__(
        self,
        llm_provider: GeminiProvider,
        rag_service: RAGService,
        prompt_builder: PromptBuilder,
        conversation_service: ConversationService,
    ) -> None:
        self.llm_provider = llm_provider
        self.rag_service = rag_service
        self.prompt_builder = prompt_builder
        self.conversation_service = conversation_service

    # ==================================================
    # Convert UserContext to dictionary
    # ==================================================

    @staticmethod
    def _user_context_to_dict(
        user_context: UserContext,
    ) -> dict[str, str | None]:
        """
        Convert UserContext into a JSON-compatible
        dictionary for Redis storage.
        """

        return {
            "goal": user_context.goal,
            "level": user_context.level,
            "kycStatus": user_context.kycStatus,
            "holdingSummary": user_context.holdingSummary,
        }

    # ==================================================
    # Convert dictionary back to UserContext
    # ==================================================

    @staticmethod
    def _dict_to_user_context(
        profile: dict,
    ) -> UserContext:
        """
        Convert a Redis profile dictionary back into
        the application's UserContext model.
        """

        return UserContext(
            goal=profile.get("goal"),
            level=profile.get("level"),
            kycStatus=profile.get("kycStatus"),
            holdingSummary=profile.get(
                "holdingSummary"
            ),
        )

    # ==================================================
    # Resolve session profile
    # ==================================================

    def _resolve_user_context(
        self,
        request: ChatRequest,
    ) -> UserContext | None:
        """
        Resolve the profile for the current session.

        Priority:

        1. Current request userContext
        2. Previously stored Redis profile
        3. None

        When the request contains userContext, the exact
        object from the request is returned. This preserves
        compatibility with existing tests and callers.
        """

        # ----------------------------------------------
        # Current request contains profile
        # ----------------------------------------------

        if request.userContext is not None:

            profile = self._user_context_to_dict(
                request.userContext
            )

            self.conversation_service.set_profile(
                user_id=request.userId,
                session_id=request.sessionId,
                profile=profile,
            )

            return request.userContext

        # ----------------------------------------------
        # No profile in request.
        # Try Redis.
        # ----------------------------------------------

        stored_profile = (
            self.conversation_service.get_profile(
                user_id=request.userId,
                session_id=request.sessionId,
            )
        )

        # ----------------------------------------------
        # No stored profile
        # ----------------------------------------------

        if stored_profile is None:
            return None

        # ----------------------------------------------
        # Protect against incorrectly configured mocks
        # or invalid Redis values.
        # ----------------------------------------------

        if not isinstance(
            stored_profile,
            dict,
        ):
            return None

        return self._dict_to_user_context(
            stored_profile
        )

    # ==================================================
    # Build LLM Messages
    # ==================================================

    def _build_messages(
        self,
        request: ChatRequest,
    ) -> list[dict[str, str]]:
        """
        Build the messages sent to the LLM.

        Includes:

        - Previous Redis conversation history
        - Session-persistent user profile
        - RAG knowledge context
        - Current user question

        No PostgreSQL lookup is performed.
        """

        # ----------------------------------------------
        # 1. Resolve profile
        # ----------------------------------------------

        user_context = self._resolve_user_context(
            request
        )

        # ----------------------------------------------
        # 2. RAG
        # ----------------------------------------------

        results = self.rag_service.retrieve(
            request.message
        )

        # ----------------------------------------------
        # 3. Prompt
        # ----------------------------------------------

        prompt = self.prompt_builder.build(
            question=request.message,
            results=results,
            user_context=user_context,
        )

        # ----------------------------------------------
        # 4. Conversation history
        # ----------------------------------------------

        history = self.conversation_service.get_history(
            user_id=request.userId,
            session_id=request.sessionId,
        )

        messages: list[dict[str, str]] = []

        messages.extend(history)

        # Current prompt is added as the latest
        # user message.
        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        return messages

    # ==================================================
    # Process Chat
    # ==================================================

    async def process_chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """
        Process a JSON chat request and return
        a structured JSON response.
        """

        # ----------------------------------------------
        # 1. Validate request
        # ----------------------------------------------

        if not isinstance(
            request,
            ChatRequest,
        ):
            raise TypeError(
                "request must be a ChatRequest"
            )

        message = request.message.strip()

        if not message:
            raise ValueError(
                "message cannot be empty"
            )

        # ----------------------------------------------
        # 2. Input Guardrail
        # ----------------------------------------------

        guardrail = check_guardrail(
            message
        )

        if guardrail.blocked:
            return ChatResponse(
                status="blocked",
                responseId=None,
                message=(
                    guardrail.message
                    or (
                        "This question cannot be "
                        "processed."
                    )
                ),
                category=guardrail.category.value,
            )

        # ----------------------------------------------
        # 3. Build messages
        # ----------------------------------------------

        messages = self._build_messages(
            request
        )

        # ----------------------------------------------
        # 4. LLM
        # ----------------------------------------------

        response = await self.llm_provider.generate(
            messages
        )

        if not response or not response.strip():
            return ChatResponse(
                status="blocked",
                responseId=None,
                message=(
                    "The AI service returned "
                    "an empty response."
                ),
                category=guardrail.category.value,
            )

        # ----------------------------------------------
        # 5. Response Validation
        # ----------------------------------------------

        validation = validate_response(
            response
        )

        if not validation.valid:
            return ChatResponse(
                status="blocked",
                responseId=None,
                message=(
                    validation.message
                    or (
                        "The generated response "
                        "could not be safely returned."
                    )
                ),
                category="response_validation",
            )

        # ----------------------------------------------
        # 6. Response ID
        # ----------------------------------------------

        response_id = str(uuid4())

        # ----------------------------------------------
        # 7. Store user message
        # ----------------------------------------------

        self.conversation_service.add_message(
            user_id=request.userId,
            session_id=request.sessionId,
            role="user",
            content=message,
        )

        # ----------------------------------------------
        # 8. Store assistant response
        # ----------------------------------------------

        self.conversation_service.add_message(
            user_id=request.userId,
            session_id=request.sessionId,
            role="assistant",
            content=response.strip(),
        )

        # ----------------------------------------------
        # 9. Return response
        # ----------------------------------------------

        return ChatResponse(
            status="success",
            responseId=response_id,
            message=response.strip(),
            category=guardrail.category.value,
        )

    # ==================================================
    # Streaming
    # ==================================================

    async def stream_chat(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[str]:
        """
        Stream an AI response.

        User profile is resolved from the current request
        or from the Redis session profile.
        """

        # ----------------------------------------------
        # 1. Validate request
        # ----------------------------------------------

        if not isinstance(
            request,
            ChatRequest,
        ):
            raise TypeError(
                "request must be a ChatRequest"
            )

        message = request.message.strip()

        if not message:
            raise ValueError(
                "message cannot be empty"
            )

        # ----------------------------------------------
        # 2. Guardrail
        # ----------------------------------------------

        guardrail = check_guardrail(
            message
        )

        if guardrail.blocked:
            yield (
                guardrail.message
                or (
                    "This question cannot be "
                    "processed."
                )
            )
            return

        # ----------------------------------------------
        # 3. Build messages
        # ----------------------------------------------

        messages = self._build_messages(
            request
        )

        # ----------------------------------------------
        # 4. Stream LLM response
        # ----------------------------------------------

        response_parts: list[str] = []

        async for chunk in self.llm_provider.stream(
            messages
        ):
            if chunk:
                response_parts.append(chunk)
                yield chunk

        response = "".join(
            response_parts
        ).strip()

        # ----------------------------------------------
        # 5. Validate response
        # ----------------------------------------------

        validation = validate_response(
            response
        )

        if not validation.valid:
            yield (
                validation.message
                or (
                    "The generated response "
                    "could not be safely returned."
                )
            )
            return

        # ----------------------------------------------
        # 6. Store conversation
        # ----------------------------------------------

        self.conversation_service.add_message(
            user_id=request.userId,
            session_id=request.sessionId,
            role="user",
            content=message,
        )

        self.conversation_service.add_message(
            user_id=request.userId,
            session_id=request.sessionId,
            role="assistant",
            content=response,
        )