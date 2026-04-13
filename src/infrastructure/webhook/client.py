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
    """Raised when a webhook cannot be delivered."""


class WebhookClient:
    """HTTP client for webhook delivery."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def send(self, url: str, payload: dict[str, Any]) -> None:
        """Send a webhook payload.

        Args:
            url: Webhook destination URL.
            payload: JSON payload to send.
        """

        async with httpx.AsyncClient() as client:
            target = httpx.URL(url)
            try:
                logger.info("Sending webhook to host %s", target.host)
                response = await client.post(str(url), json=payload, timeout=5.0)
                response.raise_for_status()
                logger.info("Webhook successfully sent to host %s", target.host)
            except httpx.HTTPError as error:
                logger.error("Failed to send webhook to host %s: %s", target.host, error)
                raise
