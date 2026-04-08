import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import create_app
from app.models import CheckResult, CheckStatus, City, SlotInfo


@pytest.fixture
def app():
    return create_app(start_checker=False)


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_get_status(client):
    resp = await client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "last_check" in data
    assert "is_monitoring" in data


@pytest.mark.asyncio
async def test_get_all_slots(client):
    resp = await client.get("/api/slots")
    assert resp.status_code == 200
    data = resp.json()
    assert "slots" in data
    assert isinstance(data["slots"], list)
    assert "status" in data


@pytest.mark.asyncio
async def test_get_slots_by_city_pinsk(client):
    resp = await client.get("/api/slots/Пинск")
    assert resp.status_code == 200
    data = resp.json()
    assert "slots" in data


@pytest.mark.asyncio
async def test_get_slots_by_city_baranovichi(client):
    resp = await client.get("/api/slots/Барановичи")
    assert resp.status_code == 200
    data = resp.json()
    assert "slots" in data


@pytest.mark.asyncio
async def test_get_slots_invalid_city(client):
    resp = await client.get("/api/slots/Минск")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_cors_headers(client):
    resp = await client.options(
        "/api/status",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code == 200
