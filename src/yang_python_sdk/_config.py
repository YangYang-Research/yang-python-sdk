from __future__ import annotations

import os

from dotenv import load_dotenv

DEFAULT_BASE_URL = "https://ai.yyng.icu"


def resolve_credentials(
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    env_file: str | None | bool = None,
) -> tuple[str, str]:
    """Load `.env` (unless env_file=False) and return (api_key, base_url)."""
    if env_file is not False:
        load_dotenv(dotenv_path=None if env_file is None else str(env_file))
    key = (api_key or os.environ.get("YANG_API_KEY") or "").strip()
    if not key:
        raise ValueError("YANG_API_KEY is required (set it in .env or pass api_key)")
    resolved = (base_url or os.environ.get("YANG_BASE_URL") or DEFAULT_BASE_URL).strip()
    return key, resolved.rstrip("/")
