from pydantic import BaseModel, Field


class UserContext(BaseModel):
    """
    User context supplied by the calling application.

    The AI service does not fetch this information
    from PostgreSQL.
    """

    goal: str | None = None

    level: str | None = None

    kycStatus: str | None = None

    holdingSummary: str | None = None


class ChatRequest(BaseModel):
    """
    JSON input for the AI chat service.
    """

    userId: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    sessionId: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )

    # User context is supplied by the caller.
    #
    # It is NOT fetched from PostgreSQL.
    userContext: UserContext | None = None


class ChatResponse(BaseModel):
    """
    JSON output returned by the AI service.
    """

    status: str

    responseId: str | None = None

    message: str

    category: str


class ChatFeedbackRequest(BaseModel):
    """
    JSON input for AI response feedback.
    """

    responseId: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    userId: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    category: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    feedback: str = Field(
        ...,
        pattern="^(up|down)$",
    )


class ChatFeedbackResponse(BaseModel):
    """
    JSON response after feedback processing.
    """

    status: str

    message: str


class ChatFeedbackAnalyticsResponse(BaseModel):
    """
    Feedback analytics grouped by category.
    """

    category: str

    thumbs_up: int

    thumbs_down: int

    total_feedback: int