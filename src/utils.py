import uuid
from datetime import datetime, timezone

from uuid_utils import uuid7


def uuid_v7() -> uuid.UUID:
    """Generate a UUIDv7 value."""

    return uuid.UUID(hex=uuid7().hex)


def utc_now() -> datetime:
    """Return the current UTC datetime."""

    return datetime.now(timezone.utc)
