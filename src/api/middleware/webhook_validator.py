"""Webhook signature validation middleware.

Validates incoming webhook requests from Plane.so by verifying
the HMAC-SHA256 signature in the request headers against the
configured webhook secret.

Usage:
    from src.api.middleware.webhook_validator import validate_webhook_signature

    @router.post("/webhooks/plane")
    async def handle_webhook(request: Request):
        await validate_webhook_signature(request)
        ...
"""

import hashlib
import hmac

from fastapi import Request

from src.common.exceptions import WebhookValidationError
from src.common.logging import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)

# Header name where Plane.so sends the signature
SIGNATURE_HEADER = "X-Plane-Signature"

# Alternative header names (webhooks may vary)
ALTERNATIVE_HEADERS = [
    "X-Webhook-Signature",
    "X-Hub-Signature-256",
    "X-Signature",
]


async def validate_webhook_signature(request: Request) -> None:
    """Validate the webhook request signature.

    Reads the raw request body and computes HMAC-SHA256 against the
    configured webhook secret. Compares with the signature in headers.

    Args:
        request: The incoming FastAPI request.

    Raises:
        WebhookValidationError: If the signature is missing or invalid.
    """
    settings = get_settings()
    secret = settings.plane.webhook_secret

    # Skip validation if no secret is configured (development mode)
    if not secret:
        logger.warning("webhook_validation_skipped_no_secret_configured")
        return

    # Find the signature header
    signature = _get_signature_from_headers(request)

    if not signature:
        raise WebhookValidationError(
            reason="Missing webhook signature header"
        )

    # Read the raw body for signature computation
    body = await request.body()

    # Compute expected signature
    expected_signature = compute_signature(body, secret)

    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(signature, expected_signature):
        logger.warning(
            "webhook_signature_mismatch",
            received_prefix=signature[:10] + "...",
        )
        raise WebhookValidationError(
            reason="Invalid webhook signature"
        )

    logger.info("webhook_signature_validated")


def compute_signature(payload: bytes, secret: str) -> str:
    """Compute HMAC-SHA256 signature for a payload.

    Args:
        payload: The raw request body bytes.
        secret: The webhook secret key.

    Returns:
        Hex-encoded HMAC-SHA256 signature.
    """
    return hmac.HMAC(
        key=secret.encode("utf-8"),
        msg=payload,
        digestmod=hashlib.sha256,
    ).hexdigest()


def _get_signature_from_headers(request: Request) -> str | None:
    """Extract the signature from request headers.

    Checks the primary header and alternative header names.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The signature string, or None if not found.
    """
    # Check primary header
    signature = request.headers.get(SIGNATURE_HEADER)
    if signature:
        return _clean_signature(signature)

    # Check alternative headers
    for header in ALTERNATIVE_HEADERS:
        signature = request.headers.get(header)
        if signature:
            return _clean_signature(signature)

    return None


def _clean_signature(signature: str) -> str:
    """Clean a signature value, removing any algorithm prefix.

    Handles formats like "sha256=abc123..." or plain hex strings.

    Args:
        signature: Raw signature header value.

    Returns:
        Cleaned hex signature string.
    """
    # Remove algorithm prefix if present
    if "=" in signature and not signature.startswith("sha"):
        return signature

    prefixes = ["sha256=", "sha1=", "hmac-sha256="]
    for prefix in prefixes:
        if signature.lower().startswith(prefix):
            return signature[len(prefix):]

    return signature
