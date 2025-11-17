from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .answer import AnswerResponse


class QuestionBase(BaseModel):
    """Base schema for Question with common fields."""

    text: str = Field(min_length=5, max_length=1000)

    model_config = ConfigDict(str_strip_whitespace=True, from_attributes=True)



class QuestionCreate(QuestionBase):
    """Schema for creating a new Question."""

    pass


class QuestionUpdate(BaseModel):
    """Schema for updating a Question."""

    id: int
    text: Optional[str] = None


class QuestionResponse(QuestionBase):
    """Schema for Question response."""

    id: int
    created_at: datetime



class QuestionWithAnswers(QuestionResponse):
    """Schema for Question with nested answers."""

    answers: list["AnswerResponse"] = []

