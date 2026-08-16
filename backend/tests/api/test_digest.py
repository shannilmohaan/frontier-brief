import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.db.database import get_session
from app.main import app


def _make_session_override(mock_session):
    async def override() -> AsyncGenerator:
        yield mock_session
    return override


def _make_digest_item(domain_tags: list[str], score: float = 0.8) -> MagicMock:
    item = MagicMock()
    item.id = uuid.uuid4()
    item.narrative = "A test narrative about AI agents.\n\nSource: [Test](https://example.com)"
    item.source_name = "Test Source"
    item.source_url = "https://example.com"
    item.content_type = "article"
    item.domain_tags = domain_tags
    item.relevance_score = score
    item.created_at = datetime.now(timezone.utc)
    return item


def test_digest_latest_returns_empty_when_no_completed_cycle() -> None:
    mock_session = AsyncMock()
    mock_session.execute.return_value.scalar_one_or_none.return_value = None

    app.dependency_overrides[get_session] = _make_session_override(mock_session)
    try:
        client = TestClient(app)
        response = client.get("/api/digest/latest")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["cycle_id"] is None


def test_digest_latest_returns_items_from_completed_cycle() -> None:
    cycle_id = uuid.uuid4()
    mock_cycle = MagicMock()
    mock_cycle.id = cycle_id
    mock_cycle.status = "completed"

    item1 = _make_digest_item(["Agentic AI"])
    item2 = _make_digest_item(["AI Research"], score=0.5)

    mock_session = AsyncMock()
    cycle_exec = MagicMock()
    cycle_exec.scalar_one_or_none.return_value = mock_cycle

    items_exec = MagicMock()
    items_exec.scalars.return_value.all.return_value = [item1, item2]

    mock_session.execute.side_effect = [cycle_exec, items_exec]

    app.dependency_overrides[get_session] = _make_session_override(mock_session)
    try:
        client = TestClient(app)
        response = client.get("/api/digest/latest")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert body["cycle_id"] == str(cycle_id)
    assert body["domain_filter"] is None


def test_digest_latest_with_domain_filter() -> None:
    cycle_id = uuid.uuid4()
    mock_cycle = MagicMock()
    mock_cycle.id = cycle_id
    mock_cycle.status = "completed"

    agentic_item = _make_digest_item(["Agentic AI"])

    mock_session = AsyncMock()
    cycle_exec = MagicMock()
    cycle_exec.scalar_one_or_none.return_value = mock_cycle

    items_exec = MagicMock()
    items_exec.scalars.return_value.all.return_value = [agentic_item]

    mock_session.execute.side_effect = [cycle_exec, items_exec]

    app.dependency_overrides[get_session] = _make_session_override(mock_session)
    try:
        client = TestClient(app)
        response = client.get("/api/digest/latest?domain=Agentic+AI")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["domain_filter"] == "Agentic AI"
    assert len(body["items"]) == 1
    assert "Agentic AI" in body["items"][0]["domain_tags"]
