from __future__ import annotations

import httpx
import pytest
import respx

from yang_python_sdk.open_guardrails import YogApiError, YogClient, YogTripwireTriggered

BASE = "https://ai.yyng.icu"
PROFILE = "YOG-AbCdEfGhIjKl"
VERSION = "a1B2c3D4"
URL = f"{BASE}/yog/{PROFILE}/version/{VERSION}/apply"


def _ok_body(**overrides):
    body = {
        "requestId": "yog_test",
        "profile": {"id": PROFILE, "version": "1", "versionId": VERSION},
        "action": "NONE",
        "actionReason": "No action.",
        "outputs": [{"text": "hello"}],
        "assessments": [],
        "usage": {},
        "guardrailCoverage": {},
        "degraded": False,
        "warnings": [],
    }
    body.update(overrides)
    return body


@respx.mock
def test_apply_input_ok():
    route = respx.post(URL).mock(return_value=httpx.Response(200, json=_ok_body()))
    with YogClient(api_key="sk-yyng-test", base_url=BASE) as client:
        result = client.apply(
            profile_id=PROFILE,
            version_id=VERSION,
            source="INPUT",
            content=[{"text": {"text": "hello"}}],
        )
    assert result["action"] == "NONE"
    assert route.called
    sent = route.calls.last.request
    assert sent.headers["Authorization"] == "Bearer sk-yyng-test"
    assert sent.read()  # body present


@respx.mock
def test_apply_tripwire_blocked():
    respx.post(URL).mock(
        return_value=httpx.Response(
            200,
            json=_ok_body(
                action="GUARDRAIL_INTERVENED",
                actionReason="Guardrail blocked: contentPolicy:hate",
                outputs=[{"text": "I cannot help with that."}],
            ),
        )
    )
    with YogClient(api_key="sk-yyng-test", base_url=BASE) as client:
        with pytest.raises(YogTripwireTriggered) as ei:
            client.apply(
                profile_id=PROFILE,
                version_id=VERSION,
                source="INPUT",
                content=[{"text": {"text": "bad"}}],
                raise_on_tripwire=True,
            )
    assert ei.value.result["outputs"][0]["text"] == "I cannot help with that."


@respx.mock
def test_apply_anonymize_no_tripwire():
    respx.post(URL).mock(
        return_value=httpx.Response(
            200,
            json=_ok_body(
                action="GUARDRAIL_INTERVENED",
                actionReason="Guardrail intervened: sensitiveInformationPolicy",
                outputs=[{"text": "my email is ***"}],
            ),
        )
    )
    with YogClient(api_key="sk-yyng-test", base_url=BASE) as client:
        result = client.apply(
            profile_id=PROFILE,
            version_id=VERSION,
            source="OUTPUT",
            content=[{"text": {"text": "my email is a@b.com"}}],
            raise_on_tripwire=True,
        )
    assert result["action"] == "GUARDRAIL_INTERVENED"
    assert result["outputs"][0]["text"] == "my email is ***"


@respx.mock
def test_apply_http_error():
    respx.post(URL).mock(
        return_value=httpx.Response(
            403,
            json={"error": {"message": "No entitlement", "type": "invalid_request_error", "code": "entitlement_required"}},
        )
    )
    with YogClient(api_key="sk-yyng-test", base_url=BASE) as client:
        with pytest.raises(YogApiError) as ei:
            client.apply(
                profile_id=PROFILE,
                version_id=VERSION,
                source="INPUT",
                content=[{"text": {"text": "x"}}],
            )
    assert ei.value.status_code == 403
    assert ei.value.code == "entitlement_required"


def test_bad_version_id():
    with YogClient(api_key="sk-yyng-test") as client:
        with pytest.raises(ValueError, match="version_id"):
            client.apply(
                profile_id=PROFILE,
                version_id="short",
                source="INPUT",
                content=[{"text": {"text": "x"}}],
            )


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("YANG_API_KEY", raising=False)
    with pytest.raises(ValueError, match="YANG_API_KEY"):
        YogClient(env_file=False)
