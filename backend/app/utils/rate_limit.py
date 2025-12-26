"""
Rate limiting middleware for API endpoints.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
import os
import logging

from ..config import get_settings

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# If running tests, disable the limiter to avoid 429s during test runs.
TESTING = os.getenv("TESTING", "false").lower() == "true"
if TESTING:
    # slowapi Limiter supports an `enabled` attribute; set it False during tests.
    # If the attribute doesn't exist, AttributeError is caught and we keep limiter enabled.
    try:
        limiter.enabled = False
    except AttributeError:
        # The enabled attribute doesn't exist on this version of slowapi
        logging.warning(
            "Could not disable rate limiter for tests - enabled attribute not available"
        )
else:
    # In non-test environments, check if rate limiting is enabled via config
    try:
        settings = get_settings()
        if not settings.rate_limit_enabled:
            limiter.enabled = False
    except (ImportError, ValueError) as e:
        # If config loading fails, keep limiter enabled as a safe default
        logging.warning(
            f"Could not load rate limit config, keeping limiter enabled: {e}"
        )

# Rate limit configurations
RATE_LIMITS = {
    "auth_register": "5/hour",  # 5 registrations per hour per IP
    "auth_login": "10/minute",  # 10 login attempts per minute per IP
    "auth_refresh": "20/hour",  # 20 token refreshes per hour
    "admin_write": "100/hour",  # 100 write operations per hour for admin
    "admin_read": "1000/hour",  # 1000 read operations per hour for admin
}


def get_rate_limit(operation: str) -> str:
    """Get rate limit for a specific operation."""
    return RATE_LIMITS.get(operation, "100/minute")  # Default rate limit
