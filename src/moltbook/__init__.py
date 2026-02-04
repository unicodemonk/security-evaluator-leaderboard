"""
Moltbook Integration Module

A reusable Python client for interacting with the Moltbook social network API.
Moltbook is a social network designed for AI agents to interact, share knowledge,
and build community.

Usage:
    from src.moltbook import MoltbookClient
    
    client = MoltbookClient(api_key="moltbook_xxx")
    client.create_post(
        submolt="aisecurity",
        title="Security Evaluation Results",
        content="..."
    )
"""

from .client import MoltbookClient
from .exceptions import (
    MoltbookError,
    MoltbookAuthError,
    MoltbookRateLimitError,
    MoltbookNotFoundError,
    MoltbookValidationError
)

__version__ = "1.0.0"
__all__ = [
    "MoltbookClient",
    "MoltbookError",
    "MoltbookAuthError",
    "MoltbookRateLimitError",
    "MoltbookNotFoundError",
    "MoltbookValidationError"
]
