from fastapi import FastAPI
import uvicorn

from app.routers.questions import router as questions_router
from app.routers.answers import router as answers_router


app = FastAPI()
app.include_router(questions_router)
app.include_router(answers_router)


if __name__ == "__main__":
    uvicorn.run("main:app")
