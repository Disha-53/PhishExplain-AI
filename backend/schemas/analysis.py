from pydantic import BaseModel, Field, field_validator


class AnalysisRequest(BaseModel):
    text: str = Field(default="", min_length=0, max_length=50000)
    url: str = Field(default="", min_length=0, max_length=5000)

    @field_validator("text")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return (value or "").strip()

    @field_validator("url")
    @classmethod
    def normalize_url(cls, value: str) -> str:
        return (value or "").strip()


class AnalysisResponse(BaseModel):
    label: str
    risk_score: int
    severity: str
    attack_type: str
    indicators: list
    xai: list
    url_analysis: dict
    knowledge: dict
    explanation: str
    recommendation: str
