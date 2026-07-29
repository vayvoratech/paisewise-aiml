from pydantic import BaseModel


class FeatureRefreshRequest(BaseModel):
    userId: str