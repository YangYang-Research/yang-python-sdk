# Yang Python SDK

Build YangYang into your agents and apps. One Python package, typed clients per tool, shared API key — start with Open Guardrails and pick up more tools as they ship.

## Install

```bash
pip install yang-python-sdk
```

## Tools

| Tool | Import | Docs |
|------|--------|------|
| **Open Guardrails** | `from yang_python_sdk.open_guardrails import YogClient` | [docs/open-guardrails.md](docs/open-guardrails.md) |

## Setup

Create an API key in Yang Studio (`sk-yyng…`) and put it in `.env`:

```bash
YANG_API_KEY=sk-yyng…
```

## License

Apache License 2.0
