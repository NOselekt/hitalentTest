from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.async_database import get_database
from app.schemas.answer import AnswerResponse
from app.routers.dependencies import get_answer_by_id

router = APIRouter(prefix="/answers", tags=["answers"])


@router.get("/{answer_id}", response_model=AnswerResponse)
async def get_answer(
    answer_id: int, database: Annotated[AsyncSession, Depends(get_database)]
):
    """Get an answer by ID."""
    answer = await get_answer_by_id(database=database, answer_id=answer_id)

    return answer


@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(
    answer_id: int, database: Annotated[AsyncSession, Depends(get_database)]
):
    """Delete an answer by ID."""
    answer = await get_answer_by_id(database=database, answer_id=answer_id)

    await database.delete(answer)
    await database.commit()
