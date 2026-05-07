from pydantic import BaseModel, Field
from typing import Literal

class EmailInput(BaseModel):
    sender: str
    subject: str
    body: str
    timestamp: str # e.g. "2026-05-06T14:30:00"

class EmailClassification(BaseModel):
    model_config = {"validate_assignment": True}  # ← re-validates on every assignment
    category: Literal["urgent","needs_reply","fyi","spam"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    draft_reply: str | None = None

class TriageReport(BaseModel):
    results: list[EmailClassification]
    