# Quick Reference — tap-rest-api-msdk

**Metadata**

| Field | Value |
|-------|--------|
| Version | 1.0 |
| Last Updated | 2025-03-10 |
| Tags | quick-reference, tap, singer, meltano-sdk, rest-api |
| Cross-References | AI_CONTEXT_REPOSITORY.md (architecture), AI_CONTEXT_PATTERNS.md (patterns) |

---

## Project Summary

`tap-rest-api-msdk` is a Singer tap for generic REST APIs built with the Meltano SDK. It auto-discovers stream schemas from API responses and supports multiple auth methods (Basic, API Key, Bearer, OAuth, AWS). Main components: **tap** (CLI/entry), **streams** (DynamicStream), **client** (RestApiStream), **auth**, **pagination**, **utils**.

---

## Environment & Versions

- **Runtime:** Python 3.12+
- **Package manager:** `uv` (venv + sync)
- **Config:** `pyproject.toml` — scripts, deps, ruff, mypy, pytest
- **Venv:** `.venv` (create with `uv venv --python 3.12`; activate before commands)

---

## Key Commands (Shell)

| Action | Command |
|--------|---------|
| Full install (venv + deps + tests) | `./install.sh` |
| Activate venv | `source .venv/bin/activate` |
| Install deps (with dev) | `uv sync --extra dev` |
| Run tests | `uv run pytest` |
| Lint + typecheck + tests | `uv run tox -e py` |
| Tap version | `uv run tap-rest-api-msdk --version` |
| Tap help | `uv run tap-rest-api-msdk --help` |
| About (settings/capabilities) | `uv run tap-rest-api-msdk --about` |
| Discover (write catalog) | `uv run tap-rest-api-msdk --config CONFIG --discover > ./catalog.json` |
| Run tap (with config) | `uv run tap-rest-api-msdk --config CONFIG --catalog CATALOG` |

Quality gate before merge: `uv run tox -e py` must pass (pytest, ruff, mypy).

---

## Runtime Entry Points

- **CLI:** `tap-rest-api-msdk` → `tap_rest_api_msdk.tap:TapRestApiMsdk.cli` (Singer tap entry).
- **Meltano:** executable `tap-rest-api-msdk`; e.g. `meltano invoke tap-rest-api-msdk --version`, `meltano elt tap-rest-api-msdk target-jsonl`.

---

## Core Interfaces (Quick View)

- **Tap:** `TapRestApiMsdk` in `tap_rest_api_msdk.tap` — Singer tap; streams built from config.
- **Streams:** `DynamicStream` in `tap_rest_api_msdk.streams` — per-stream sync; uses `RestApiStream`, pagination, auth.
- **Client:** `RestApiStream` in `tap_rest_api_msdk.client` — HTTP requests and response handling.
- **Auth:** `get_authenticator` in `tap_rest_api_msdk.auth` — returns auth implementation from config (Basic, API Key, Bearer, OAuth, AWS).

---

## Frequently Used Imports

```python
from tap_rest_api_msdk.tap import TapRestApiMsdk

# Streams and client
from tap_rest_api_msdk.streams import DynamicStream
from tap_rest_api_msdk.client import RestApiStream

# Auth and utilities
from tap_rest_api_msdk.auth import get_authenticator
from tap_rest_api_msdk.utils import flatten_json, get_start_date
```

---

## Quick Troubleshooting

| Symptom | Check / Action |
|--------|-----------------|
| Command not found | Ensure venv is active: `source .venv/bin/activate`; use `uv run tap-rest-api-msdk` if needed. |
| Import errors | Run `uv sync --extra dev` from project root. |
| Tests fail | Run `uv run pytest`; fix regressions before considering task complete (see project TDD/regression rules). |
| Lint/type errors | Run `uv run tox -e py`; fix ruff/mypy in changed files. |
| Tap fails on discover/sync | Validate `--config` (e.g. `api_url`, `streams` with `name`, `path`, `primary_keys`); run `tap-rest-api-msdk --about` for settings. |
| Auth failures | Confirm `auth_method` and required fields (e.g. `api_key`, `username`/`password`, `bearer_token`, OAuth params) in config. |
