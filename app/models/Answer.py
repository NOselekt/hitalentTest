from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, Integer, UUID, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship


from app.backend.Base import Base

if TYPE_CHECKING:
    from .Question import Question


class Answer(Base):
    """
    Model class for questions.
    """

    user_id: Mapped[UUID] = mapped_column(
        UUID, nullable=False, default=uuid4()
    )  # ForeignKey('users.id')
    text: Mapped[str] = mapped_column(Text, nullable=False)
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"))

    question: Mapped["Question"] = relationship(backref="answer")
