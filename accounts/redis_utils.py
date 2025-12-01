import redis
from django.conf import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

BLACKLIST_PREFIX = 'token_blacklist:'


def blacklist_token(token):
    """Add a token to the blacklist with TTL of 2 days."""
    key = f"{BLACKLIST_PREFIX}{token}"
    redis_client.setex(key, settings.TOKEN_BLACKLIST_TTL, "1")


def is_token_blacklisted(token):
    """Check if a token is blacklisted."""
    key = f"{BLACKLIST_PREFIX}{token}"
    return redis_client.exists(key)
