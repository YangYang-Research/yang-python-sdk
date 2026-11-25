"""Agent-app hook: apply INPUT before agent, OUTPUT before showing reply."""

from __future__ import annotations

import os
import sys

from yang_open_guardrails import YogApiError, YogClient, YogTripwireTriggered


def main() -> int:
    profile_id = os.environ.get("YOG_PROFILE_ID", "").strip()
    version_id = os.environ.get("YOG_VERSION_ID", "").strip()
    if not profile_id or not version_id:
        print("Set YOG_PROFILE_ID and YOG_VERSION_ID (YANG_API_KEY in .env)", file=sys.stderr)
        return 1

    user_message = " ".join(sys.argv[1:]) or "Hello"

    with YogClient() as client:
        try:
            inbound = client.apply(
                profile_id=profile_id,
                version_id=version_id,
                source="INPUT",
                content=[{"text": {"text": user_message}}],
                raise_on_tripwire=True,
            )
        except YogTripwireTriggered as e:
            print("INPUT blocked:", e.result.get("outputs", [{}])[0].get("text"))
            return 2
        except YogApiError as e:
            print("API error:", e.message, file=sys.stderr)
            return 1

        # Your agent / LLM runs here — SDK does not call inference.
        assistant_reply = f"Echo: {inbound.get('outputs', [{}])[0].get('text', user_message)}"

        outbound = client.apply(
            profile_id=profile_id,
            version_id=version_id,
            source="OUTPUT",
            content=[{"text": {"text": assistant_reply}}],
        )
        if outbound.get("action") == "GUARDRAIL_INTERVENED":
            print(outbound.get("outputs", [{}])[0].get("text") or assistant_reply)
        else:
            print(assistant_reply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
