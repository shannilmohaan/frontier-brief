import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.db.database import AsyncSessionLocal, get_session
from app.main import app

VALID_KEY = "test-refresh-secret-key"
WRONG_KEY = "wrong-key"


def _make_session_override(mock_session):
    async def override() -> AsyncGenerator:
        yield mock_session
    return override


def test_refresh_wrong_key_returns_401() -> None:
    client = TestClient(app)
    response = client.post("/api/refresh", headers={"X-Refresh-Key": WRONG_KEY})
    assert response.status_code == 401


def test_refresh_missing_key_returns_401() -> None:
    client = TestClient(app)
    response = client.post("/api/refresh")
    assert response.status_code == 401


def test_refresh_valid_key_returns_202_with_job_id() -> None:
    job_id = uuid.uuid4()

    mock_session = AsyncMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = None
    mock_session.commit = AsyncMock()

    async def mock_refresh_side_effect(obj):
        obj.id = job_id
        obj.status = "pending"

    mock_session.refresh = AsyncMock(side_effect=mock_refresh_side_effect)

    app.dependency_overrides[get_session] = _make_session_override(mock_session)
    try:
        with patch("app.api.refresh.run_pipeline", new_callable=AsyncMock) as mock_pipeline:
            client = TestClient(app)
            response = client.post("/api/refresh", headers={"X-Refresh-Key": VALID_KEY})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    body = response.json()
    assert body["job_id"] == str(job_id)
    assert body["status"] == "pending"
    assert body["created"] is True
    mock_pipeline.assert_called_once_with(job_id, AsyncSessionLocal)


def test_refresh_returns_existing_job_when_already_running() -> None:
    existing_id = uuid.uuid4()
    mock_cycle = MagicMock()
    mock_cycle.id = existing_id
    mock_cycle.status = "running"

    mock_session = AsyncMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = mock_cycle

    app.dependency_overrides[get_session] = _make_session_override(mock_session)
    try:
        client = TestClient(app)
        response = client.post("/api/refresh", headers={"X-Refresh-Key": VALID_KEY})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "running"
    assert body["job_id"] == str(existing_id)
    assert body["created"] is False


def test_poll_unknown_job_id_returns_404() -> None:
    mock_session = AsyncMock()
    mock_session.get.return_value = None

    app.dependency_overrides[get_session] = _make_session_override(mock_session)
    try:
        client = TestClient(app)
        response = client.get(f"/api/refresh/{uuid.uuid4()}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404


def test_poll_known_job_id_returns_status() -> None:
    job_id = uuid.uuid4()
    mock_cycle = MagicMock()
    mock_cycle.id = job_id
    mock_cycle.status = "completed"

    mock_session = AsyncMock()
    mock_session.get.return_value = mock_cycle

    app.dependency_overrides[get_session] = _make_session_override(mock_session)
    try:
        client = TestClient(app)
        response = client.get(f"/api/refresh/{job_id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["job_id"] == str(job_id)
