from __future__ import annotations

import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv

from .errors import YogApiError, YogTripwireTriggered
from .types import ApplyResult, ApplySource, ContentBlock, OutputScope

DEFAULT_BASE_URL = "https://ai.yyng.icu"
VERSION_ID_RE = re.compile(r"^[A-Za-z0-9]{8}$")


def _is_blocked(result: ApplyResult) -> bool:
    """Tripwire on hard block only (not anonymize / detect-only)."""
    if result.get("action") != "GUARDRAIL_INTERVENED":
        return False
    reason = str(result.get("actionReason") or "")
    return reason.startswith("Guardrail blocked")


class YogClient:
    """Thin client for YAIG `POST /yog/{profileId}/version/{versionId}/apply`."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
        env_file: str | None | bool = None,
    ) -> None:
        # env_file=False skips .env; None loads default .env from cwd; str = path
        if env_file is not False:
            load_dotenv(dotenv_path=None if env_file is None else str(env_file))
        key = (api_key or os.environ.get("YANG_API_KEY") or "").strip()
        if not key:
            raise ValueError("YANG_API_KEY is required (set it in .env or pass api_key)")
        self._api_key = key
        resolved_base = (base_url or os.environ.get("YANG_BASE_URL") or DEFAULT_BASE_URL).strip()
        self._base_url = resolved_base.rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout)

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> YogClient:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def apply(
        self,
        *,
        profile_id: str,
        version_id: str,
        source: ApplySource,
        content: list[ContentBlock],
        output_scope: OutputScope | None = None,
        grounding_source: str | None = None,
        query: str | None = None,
        raise_on_tripwire: bool = False,
    ) -> ApplyResult:
        profile_id = (profile_id or "").strip()
        version_id = (version_id or "").strip()
        if not profile_id:
            raise ValueError("profile_id is required")
        if not VERSION_ID_RE.match(version_id):
            raise ValueError("version_id must be 8 chars A-Za-z0-9")
        if source not in ("INPUT", "OUTPUT"):
            raise ValueError("source must be INPUT or OUTPUT")
        if not content:
            raise ValueError("content must be a non-empty list")

        body: dict[str, Any] = {"source": source, "content": content}
        if output_scope is not None:
            body["outputScope"] = output_scope
        if grounding_source is not None:
            body["groundingSource"] = grounding_source
        if query is not None:
            body["query"] = query

        url = f"{self._base_url}/yog/{profile_id}/version/{version_id}/apply"
        try:
            res = self._client.post(
                url,
                json=body,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        except httpx.HTTPError as e:
            raise YogApiError(f"Request failed: {e}") from e

        raw: Any
        try:
            raw = res.json()
        except ValueError:
            raw = {"error": {"message": res.text or "Non-JSON response"}}

        if res.status_code >= 400:
            err = raw.get("error") if isinstance(raw, dict) else None
            if isinstance(err, dict):
                message = str(err.get("message") or res.reason_phrase)
                code = err.get("code")
            else:
                message = str(raw) if raw else res.reason_phrase
                code = None
            raise YogApiError(
                message,
                status_code=res.status_code,
                code=str(code) if code is not None else None,
                body=raw,
            )

        if not isinstance(raw, dict):
            raise YogApiError("Invalid apply response", status_code=res.status_code, body=raw)

        result: ApplyResult = raw  # type: ignore[assignment]
        if raise_on_tripwire and _is_blocked(result):
            raise YogTripwireTriggered(result)
        return result
