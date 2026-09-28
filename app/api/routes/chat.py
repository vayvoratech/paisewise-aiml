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
from app.services.ai_prompt_service import AIPromptService
from app.services.chat_service import ChatService
from app.services.conversation_service import ConversationService
from app.services.feedback_service import FeedbackService
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm_cost_service import LLMCostService
from app.services.llm_usage_repository import LLMUsageRepository
from app.services.rag.predictive_rag_cache_service import (
    PredictiveRAGCacheService,
    RAGQueryPopularityService,
)
from app.services.rag.prompt_builder import PromptBuilder
from app.services.rag.rag_query_cache_service import (
    RAGQueryCacheService,
)
from app.services.rag.rag_service import RAGService
from app.services.slack_notification_service import (
    SlackNotificationService,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI Chat"],
)


# --------------------------------------------------
# RAG cache
# --------------------------------------------------

base_rag_query_cache = RAGQueryCacheService(redis_client)
rag_query_popularity = RAGQueryPopularityService(redis_client)

rag_query_cache = PredictiveRAGCacheService(
    cache_service=base_rag_query_cache,
    popularity_service=rag_query_popularity,
)


# --------------------------------------------------
# LLM
# --------------------------------------------------

usage_repository = LLMUsageRepository()

cost_service = LLMCostService.from_environment(
    usage_repository=usage_repository,
)

llm_provider = GeminiProvider(
    cost_service=cost_service,
)


# --------------------------------------------------
# RAG
# --------------------------------------------------

# RAG is configured during application startup.
rag_service: RAGService | None = None


# --------------------------------------------------
# Prompt builder
# --------------------------------------------------

prompt_service = AIPromptService()

prompt_builder = PromptBuilder(
    max_context_chunks=5,
    max_context_characters=12000,
    prompt_service=prompt_service,
    prompt_key="chat_system_prompt",
)


# --------------------------------------------------
# Conversation service
# --------------------------------------------------

conversation_service = ConversationService(
    redis_client=redis_client,
)


# --------------------------------------------------
# Chat service
# --------------------------------------------------

# ChatService is created after the startup RAG instance is configured.
chat_service: ChatService | None = None


def configure_rag_service(service: RAGService) -> None:
    """Configure the startup-initialized RAG and chat services."""
    global rag_service
    global chat_service

    rag_service = service

    chat_service = ChatService(
        llm_provider=llm_provider,
        rag_service=rag_service,
        prompt_builder=prompt_builder,
        conversation_service=conversation_service,
        rag_cache_service=rag_query_cache,
    )


async def prewarm_rag_cache(
    queries: list[str] | None = None,
) -> int:
    """Prewarm popular cached queries, or an explicitly supplied list."""
    if rag_service is None:
        return 0

    return await rag_query_cache.prewarm(
        rag_service=rag_service,
        queries=queries,
    )


def get_chat_service() -> ChatService:
    """Return the configured ChatService."""
    if chat_service is None:
        raise RuntimeError("Chat service is not initialized")

    return chat_service


# --------------------------------------------------
# Feedback service
# --------------------------------------------------

# Feedback persistence and analytics are separate from ChatService.
feedback_service = FeedbackService(
    slack_service=SlackNotificationService(),
)


# ==================================================
# CHAT
# ==================================================

@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a chat request and return a JSON response."""
    return await get_chat_service().process_chat(request)


# ==================================================
# STREAMING CHAT
# ==================================================

@router.post("/chat/stream")
async def stream_chat(request: ChatRequest) -> StreamingResponse:
    """Stream the AI response."""
    return StreamingResponse(
        get_chat_service().stream_chat(request),
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
    """Submit feedback for an AI response."""
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
    response_model=list[ChatFeedbackAnalyticsResponse],
)
async def get_chat_feedback_analytics():
    """Return weekly feedback analytics."""
    return feedback_service.get_weekly_analytics()