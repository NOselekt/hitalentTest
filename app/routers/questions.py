from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.backend.async_database import get_database
from app.models.Question import Question
from app.models.Answer import Answer
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionWithAnswers
from app.schemas.answer import AnswerResponse, AnswerCreate
from app.routers.dependencies import get_question_by_id

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/", response_model=list[QuestionResponse])
async def get_questions(database: Annotated[AsyncSession, Depends(get_database)]):
    """Get a list of all questions."""

    result = (await database.scalars(select(Question))).all()
    return result


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    database: Annotated[AsyncSession, Depends(get_database)],
):
    """Create a new question."""

    if not question_data.text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question text cannot be empty",
        )

    same_question = await database.scalar(
        select(Question).where(Question.text == question_data.text)
    )
    if same_question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question with this text already exists",
        )

    new_question = Question(**question_data.model_dump())
    database.add(new_question)
    await database.commit()
    await database.refresh(new_question)
    return new_question


@router.get("/{question_id}", response_model=QuestionWithAnswers)
async def get_question(
    question_id: int, database: Annotated[AsyncSession, Depends(get_database)]
):
    """Get a question by ID with all its answers."""

    question = await get_question_by_id(database=database, question_id=question_id)

    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int, database: Annotated[AsyncSession, Depends(get_database)]
):
    """Delete a question by ID."""

    question = await get_question_by_id(database=database, question_id=question_id)

    await database.delete(question)
    await database.commit()


@router.post(
    "/{question_id}/answers/",
    response_model=AnswerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_answer(
    question_id: int,
    answer_data: AnswerCreate,
    database: Annotated[AsyncSession, Depends(get_database)],
):
    """Add an answer to a question."""
    if not answer_data.text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answer text cannot be empty",
        )

    await get_question_by_id(database=database, question_id=question_id)

    new_answer = Answer(
        text=answer_data.text,
        question_id=question_id,
        user_id=answer_data.user_id,
    )
    database.add(new_answer)
    await database.commit()
    await database.refresh(new_answer)
    return new_answer
