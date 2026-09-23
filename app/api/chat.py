from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.redis import redis_client
from app.schemas.chat import (
    ChatFeedbackAnalyticsResponse,
    ChatFeedbackRequest,
    ChatFeedbackResponse,
    ChatRequest,
    ChatResponse,
)
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService
from app.services.feedback_service import FeedbackService
from app.services.llm.gemini_provider import GeminiProvider
from app.services.rag.prompt_builder import PromptBuilder
from app.services.rag.rag_service import RAGService


router = APIRouter(
    prefix="/ai",
    tags=["AI Chat"],
)


# --------------------------------------------------
# LLM
# --------------------------------------------------

llm_provider = GeminiProvider()


# --------------------------------------------------
# RAG
# --------------------------------------------------

rag_service = RAGService(
    knowledge_base_path="data/knowledge_base",
)


# --------------------------------------------------
# Prompt Builder
# --------------------------------------------------

prompt_builder = PromptBuilder(
    max_context_chunks=5,
    max_context_characters=12000,
)


# --------------------------------------------------
# Conversation Service
# --------------------------------------------------

# Redis is used ONLY for short-lived
# conversation history.

conversation_service = ConversationService(
    redis_client=redis_client,
)


# --------------------------------------------------
# Chat Service
# --------------------------------------------------

# ChatService does not access PostgreSQL.

chat_service = ChatService(
    llm_provider=llm_provider,
    rag_service=rag_service,
    prompt_builder=prompt_builder,
    conversation_service=conversation_service,
)


# --------------------------------------------------
# Feedback Service
# --------------------------------------------------

# Feedback is a separate component.
#
# PostgreSQL is used only here for:
# - feedback persistence
# - weekly analytics

feedback_service = FeedbackService()


# ==================================================
# CHAT
# ==================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
) -> ChatResponse:
    """
    Process JSON input and return JSON output.

    User profile/holding information is supplied
    through JSON.

    Conversation history is retrieved from Redis.

    PostgreSQL is NOT used by ChatService.
    """

    return await chat_service.process_chat(
        request
    )


# ==================================================
# STREAMING CHAT
# ==================================================

@router.post(
    "/chat/stream",
)
async def stream_chat(
    request: ChatRequest,
) -> StreamingResponse:
    """
    Stream the AI response.

    Conversation history comes from Redis.
    """

    return StreamingResponse(
        chat_service.stream_chat(request),
        media_type="text/plain",
    )


# ==================================================
# FEEDBACK
# ==================================================

@router.post(
    "/chat/feedback",
    response_model=ChatFeedbackResponse,
)
async def submit_chat_feedback(
    request: ChatFeedbackRequest,
) -> ChatFeedbackResponse:
    """
    Submit feedback for an AI response.

    Feedback is persisted separately from
    ChatService.
    """

    result = feedback_service.submit_feedback(
        response_id=request.responseId,
        user_id=request.userId,
        category=request.category,
        feedback=request.feedback,
    )

    return ChatFeedbackResponse(
        status=result["status"],
        message=result["message"],
    )


# ==================================================
# FEEDBACK ANALYTICS
# ==================================================

@router.get(
    "/chat/feedback/analytics",
    response_model=list[
        ChatFeedbackAnalyticsResponse
    ],
)
async def get_chat_feedback_analytics():
    """
    Return weekly feedback analytics.

    Analytics are retrieved from the separate
    PostgreSQL feedback component.
    """

    return feedback_service.get_weekly_analytics()