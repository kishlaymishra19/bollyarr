"""Custom exceptions for Bollyarr."""


class BollyarrException(Exception):
    """Base exception for all Bollyarr errors."""

    pass


# Preserve imports from integrations using the original exception name.
BoxarrException = BollyarrException


class ConfigurationError(BollyarrException):
    """Raised when configuration is invalid or missing."""

    pass


class BoxOfficeError(BollyarrException):
    """Raised when box office data cannot be fetched."""

    pass


class RadarrError(BollyarrException):
    """Base exception for Radarr-related errors."""

    pass


class RadarrConnectionError(RadarrError):
    """Raised when connection to Radarr fails."""

    pass


class RadarrAuthenticationError(RadarrError):
    """Raised when Radarr authentication fails."""

    pass


class RadarrNotFoundError(RadarrError):
    """Raised when a resource is not found in Radarr."""

    pass


class MovieMatchingError(BollyarrException):
    """Raised when movie matching fails."""

    pass


class SchedulerError(BollyarrException):
    """Raised when scheduler operations fail."""

    pass
