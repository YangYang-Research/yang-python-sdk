from __future__ import annotations

from typing import Any

from .types import ApplyResult


class YogApiError(Exception):
    """HTTP / API error from YAIG apply."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.body = body


class YogTripwireTriggered(Exception):
    """Raised when apply intervenes with a block and raise_on_tripwire=True."""

    def __init__(self, result: ApplyResult) -> None:
        reason = str(result.get("actionReason") or "Guardrail intervened")
        super().__init__(reason)
        self.result = result
