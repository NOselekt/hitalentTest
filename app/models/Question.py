from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.backend.Base import Base

if TYPE_CHECKING:
    from .Answer import Answer


class Question(Base):
    """
    Model class for questions.
    """

    text: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    answers: Mapped[list["Answer"]] = relationship(
        backref="questions", cascade="all, delete-orphan"
    )
