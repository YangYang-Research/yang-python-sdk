# Yang Open Guardrails — Python SDK

Thin client for [Yang Open Guardrails](https://ai.yyng.icu). Use it from an **existing agent app** to check text before the agent runs (`source=INPUT`) and before you show a reply (`source=OUTPUT`).

This SDK does **not** call chat/completions or wrap OpenAI/Anthropic.

## Install

```bash
pip install yang-open-guardrails
```

Dev / local:

```bash
pip install -e ".[dev]"
```

## Auth

- API key: `YANG_API_KEY` or `YogClient(api_key="sk-yyng…")`
- Entitlement: `yang_open_guardrails`
- Profile: Studio-published `profileId` + `versionId` (8-char)

## Quickstart

```python
from yang_open_guardrails import YogClient, YogTripwireTriggered

client = YogClient(api_key="sk-yyng…")  # default base_url https://ai.yyng.icu

try:
    # Before your agent / LLM
    client.apply(
        profile_id="YOG-AbCdEfGhIjKl",
        version_id="a1B2c3D4",
        source="INPUT",
        content=[{"text": {"text": user_message}}],
        raise_on_tripwire=True,
    )
except YogTripwireTriggered as e:
    show(e.result["outputs"][0]["text"])
    return

reply = run_your_agent(user_message)  # your code

# Before showing the reply
out = client.apply(
    profile_id="YOG-AbCdEfGhIjKl",
    version_id="a1B2c3D4",
    source="OUTPUT",
    content=[{"text": {"text": reply}}],
)
if out["action"] == "GUARDRAIL_INTERVENED":
    reply = out["outputs"][0]["text"]
show(reply)
```

Optional body fields: `output_scope` (`INTERVENTIONS` | `FULL`), `grounding_source`, `query`.

`raise_on_tripwire=True` raises only on hard blocks (`actionReason` starts with `Guardrail blocked`). Anonymize returns `ApplyResult` for you to use `outputs`.

## Example

```bash
export YANG_API_KEY=sk-yyng…
export YOG_PROFILE_ID=YOG-…
export YOG_VERSION_ID=a1B2c3D4
python examples/hello_world.py "Hello"
```

## Publish (maintainers)

Auto-publish via GitHub Actions (`.github/workflows/publish.yml`) when a **GitHub Release** is published, or via **Actions → Publish PyPI → Run workflow**.

Secret: `PYPI_UPLOAD_PACKAGE` (PyPI API token). Package: `yang-open-guardrails`.

1. Bump `version` in `pyproject.toml` and `__init__.__version__`
2. Commit + push `main`
3. Create a GitHub Release (tag e.g. `v0.1.0`) → workflow uploads to PyPI

## License

MIT
