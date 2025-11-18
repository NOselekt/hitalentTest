import uuid

import pytest


async def create_question(client, text="What is FastAPI?"):
    response = await client.post("/questions/", json={"text": text})
    assert response.status_code == 201
    return response.json()


async def create_answer(client, question_id, text="Because.", user_id=None):
    payload = {
        "text": text,
        "user_id": str(user_id or uuid.uuid4()),
    }
    response = await client.post(f"/questions/{question_id}/answers/", json=payload)
    assert response.status_code == 201
    return response.json()


@pytest.mark.anyio
async def test_create_question_success(client):
    payload = {"text": "Explain dependency injection?"}
    response = await client.post("/questions/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["text"] == payload["text"]
    assert "id" in data


@pytest.mark.anyio
async def test_create_question_duplicate_text_rejected(client):
    text = "Unique question?"
    await create_question(client, text=text)

    response = await client.post("/questions/", json={"text": text})
    assert response.status_code == 400
    assert response.json()["detail"] == "Question with this text already exists"


@pytest.mark.anyio
async def test_get_questions_returns_created_items(client):
    await create_question(client, "Question A?")
    await create_question(client, "Question B?")

    response = await client.get("/questions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {item["text"] for item in data} == {"Question A?", "Question B?"}


@pytest.mark.anyio
async def test_get_question_includes_answers(client):
    question = await create_question(client, "What is caching?")
    await create_answer(client, question_id=question["id"], text="Stores data")

    response = await client.get(f"/questions/{question['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == question["id"]
    assert len(data["answers"]) == 1
    assert data["answers"][0]["text"] == "Stores data"


@pytest.mark.anyio
async def test_delete_question_removes_it(client):
    question = await create_question(client, "Delete me?")
    await create_answer(client, question_id=question["id"])

    delete_response = await client.delete(f"/questions/{question['id']}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/questions/{question['id']}")
    assert get_response.status_code == 404


@pytest.mark.anyio
async def test_create_answer_requires_existing_question(client):
    non_existing_id = 999
    payload = {"text": "Nope", "user_id": str(uuid.uuid4())}
    response = await client.post(f"/questions/{non_existing_id}/answers/", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == f"Question with id {non_existing_id} not found"


@pytest.mark.anyio
async def test_answer_endpoints(client):
    question = await create_question(client, "Answer me?")
    answer = await create_answer(client, question_id=question["id"], text="Sure")

    get_response = await client.get(f"/answers/{answer['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["text"] == "Sure"

    delete_response = await client.delete(f"/answers/{answer['id']}")
    assert delete_response.status_code == 204

    get_after_delete = await client.get(f"/answers/{answer['id']}")
    assert get_after_delete.status_code == 404

