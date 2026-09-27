from pathlib import Path

import yaml
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

import src.api.routes.config as cfg_routes
import src.utils.config as cfg_utils
from src.api.app import create_app


class _FakeRadarrService:
    def __init__(self, *_, **__):
        pass

    def test_connection(self) -> bool:
        return True


def _client(
    tmp_path: Path,
    monkeypatch,
    tmdb_api_key: str = "",
    region: str = "",
) -> TestClient:
    monkeypatch.setenv("BOXARR_DATA_DIRECTORY", str(tmp_path))
    monkeypatch.delenv("TMDB_API_KEY", raising=False)
    if tmdb_api_key:
        monkeypatch.setenv("TMDB_API_KEY", tmdb_api_key)
    if region:
        with (tmp_path / "local.yaml").open("w") as config_file:
            yaml.safe_dump(
                {"boxarr": {"features": {"box_office_region": region}}},
                config_file,
            )
    monkeypatch.setattr(cfg_routes, "RadarrService", _FakeRadarrService)
    monkeypatch.setattr(cfg_utils, "_settings", None)
    return TestClient(create_app())


def _payload(**values) -> dict:
    return {
        "radarr_url": "http://localhost:7878",
        "radarr_api_key": "test-key",
        "boxarr_scheduler_enabled": False,
        "boxarr_features_box_office_region": "IN",
        **values,
    }


def test_india_setup_shows_blank_password_field(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch, region="IN")

    response = client.get("/setup")
    soup = BeautifulSoup(response.text, "html.parser")
    field = soup.find(id="tmdbApiKey")
    group = soup.find(id="tmdbApiKeyGroup")

    assert response.status_code == 200
    assert field is not None
    assert field["type"] == "password"
    assert field["name"] == "tmdb_api_key"
    assert not field.has_attr("value")
    assert field.has_attr("required")
    assert not field.has_attr("disabled")
    assert group is not None
    assert not group.has_attr("hidden")


def test_tmdb_key_field_is_hidden_outside_india(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch, region="DE")

    response = client.get("/setup")
    soup = BeautifulSoup(response.text, "html.parser")

    assert soup.find(id="tmdbApiKeyGroup").has_attr("hidden")
    assert soup.find(id="tmdbApiKey").has_attr("disabled")


def test_api_key_is_saved_and_blank_submission_preserves_it(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)

    response = client.post(
        "/api/config/save", json=_payload(tmdb_api_key="entered-key")
    )
    assert response.json()["success"] is True
    with (tmp_path / "local.yaml").open() as config_file:
        saved_config = yaml.safe_load(config_file)
    assert saved_config["tmdb_api_key"] == "entered-key"

    response = client.post("/api/config/save", json=_payload(tmdb_api_key=""))
    assert response.json()["success"] is True
    with (tmp_path / "local.yaml").open() as config_file:
        saved_config = yaml.safe_load(config_file)
    assert saved_config["tmdb_api_key"] == "entered-key"


def test_india_selection_requires_a_key(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)

    response = client.post("/api/config/save", json=_payload())

    assert response.json() == {
        "success": False,
        "message": "TMDB API key is required when the Box Office Region is India.",
    }
    assert not (tmp_path / "local.yaml").exists()


def test_environment_key_is_not_rendered_or_persisted(tmp_path, monkeypatch):
    secret = "environment-secret"
    client = _client(tmp_path, monkeypatch, tmdb_api_key=secret, region="IN")

    page = client.get("/setup")
    field = BeautifulSoup(page.text, "html.parser").find(id="tmdbApiKey")
    assert secret not in page.text
    assert field is not None
    assert field.has_attr("disabled")

    response = client.post("/api/config/save", json=_payload())
    assert response.json()["success"] is True
    with (tmp_path / "local.yaml").open() as config_file:
        saved_config = yaml.safe_load(config_file)
    assert "tmdb_api_key" not in saved_config