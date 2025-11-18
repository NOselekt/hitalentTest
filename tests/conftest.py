from __future__ import annotations

import sys
from pathlib import Path
import importlib.util
from typing import AsyncGenerator

import pytest
from fastapi import HTTPException, status
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload
from sqlalchemy.pool import StaticPool

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    import aiosqlite  # type: ignore # noqa: F401
except ModuleNotFoundError:
    stub_path = Path(__file__).with_name("aiosqlite_stub.py")
    spec = importlib.util.spec_from_file_location("aiosqlite", stub_path)
    if spec is None or spec.loader is None:
        raise
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules["aiosqlite"] = module

from app.backend.Base import Base
from app.backend.async_database import get_database
from app.models.Answer import Answer
from app.models.Question import Question
from main import app


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def session_factory(engine: AsyncEngine) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


@pytest.fixture(scope="function", autouse=True)
async def _override_db_dependency(session_factory: async_sessionmaker[AsyncSession]) -> AsyncGenerator[None, None]:
    async def _get_db() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_database] = _get_db
    yield
    app.dependency_overrides.pop(get_database, None)


@pytest.fixture(scope="function", autouse=True)
def patch_dependency_functions():
    from app.routers import dependencies as deps_module
    from app.routers import questions as questions_router
    from app.routers import answers as answers_router

    async def _get_question_by_id(
        question_id: int,
        database: AsyncSession,
    ) -> Question:
        result = await database.execute(
            select(Question).options(selectinload(Question.answers)).where(Question.id == question_id)
        )
        question = result.scalar_one_or_none()
        if question is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question with id {question_id} not found",
            )
        return question

    async def _get_answer_by_id(
        answer_id: int,
        database: AsyncSession,
    ) -> Answer:
        answer = await database.scalar(select(Answer).where(Answer.id == answer_id))
        if answer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Answer with id {answer_id} not found",
            )
        return answer

    deps_module.get_question_by_id = _get_question_by_id
    deps_module.get_answer_by_id = _get_answer_by_id
    questions_router.get_question_by_id = _get_question_by_id
    answers_router.get_answer_by_id = _get_answer_by_id

    yield

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

