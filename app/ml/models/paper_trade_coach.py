from pydantic import BaseModel, Field

from uuid import UUID


class PaperTradeCoachRequest(BaseModel):

    order_id: int = Field(gt=0)


class LessonRecommendation(BaseModel):

    id: str

    title: str


class PaperTradeCoachResponse(BaseModel):

    order_id: int

    learning_point: str

    lesson: LessonRecommendation