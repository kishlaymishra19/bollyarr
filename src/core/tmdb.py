"""TMDB discovery for Indian movies with releases in India."""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

from ..utils.config import settings
from ..utils.logger import get_logger
from .boxoffice import BoxOfficeMovie
from .exceptions import BoxOfficeError

logger = get_logger(__name__)


class TMDBIndianReleaseService:
    """Fetch Indian-origin movies released in India during a target weekend.

    TMDB popularity is used for ordering because reliable weekly gross data is
    not available here. The existing BoxOfficeMovie shape keeps this source
    compatible with Bollyarr's matcher and scheduler.
    """

    BASE_URL = "https://api.themoviedb.org/3"
    MAX_FETCH_ATTEMPTS = 3
    RETRY_BACKOFF_SECONDS = (2, 4)
    PAGE_SIZE = 20

    def __init__(
        self,
        api_key: Optional[str] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self.api_key = api_key or getattr(settings, "tmdb_api_key", "") or ""
        if not self.api_key:
            raise BoxOfficeError(
                "TMDB API key is required when Box Office Region is India. "
                "Set the TMDB_API_KEY environment variable."
            )
        self.client = http_client or httpx.Client(
            timeout=getattr(settings, "boxoffice_timeout", 120.0),
            follow_redirects=True,
        )

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        request_params = {**params, "api_key": self.api_key}
        url = f"{self.BASE_URL}{path}"

        for attempt in range(1, self.MAX_FETCH_ATTEMPTS + 1):
            try:
                response = self.client.get(url, params=request_params)
                response.raise_for_status()
                try:
                    return response.json()
                except ValueError:
                    raise BoxOfficeError(
                        "TMDB returned an invalid JSON response."
                    ) from None
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                if status_code < 500 and status_code != 429:
                    raise BoxOfficeError(
                        f"TMDB request failed with HTTP {status_code}."
                    ) from None
                if attempt == self.MAX_FETCH_ATTEMPTS:
                    break
                logger.warning(
                    "TMDB request attempt %s/%s failed with HTTP %s; retrying",
                    attempt,
                    self.MAX_FETCH_ATTEMPTS,
                    status_code,
                )
            except (httpx.TimeoutException, httpx.TransportError) as e:
                if attempt == self.MAX_FETCH_ATTEMPTS:
                    break
                logger.warning(
                    "TMDB request attempt %s/%s failed with %s; retrying",
                    attempt,
                    self.MAX_FETCH_ATTEMPTS,
                    type(e).__name__,
                )

            time.sleep(self.RETRY_BACKOFF_SECONDS[attempt - 1])

        raise BoxOfficeError("Failed to fetch data from TMDB after 3 attempts.")

    def fetch_weekend_releases(
        self,
        friday: datetime,
        sunday: datetime,
        limit: int = 10,
    ) -> List[BoxOfficeMovie]:
        """Fetch Indian-origin releases around the specified weekend.

        The window starts three days before Friday to include Thursday releases
        and small regional date discrepancies in TMDB's records.
        """
        if limit <= 0:
            return []

        window_start = (friday - timedelta(days=3)).strftime("%Y-%m-%d")
        window_end = sunday.strftime("%Y-%m-%d")
        params: Dict[str, Any] = {
            "with_origin_country": "IN",
            "region": "IN",
            "release_date.gte": window_start,
            "release_date.lte": window_end,
            "sort_by": "popularity.desc",
            "include_adult": "false",
        }

        logger.info(
            "Fetching Indian releases from TMDB for %s..%s", window_start, window_end
        )
        results: List[Dict[str, Any]] = []
        page = 1
        total_pages = 1
        while len(results) < limit and page <= total_pages:
            data = self._get("/discover/movie", {**params, "page": page})
            results.extend(data.get("results", []))
            total_pages = data.get("total_pages", 1)
            page += 1

        movies: List[BoxOfficeMovie] = []
        for item in results[:limit]:
            title = item.get("title") or item.get("original_title") or ""
            tmdb_id = item.get("id")
            if not title:
                continue

            movie = BoxOfficeMovie(
                rank=len(movies) + 1,
                title=title,
                release_url=(
                    f"https://www.themoviedb.org/movie/{tmdb_id}"
                    if tmdb_id is not None
                    else None
                ),
            )
            if tmdb_id is not None:
                try:
                    external_ids = self._get(f"/movie/{tmdb_id}/external_ids", {})
                    movie.imdb_id = external_ids.get("imdb_id") or None
                except BoxOfficeError as e:
                    logger.debug(
                        "Could not fetch external IDs for TMDB movie %s: %s",
                        tmdb_id,
                        e,
                    )
            movies.append(movie)

        return movies