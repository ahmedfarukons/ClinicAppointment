"""
Rate limiting middleware using SlowAPI.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

# Use client IP as the key; can be swapped for user-id-based keying later.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit],
    storage_uri="memory://",
)
