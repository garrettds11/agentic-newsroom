from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app


def override_settings(**kwargs):
    values = {
        "environment": "test",
        "dry_run": True,
        "search_provider": "placeholder",
        "storage_provider": "memory",
        "require_auth": False,
        "newsroom_api_key": "",
        "newsroom_default_max_sources": 25,
        "newsroom_system_max_sources": 250,
    }
    values.update(kwargs)
    return Settings(**values)


def test_research_request_schema_accepts_optional_service_fields() -> None:
    from app.schemas import ResearchRequest

    request = ResearchRequest(
        topic="local transit",
        source_provider="rss",
        source_ids=["local_feed"],
        max_sources=5,
        tags=["civic"],
        category="local",
        sort="published_desc",
        time_window="7d",
        output_format="json",
        page_size=25,
        cursor="cursor-placeholder",
    )

    assert request.topic == "local transit"
    assert request.source_ids == ["local_feed"]
    assert request.max_sources == 5
    assert request.sort == "published_desc"
    assert request.time_window == "7d"
    assert request.page_size == 25
    assert request.cursor == "cursor-placeholder"


def test_auth_disabled_allows_research_request() -> None:
    app.dependency_overrides[get_settings] = lambda: override_settings(require_auth=False)
    client = TestClient(app)

    response = client.post("/research", json={"topic": "local newsroom"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_omitted_max_sources_uses_default_limit_metadata() -> None:
    app.dependency_overrides[get_settings] = lambda: override_settings(
        newsroom_default_max_sources=25,
        newsroom_system_max_sources=250,
    )
    client = TestClient(app)

    response = client.post("/research", json={"topic": "local newsroom"})

    app.dependency_overrides.clear()
    metadata = response.json()["metadata"]
    assert response.status_code == 200
    assert metadata["requested_max_sources"] is None
    assert metadata["effective_max_sources"] == 25
    assert metadata["system_max_sources"] == 250
    assert metadata["capped"] is False
    assert metadata["result_count"] == 1


def test_max_sources_under_cap_is_honored_in_metadata() -> None:
    app.dependency_overrides[get_settings] = lambda: override_settings(
        newsroom_default_max_sources=25,
        newsroom_system_max_sources=250,
    )
    client = TestClient(app)

    response = client.post("/research", json={"topic": "local newsroom", "max_sources": 50})

    app.dependency_overrides.clear()
    metadata = response.json()["metadata"]
    assert response.status_code == 200
    assert metadata["requested_max_sources"] == 50
    assert metadata["effective_max_sources"] == 50
    assert metadata["capped"] is False
    assert metadata["result_count"] == 1


def test_max_sources_over_cap_is_capped_in_metadata() -> None:
    app.dependency_overrides[get_settings] = lambda: override_settings(
        newsroom_default_max_sources=25,
        newsroom_system_max_sources=250,
    )
    client = TestClient(app)

    response = client.post("/research", json={"topic": "local newsroom", "max_sources": 1000})

    app.dependency_overrides.clear()
    metadata = response.json()["metadata"]
    assert response.status_code == 200
    assert metadata["requested_max_sources"] == 1000
    assert metadata["effective_max_sources"] == 250
    assert metadata["system_max_sources"] == 250
    assert metadata["capped"] is True
    assert metadata["result_count"] == 1


def test_null_max_sources_uses_default_limit_metadata() -> None:
    app.dependency_overrides[get_settings] = lambda: override_settings(
        newsroom_default_max_sources=33,
        newsroom_system_max_sources=250,
    )
    client = TestClient(app)

    response = client.post("/research", json={"topic": "local newsroom", "max_sources": None})

    app.dependency_overrides.clear()
    metadata = response.json()["metadata"]
    assert response.status_code == 200
    assert metadata["requested_max_sources"] is None
    assert metadata["effective_max_sources"] == 33


def test_page_size_and_cursor_are_returned_with_null_next_cursor() -> None:
    app.dependency_overrides[get_settings] = lambda: override_settings()
    client = TestClient(app)

    response = client.post(
        "/research",
        json={"topic": "local newsroom", "page_size": 20, "cursor": "abc123"},
    )

    app.dependency_overrides.clear()
    metadata = response.json()["metadata"]
    assert response.status_code == 200
    assert metadata["page_size"] == 20
    assert metadata["cursor"] == "abc123"
    assert metadata["next_cursor"] is None


def test_auth_enabled_rejects_missing_key() -> None:
    app.dependency_overrides[get_settings] = lambda: override_settings(
        require_auth=True,
        newsroom_api_key="test-key",
    )
    client = TestClient(app)

    response = client.post("/research", json={"topic": "local newsroom"})

    app.dependency_overrides.clear()
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_auth_enabled_accepts_correct_header_key() -> None:
    app.dependency_overrides[get_settings] = lambda: override_settings(
        require_auth=True,
        newsroom_api_key="test-key",
    )
    client = TestClient(app)

    response = client.post(
        "/research",
        json={"topic": "local newsroom"},
        headers={"X-Newsroom-Api-Key": "test-key"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_auth_enabled_accepts_bearer_key() -> None:
    app.dependency_overrides[get_settings] = lambda: override_settings(
        require_auth=True,
        newsroom_api_key="test-key",
    )
    client = TestClient(app)

    response = client.post(
        "/research",
        json={"topic": "local newsroom"},
        headers={"Authorization": "Bearer test-key"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
