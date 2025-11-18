from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from typing import Annotated

from app.backend.async_database import get_database
from app.models.Answer import Answer
from app.models.Question import Question


async def get_question_by_id(
    question_id: int, database: Annotated[AsyncSession, Depends(get_database)]
) -> Question:
    """Get a question by ID."""

    question = await database.scalar(select(Question).where(Question.id == question_id))

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question with id {question_id} not found",
        )

    return question


async def get_answer_by_id(
    answer_id: int, database: Annotated[AsyncSession, Depends(get_database)]
) -> Answer:
    """Get an answer by ID."""

    answer = await database.scalar(select(Answer).where(Answer.id == answer_id))

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Answer with id {answer_id} not found",
        )

    return answer
