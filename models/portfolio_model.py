from pydantic import BaseModel


class PortfolioRequest(BaseModel):
    user_id: str
    language: str = "english"