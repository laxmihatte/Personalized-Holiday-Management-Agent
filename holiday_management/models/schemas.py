from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class PlanRequest(BaseModel):
    content: str = Field(
        ..., min_length=5, max_length=1000,
        description="Free-text description of the desired trip.",
    )
    source: str = Field("User", min_length=1, max_length=50)
    user_id: str = Field(
        "guest", min_length=1, max_length=50,
        description="Identifier used to personalise and remember preferences.",
    )
    tags: Optional[List[str]] = Field(default_factory=list)

    @field_validator("content")
    def content_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Trip description must not be empty or whitespace.")
        return value.strip()


class AgentMessage(BaseModel):
    source: str
    content: str


class PlanResponse(BaseModel):
    status: str = "success"
    user_id: str
    signature: str
    message_count: int = Field(0, ge=0)
    messages: List[AgentMessage] = Field(default_factory=list)
    remembered: List[str] = Field(
        default_factory=list,
        description="Preferences recalled from memory and used for personalisation.",
    )
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
