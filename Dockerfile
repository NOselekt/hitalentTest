FROM python:3.12-slim AS base


WORKDIR ./


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install --upgrade pip wheel "poetry==2.1.3"
RUN poetry config virtualenvs.create false

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY poetry.lock pyproject.toml alembic.ini ./
ADD migrations ./migrations
ADD app ./app

RUN poetry install --no-root



EXPOSE 8000


RUN chmod +x app/prestart.sh

ENTRYPOINT ["./app/prestart.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

