import logging
from typing import Any

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class WebhookDeliveryError(Exception):
    pass


class WebhookClient:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def send(self, url: str, payload: dict[str, Any]) -> None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(str(url), json=payload, timeout=5.0)
                response.raise_for_status()
                logger.info(f"Webhook successfully sent to {url}")
            except httpx.HTTPError as e:
                logger.error(f"Failed to send webhook to {url}: {e}")
                raise
