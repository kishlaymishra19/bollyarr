"""Core business logic for Bollyarr."""

from .boxoffice import BoxOfficeMovie, BoxOfficeService
from .exceptions import (
    BoxarrException,
    BollyarrException,
    BoxOfficeError,
    ConfigurationError,
    MovieMatchingError,
    RadarrAuthenticationError,
    RadarrConnectionError,
    RadarrError,
    RadarrNotFoundError,
    SchedulerError,
)
from .matcher import MatchResult, MovieMatcher
from .radarr import MovieStatus, QualityProfile, RadarrMovie, RadarrService
from .scheduler import BollyarrScheduler, BoxarrScheduler

__all__ = [
    # Services
    "BoxOfficeService",
    "RadarrService",
    "MovieMatcher",
    "BollyarrScheduler",
    "BoxarrScheduler",
    # Data classes
    "BoxOfficeMovie",
    "RadarrMovie",
    "QualityProfile",
    "MovieStatus",
    "MatchResult",
    # Exceptions
    "BollyarrException",
    "BoxarrException",
    "ConfigurationError",
    "BoxOfficeError",
    "RadarrError",
    "RadarrConnectionError",
    "RadarrAuthenticationError",
    "RadarrNotFoundError",
    "MovieMatchingError",
    "SchedulerError",
]
