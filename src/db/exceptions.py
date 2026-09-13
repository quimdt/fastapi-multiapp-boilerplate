class BaseAppError(Exception):
    """Base exception for all application errors."""


class BadCredentials(BaseAppError):
    """Raised when authentication fails."""


class NotFound(BaseAppError):
    """Raised when a requested resource does not exist."""


class DBError(BaseAppError):
    """Raised when a database operation fails."""
