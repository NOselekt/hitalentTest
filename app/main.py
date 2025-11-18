from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn

from app.routers.questions import router as questions_router
from app.routers.answers import router as answers_router


app = FastAPI()
app.include_router(questions_router)
app.include_router(answers_router)


@app.get("/")
async def main() -> RedirectResponse:
    """
    Responsible for the main page.
    """
    return RedirectResponse("/docs")


if __name__ == "__main__":
    uvicorn.run("app.main:app")
