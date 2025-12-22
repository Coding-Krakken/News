"""
Rate limiting middleware for API endpoints.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

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
