from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from src.core.boxoffice import BoxOfficeService
from src.core.exceptions import BoxOfficeError
from src.core.tmdb import TMDBIndianReleaseService
from src.utils.config import Settings


def _response(payload):
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


def test_india_region_uses_tmdb_indian_origin_and_regional_release_dates(monkeypatch):
    client = MagicMock()
    client.get.side_effect = [
        _response(
            {
                "total_pages": 1,
                "results": [
                    {"id": 123, "title": "Indian Film", "original_title": "Indian Film"}
                ],
            }
        ),
        _response({"imdb_id": "tt1234567"}),
    ]
    monkeypatch.setattr(
        "src.core.boxoffice.settings",
        SimpleNamespace(
            boxarr_features_box_office_region="IN", tmdb_api_key="test-key"
        ),
    )

    movies = BoxOfficeService(http_client=client).fetch_weekend_box_office(2024, 48, 10)

    discover_args, discover_kwargs = client.get.call_args_list[0]
    discover_url = discover_args[0]
    assert discover_url == "https://api.themoviedb.org/3/discover/movie"
    assert discover_kwargs["params"] == {
        "with_origin_country": "IN",
        "region": "IN",
        "release_date.gte": "2024-11-26",
        "release_date.lte": "2024-12-01",
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "page": 1,
        "api_key": "test-key",
    }
    assert [(movie.rank, movie.title, movie.imdb_id) for movie in movies] == [
        (1, "Indian Film", "tt1234567")
    ]
    assert movies[0].weekend_gross is None


def test_non_india_region_keeps_box_office_mojo(monkeypatch):
    client = MagicMock()
    response = _response({})
    response.text = "<html><body><table></table></body></html>"
    client.get.return_value = response
    service = BoxOfficeService(http_client=client)
    monkeypatch.setattr(
        "src.core.boxoffice.settings",
        SimpleNamespace(boxarr_features_box_office_region="DE"),
    )
    monkeypatch.setattr(service, "parse_box_office_html", lambda html, limit: [])

    assert service.fetch_weekend_box_office(2024, 48) == []
    assert client.get.call_args.args[0].endswith("?area=DE")


def test_tmdb_service_requires_api_key():
    with pytest.raises(BoxOfficeError, match="TMDB_API_KEY"):
        TMDBIndianReleaseService(api_key="", http_client=MagicMock())


def test_tmdb_api_key_loads_from_environment(monkeypatch):
    monkeypatch.setenv("TMDB_API_KEY", "environment-key")

    assert Settings().tmdb_api_key == "environment-key"


def test_tmdb_service_returns_empty_for_nonpositive_limit():
    service = TMDBIndianReleaseService(api_key="test-key", http_client=MagicMock())

    assert service.fetch_weekend_releases(
        datetime(2024, 11, 29), datetime(2024, 12, 1), limit=0
    ) == []