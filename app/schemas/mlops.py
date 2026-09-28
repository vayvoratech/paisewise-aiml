from datetime import datetime

from pydantic import BaseModel, Field


class ModelVersionMetadata(BaseModel):
    model_name: str = Field(min_length=1)
    version: str = Field(min_length=1)
    created_at: datetime
    metrics: dict[str, float]
    dataset_version: str = Field(min_length=1)