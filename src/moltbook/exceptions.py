"""
Custom exceptions for Moltbook API interactions.
"""


class MoltbookError(Exception):
    """Base exception for all Moltbook-related errors."""
    pass


class MoltbookAuthError(MoltbookError):
    """Raised when authentication fails or API key is invalid."""
    pass


class MoltbookRateLimitError(MoltbookError):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message, retry_after_minutes=None, retry_after_seconds=None, daily_remaining=None):
        super().__init__(message)
        self.retry_after_minutes = retry_after_minutes
        self.retry_after_seconds = retry_after_seconds
        self.daily_remaining = daily_remaining


class MoltbookNotFoundError(MoltbookError):
    """Raised when a requested resource is not found."""
    pass


class MoltbookValidationError(MoltbookError):
    """Raised when request validation fails."""
    pass
