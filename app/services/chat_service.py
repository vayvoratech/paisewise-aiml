from __future__ import annotations

import inspect
from collections.abc import AsyncIterable, Iterable
from typing import Any, AsyncIterator
from uuid import uuid4

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    UserContext,
)

from app.services.ai_request_replay_service import (
    AIRequestReplayService,
)

from app.services.conversation_service import (
    ConversationService,
)

from app.services.guardrail_service import (
    check_guardrail,
)

from app.services.response_validator import (
    validate_response,
)


class ChatService:
    """
    Database-independent AI chat service.

    Responsibilities:
    - Validate chat requests
    - Apply input guardrails
    - Load conversation history
    - Load user profile
    - Retrieve RAG context
    - Build LLM prompts
    - Call the LLM
    - Validate LLM responses
    - Persist conversation history
    - Record AI request replay information
    - Support streaming responses

    PostgreSQL is not accessed directly by this service.
    """

    def __init__(
        self,
        llm_provider: Any,
        rag_service: Any = None,
        prompt_builder: Any = None,
        conversation_service: Any = None,
        replay_service: Any = None,
        rag_cache_service: Any = None,
    ) -> None:
        self.llm_provider = llm_provider
        self.rag_cache_service = rag_cache_service
        self.rag_service = rag_service
        self.prompt_builder = prompt_builder
        self.conversation_service = conversation_service

        # Tests can inject a mocked replay service.
        # Production gets a real replay service automatically.
        self.replay_service = (
            replay_service
            if replay_service is not None
            else AIRequestReplayService()
        )

    # ==========================================================
    # ASYNC COMPATIBILITY
    # ==========================================================

    @staticmethod
    async def _maybe_await(value: Any) -> Any:
        """Support both synchronous and asynchronous dependencies."""
        if inspect.isawaitable(value):
            return await value
        return value

    # ==========================================================
    # USER CONTEXT
    # ==========================================================

    @staticmethod
    def _user_context_to_dict(
        user_context: UserContext,
    ) -> dict[str, Any]:
        """Convert UserContext into a Redis-compatible dictionary."""
        return {
            "goal": user_context.goal,
            "level": user_context.level,
            "kycStatus": user_context.kycStatus,
            "holdingSummary": user_context.holdingSummary,
        }

    @staticmethod
    def _dict_to_user_context(
        profile: dict[str, Any],
    ) -> UserContext:
        """Convert Redis profile dictionary back to UserContext."""
        return UserContext(
            goal=profile.get("goal"),
            level=profile.get("level"),
            kycStatus=profile.get("kycStatus"),
            holdingSummary=profile.get("holdingSummary"),
        )

    # ==========================================================
    # RESOLVE USER CONTEXT
    # ==========================================================

    async def _resolve_user_context(
        self,
        request: ChatRequest,
    ) -> UserContext | None:
        """
        Resolve user context in this order:
        1. Context supplied in the current request
        2. Context stored in Redis
        3. None
        """
        if request.userContext is not None:
            profile = self._user_context_to_dict(
                request.userContext
            )

            if self.conversation_service is not None:
                set_profile = getattr(
                    self.conversation_service,
                    "set_profile",
                    None,
                )

                if set_profile is not None:
                    result = set_profile(
                        user_id=request.userId,
                        session_id=request.sessionId,
                        profile=profile,
                    )
                    await self._maybe_await(result)

            return request.userContext

        if self.conversation_service is None:
            return None

        get_profile = getattr(
            self.conversation_service,
            "get_profile",
            None,
        )

        if get_profile is None:
            return None

        result = get_profile(
            user_id=request.userId,
            session_id=request.sessionId,
        )

        stored_profile = await self._maybe_await(result)

        if not isinstance(stored_profile, dict):
            return None

        return self._dict_to_user_context(stored_profile)

    # ==========================================================
    # HISTORY
    # ==========================================================

    async def _get_history(
        self,
        user_id: str,
        session_id: str,
    ) -> list[dict[str, str]]:
        if self.conversation_service is None:
            return []

        get_history = getattr(
            self.conversation_service,
            "get_history",
            None,
        )

        if get_history is None:
            return []

        result = get_history(
            user_id=user_id,
            session_id=session_id,
        )
        result = await self._maybe_await(result)

        if result is None:
            return []

        if not isinstance(result, list):
            try:
                return list(result)
            except TypeError:
                return []

        return result

    # ==========================================================
    # RAG
    # ==========================================================

    async def _get_rag_context(
        self,
        message: str,
    ) -> Any:
        if self.rag_service is None:
            return []

        if self.rag_cache_service is not None:
            try:
                cached = await self.rag_cache_service.get(message)
                if cached is not None:
                    return cached
            except Exception:
                # Cache errors must not block normal retrieval.
                pass

        retrieve = getattr(
            self.rag_service,
            "retrieve",
            None,
        )

        if retrieve is None:
            return []

        try:
            result = retrieve(message)
        except TypeError:
            try:
                result = retrieve(query=message)
            except TypeError:
                return []

        result = await self._maybe_await(result)

        if self.rag_cache_service is not None:
            try:
                await self.rag_cache_service.set(message, result)
            except Exception:
                # A cache write failure must not fail chat.
                pass

        return result

    # ==========================================================
    # FALLBACK PROMPT
    # ==========================================================

    @staticmethod
    def _fallback_prompt(
        question: str,
        results: Any,
        user_context: UserContext | None,
    ) -> str:
        """Build a prompt when no compatible prompt service is available."""
        if user_context is not None:
            profile = (
                f"Goal: {user_context.goal}\n"
                f"Level: {user_context.level}\n"
                f"KYC Status: {user_context.kycStatus}\n"
                f"Holding Summary: {user_context.holdingSummary}"
            )
        else:
            profile = "[No user profile context was provided.]"

        context_parts: list[str] = []

        if results:
            for result in results:
                if isinstance(result, dict):
                    content = (
                        result.get("content")
                        or result.get("text")
                        or result.get("page_content")
                    )
                else:
                    content = getattr(result, "content", None)
                    if content is None:
                        content = getattr(result, "text", None)

                if content:
                    context_parts.append(str(content))

        knowledge_context = (
            "\n\n".join(context_parts)
            if context_parts
            else "[No relevant knowledge context was retrieved.]"
        )

        return (
            "SYSTEM INSTRUCTIONS:\n"
            "Answer only using the provided context.\n\n"
            "USER PROFILE:\n"
            f"{profile}\n\n"
            "KNOWLEDGE CONTEXT:\n"
            f"{knowledge_context}\n\n"
            "USER QUESTION:\n"
            f"{question}\n\n"
            "ANSWER:"
        )

    # ==========================================================
    # BUILD PROMPT
    # ==========================================================

    async def _build_prompt(
        self,
        question: str,
        results: Any,
        user_context: UserContext | None,
    ) -> str:
        builder = self.prompt_builder

        if builder is None:
            return self._fallback_prompt(
                question=question,
                results=results,
                user_context=user_context,
            )

        # Test / PromptBuilder interface.
        build = getattr(builder, "build", None)

        if build is not None:
            result = build(
                question=question,
                results=results,
                user_context=user_context,
            )
            result = await self._maybe_await(result)

            if result is not None:
                return str(result)

        # Older PromptBuilder interface.
        build_prompt = getattr(builder, "build_prompt", None)

        if build_prompt is not None:
            try:
                result = build_prompt(
                    question=question,
                    results=results,
                    user_context=user_context,
                )
                result = await self._maybe_await(result)

                if result is not None:
                    return str(result)
            except TypeError:
                pass

            try:
                result = build_prompt(
                    question=question,
                    context=results,
                    user_context=user_context,
                )
                result = await self._maybe_await(result)

                if result is not None:
                    return str(result)
            except TypeError:
                pass

        # AIPromptService exposes get_active_prompt(prompt_key), not build().
        get_active_prompt = getattr(
            builder,
            "get_active_prompt",
            None,
        )

        if get_active_prompt is not None:
            for prompt_key in ("chat", "ai_chat", "chat_service"):
                try:
                    result = get_active_prompt(prompt_key)
                    result = await self._maybe_await(result)

                    if result is None:
                        continue

                    prompt_text = getattr(
                        result,
                        "prompt_text",
                        None,
                    )

                    if prompt_text is None:
                        prompt_text = getattr(result, "text", None)

                    if prompt_text:
                        runtime_context = self._fallback_prompt(
                            question=question,
                            results=results,
                            user_context=user_context,
                        )
                        return f"{prompt_text}\n\n{runtime_context}"
                except Exception:
                    continue

        return self._fallback_prompt(
            question=question,
            results=results,
            user_context=user_context,
        )

    # ==========================================================
    # BUILD LLM MESSAGES
    # ==========================================================

    async def _build_messages(
        self,
        request: ChatRequest,
    ) -> list[dict[str, str]]:
        history_task = self._get_history(
            user_id=request.userId,
            session_id=request.sessionId,
        )

        profile_task = self._resolve_user_context(request)
        rag_task = self._get_rag_context(request.message)

        history, user_context, rag_results = await self._gather_context(
            history_task,
            profile_task,
            rag_task,
        )

        prompt = await self._build_prompt(
            question=request.message,
            results=rag_results,
            user_context=user_context,
        )

        messages: list[dict[str, str]] = []

        if history:
            messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        return messages

    async def _gather_context(
        self,
        history_task: Any,
        profile_task: Any,
        rag_task: Any,
    ) -> tuple[list[dict[str, str]], UserContext | None, Any]:
        history, profile, rag_results = await self._gather_three(
            history_task,
            profile_task,
            rag_task,
        )

        if history is None:
            history = []

        if rag_results is None:
            rag_results = []

        return history, profile, rag_results

    async def _gather_three(
        self,
        first: Any,
        second: Any,
        third: Any,
    ) -> tuple[Any, Any, Any]:
        # Keep compatibility with ordinary MagicMock results.
        first_result = await self._maybe_await(first)
        second_result = await self._maybe_await(second)
        third_result = await self._maybe_await(third)

        return first_result, second_result, third_result

    # ==========================================================
    # LLM GENERATION
    # ==========================================================

    async def _generate(
        self,
        messages: list[dict[str, str]],
    ) -> str:
        generate = getattr(
            self.llm_provider,
            "generate",
            None,
        )

        if generate is None:
            return ""

        result = generate(messages)
        result = await self._maybe_await(result)

        if result is None:
            return ""

        if isinstance(result, str):
            return result

        text = getattr(result, "text", None)

        if text is not None:
            return str(text)

        if isinstance(result, dict):
            for key in ("text", "content", "response", "answer"):
                if key in result:
                    value = result[key]
                    return "" if value is None else str(value)

        return str(result)

    # ==========================================================
    # STORE CONVERSATION
    # ==========================================================

    async def _store_message(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        if self.conversation_service is None:
            return

        add_message = getattr(
            self.conversation_service,
            "add_message",
            None,
        )

        if add_message is None:
            return

        result = add_message(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content,
        )
        await self._maybe_await(result)

    async def _store_conversation(
        self,
        user_id: str,
        session_id: str,
        question: str,
        response: str,
    ) -> None:
        await self._store_message(
            user_id=user_id,
            session_id=session_id,
            role="user",
            content=question,
        )

        if response:
            await self._store_message(
                user_id=user_id,
                session_id=session_id,
                role="assistant",
                content=response,
            )

    # ==========================================================
    # REPLAY
    # ==========================================================

    async def _record_replay(
        self,
        request: ChatRequest,
        messages: list[dict[str, str]],
    ) -> None:
        if self.replay_service is None:
            return

        record_request = getattr(
            self.replay_service,
            "record_request",
            None,
        )

        if record_request is None:
            return

        model = getattr(self.llm_provider, "model", None)
        request_id = str(uuid4())

        result = record_request(
            request_id=request_id,
            service_name="chat_service",
            model=model,
            inputs={"messages": messages},
        )
        await self._maybe_await(result)

    # ==========================================================
    # PROCESS CHAT
    # ==========================================================

    async def process_chat(
        self,
        request: ChatRequest | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        message: str | None = None,
    ) -> ChatResponse:
        """
        Accept either process_chat(request) or keyword user/session/message.
        """
        if request is None:
            if user_id is None or session_id is None or message is None:
                raise TypeError(
                    "process_chat requires a ChatRequest or "
                    "user_id, session_id and message"
                )

            request = ChatRequest(
                userId=user_id,
                sessionId=session_id,
                message=message,
            )

        if not isinstance(request, ChatRequest):
            raise TypeError("request must be a ChatRequest")

        message = request.message.strip()

        if not message:
            raise ValueError("message cannot be empty")

        guardrail = check_guardrail(message)

        if guardrail.blocked:
            return ChatResponse(
                status="blocked",
                responseId=None,
                message=(
                    guardrail.message
                    or "This question cannot be processed."
                ),
                category=guardrail.category.value,
            )

        request_for_llm = request.model_copy(
            update={"message": message}
        )

        messages = await self._build_messages(request_for_llm)

        await self._record_replay(
            request=request_for_llm,
            messages=messages,
        )

        response = await self._generate(messages)
        response = response.strip() if response else ""

        if not response:
            return ChatResponse(
                status="blocked",
                responseId=None,
                message="The AI service returned an empty response.",
                category="response_validation",
            )

        validation = validate_response(response)

        if not validation.valid:
            return ChatResponse(
                status="blocked",
                responseId=None,
                message=(
                    validation.message
                    or "The generated response could not be safely returned."
                ),
                category="response_validation",
            )

        await self._store_conversation(
            user_id=request.userId,
            session_id=request.sessionId,
            question=message,
            response=response,
        )

        return ChatResponse(
            status="success",
            responseId=str(uuid4()),
            message=response,
            category=guardrail.category.value,
        )

    # ==========================================================
    # STREAM CHAT
    # ==========================================================

    async def stream_chat(
        self,
        request: ChatRequest | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        message: str | None = None,
    ) -> AsyncIterator[str]:
        """
        Accept either stream_chat(request) or keyword user/session/message.
        """
        if not isinstance(request, ChatRequest):
            if user_id is None or session_id is None or message is None:
                raise TypeError(
                    "stream_chat requires a ChatRequest or "
                    "user_id, session_id and message"
                )

            request = ChatRequest(
                userId=user_id,
                sessionId=session_id,
                message=message,
            )

        message = request.message.strip()

        if not message:
            raise ValueError("message cannot be empty")

        request_for_llm = request.model_copy(
            update={"message": message}
        )

        guardrail = check_guardrail(message)

        if guardrail.blocked:
            yield (
                guardrail.message
                or "This question cannot be processed."
            )
            return

        messages = await self._build_messages(request_for_llm)

        stream_method = getattr(
            self.llm_provider,
            "stream",
            None,
        )

        if stream_method is None:
            response = await self._generate(messages)
            response = response.strip() if response else ""

            if not response:
                yield "The AI service returned an empty response."
                return

            validation = validate_response(response)

            if not validation.valid:
                yield (
                    validation.message
                    or "The generated response could not be safely returned."
                )
                return

            yield response

            await self._store_conversation(
                user_id=request.userId,
                session_id=request.sessionId,
                question=message,
                response=response,
            )

            await self._record_replay(
                request=request_for_llm,
                messages=messages,
            )
            return

        result = stream_method(messages)

        if inspect.isawaitable(result):
            result = await result

        response_parts: list[str] = []

        if isinstance(result, AsyncIterable):
            async for chunk in result:
                chunk_text = self._chunk_text(chunk)

                if not chunk_text:
                    continue

                response_parts.append(chunk_text)
                yield chunk_text

        elif isinstance(result, Iterable) and not isinstance(
            result,
            (str, bytes),
        ):
            for chunk in result:
                chunk_text = self._chunk_text(chunk)

                if not chunk_text:
                    continue

                response_parts.append(chunk_text)
                yield chunk_text

        else:
            raise TypeError(
                "LLM stream must return an iterable of text chunks"
            )

        response = "".join(response_parts).strip()

        if not response:
            return

        # Chunks have already been sent; this validation gates persistence.
        validation = validate_response(response)

        if not validation.valid:
            return

        await self._store_conversation(
            user_id=request.userId,
            session_id=request.sessionId,
            question=message,
            response=response,
        )

        await self._record_replay(
            request=request_for_llm,
            messages=messages,
        )

    @staticmethod
    def _chunk_text(chunk: Any) -> str:
        if chunk is None:
            return ""

        if isinstance(chunk, str):
            return chunk

        text = getattr(chunk, "text", None)

        if text is not None:
            return str(text)

        if isinstance(chunk, dict):
            for key in ("text", "content", "response", "answer"):
                if chunk.get(key) is not None:
                    return str(chunk[key])

        return str(chunk)

    # ==========================================================
    # LEGACY ALIASES
    # ==========================================================

    async def chat(
        self,
        user_id: str,
        session_id: str,
        question: str,
    ) -> str:
        request = ChatRequest(
            userId=user_id,
            sessionId=session_id,
            message=question,
        )

        response = await self.process_chat(request)
        return response.message

    async def process_message(
        self,
        user_id: str,
        session_id: str,
        question: str,
    ) -> str:
        return await self.chat(
            user_id=user_id,
            session_id=session_id,
            question=question,
        )