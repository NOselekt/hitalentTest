from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnswerBase(BaseModel):
    """Base schema for Answer with common fields."""

    text: str = Field(min_length=1, max_length=1000)

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)


class AnswerCreate(AnswerBase):
    """Schema for creating an Answer via question endpoint (question_id from path)."""

    user_id: UUID


class AnswerUpdate(BaseModel):
    """Schema for updating an Answer."""

    text: Optional[str]
    id: Optional[UUID]


class AnswerResponse(AnswerBase):
    """Schema for Answer response."""

    id: int
    user_id: UUID
    created_at: datetime
    question_id: int
