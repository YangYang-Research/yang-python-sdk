# Yang Python SDK

Official Python SDK for YangYang. Typed clients for Studio products — one package, shared credentials, import the tool you need.

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
