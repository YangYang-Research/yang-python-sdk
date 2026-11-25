# Yang Python SDK

Official Python SDK for YangYang products. Use it from your apps and agents to call Yang APIs with a small, typed client.

## Install

```bash
pip install yang-python-sdk
```

## Tools

| Tool | Import | Docs |
|------|--------|------|
| **Open Guardrails** | `from yang_python_sdk.open_guardrails import YogClient` | [docs/open-guardrails.md](docs/open-guardrails.md) |

New tools land as sibling packages under `yang_python_sdk/<tool>/` — shared key/base URL stay in one place.

## Setup

Create an API key in Yang Studio (`sk-yyng…`) and put it in `.env`:

```bash
YANG_API_KEY=sk-yyng…
```

## License

Apache License 2.0
