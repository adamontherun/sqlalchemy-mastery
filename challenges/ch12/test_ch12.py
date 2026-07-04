import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from conftest import ASYNC_DB_URL


@pytest.fixture()
async def engine(subject):
    engine = create_async_engine(ASYNC_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(subject.Base.metadata.drop_all)
        await conn.run_sync(subject.Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(subject.Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture()
async def client(subject, engine):
    app = subject.build_app(engine)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_create_board(client):
    resp = await client.post("/boards", json={"name": "Launch"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Launch"
    assert body["cards"] == []
    assert isinstance(body["id"], int)


async def test_duplicate_board_is_409_and_rolls_back(client):
    assert (await client.post("/boards", json={"name": "Launch"})).status_code == 201
    assert (await client.post("/boards", json={"name": "Launch"})).status_code == 409
    # the failed request must not have poisoned anything: the app still works
    resp = await client.get("/boards")
    assert resp.status_code == 200
    assert [b["name"] for b in resp.json()] == ["Launch"]


async def test_create_card_and_404(client):
    board = (await client.post("/boards", json={"name": "Ops"})).json()
    resp = await client.post(f"/boards/{board['id']}/cards", json={"title": "Rotate keys"})
    assert resp.status_code == 201
    assert resp.json()["title"] == "Rotate keys"

    resp = await client.post("/boards/424242/cards", json={"title": "ghost"})
    assert resp.status_code == 404


async def test_list_boards_includes_cards(client):
    board = (await client.post("/boards", json={"name": "Zeta"})).json()
    await client.post(f"/boards/{board['id']}/cards", json={"title": "one"})
    await client.post(f"/boards/{board['id']}/cards", json={"title": "two"})
    await client.post("/boards", json={"name": "Alpha"})

    resp = await client.get("/boards")
    assert resp.status_code == 200
    boards = resp.json()
    assert [b["name"] for b in boards] == ["Alpha", "Zeta"]  # ordered by name
    assert {c["title"] for c in boards[1]["cards"]} == {"one", "two"}
