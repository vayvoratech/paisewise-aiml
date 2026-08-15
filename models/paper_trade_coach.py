from pydantic import BaseModel
from uuid import UUID


class PaperTradeCoachRequest(BaseModel):
    order_id: UUID


class LessonRecommendation(BaseModel):
    id: str
    title: str


class PaperTradeCoachResponse(BaseModel):
    order_id: UUID
    learning_point: str
    lesson: LessonRecommendation