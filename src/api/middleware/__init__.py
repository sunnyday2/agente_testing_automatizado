"""API middleware package.

Contains request processing middleware including webhook
signature validation.
"""

from src.api.middleware.webhook_validator import validate_webhook_signature

__all__ = ["validate_webhook_signature"]
