import uuid
from datetime import datetime, timezone

from uuid_utils import uuid7


def uuid_v7() -> uuid.UUID:
    return uuid.UUID(hex=uuid7().hex)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
