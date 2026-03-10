# Task 05: Update existing tests and documentation — Implementation plan

## Overview

This task ensures that after the optional `flatten_records` implementation (tasks 01–04), the test suite passes, and user-facing and developer documentation reflect the new option. Default `flatten_records: false` changes default behaviour; any test that assumes flattened records or flattened schema must be updated (config or expectations). Documentation (README, config.sample.json, docstrings, AI_CONTEXT) must describe `flatten_records` so users and implementers can use it correctly.

**Scope:** Audit and fix existing tests; update README, config.sample.json, code docstrings, and AI_CONTEXT. No new test files or new test cases.

**Dependencies:** Tasks 01–04 complete (config property, sync/schema branches, discovery wiring).

---

## Files to Create/Modify

| File | Action | Change |
|------|--------|--------|
| `tests/test_streams.py` | Modify | Ensure `config()` supports tests that assume flattened behaviour. If the full suite fails with default `flatten_records: false`, add `flatten_records: true` to the base `config()` return value (e.g. in the `contents` dict) so all consumers get flattened behaviour; alternatively add it only in call sites that need it. |
| `tests/test_core.py` | Modify (if needed) | Uses `config()` from test_streams. If SDK standard tap tests fail (e.g. discovery or sync assertions), ensure the config passed to `get_tap_test_class` includes `flatten_records: true` (either via shared `config()` or via an override in this file). |
| `tests/test_tap.py` | Modify (if needed) | Uses `config()`; `test_schema_inference` asserts `stream0.schema == BASIC_SCHEMA`. With default false and flat sample data, inferred schema may still match BASIC_SCHEMA. If this test fails, add `flatten_records: true` to the config used in that test (or to shared `config()`) so inference matches current flattened behaviour. |
| `tests/test_404_end_of_stream.py` | Modify (if needed) | Expects `records == json_resp()["records"]` (raw records). With `flatten_records: false`, post_process returns row unchanged, so this test should pass. If it fails (e.g. due to shared config change), adjust config for this test only to use `flatten_records: false` and keep expectations as raw records. |
| `README.md` | Modify | In **Configuration → Accepted Config Options**: (1) Top-level: add `flatten_records` (optional, boolean, default false). One to two sentences: when true, records and inferred schema are flattened (current behaviour); when false, nested structure is preserved. (2) Stream-level: add the same under stream-level config options and note that stream overrides top-level. (3) In the Meltano `settings` YAML block (if present), add `- name: flatten_records` and `kind: boolean` in the appropriate place (e.g. after `store_raw_json_message`). |
| `config.sample.json` | Modify | Add top-level key `"flatten_records": false`. If the format allows (e.g. JSONC or project convention for comments), add a short comment; otherwise the key alone is sufficient. Optionally add inside one stream object as an example of stream-level override. |
| `tap_rest_api_msdk/tap.py` | Verify only | Confirm `get_schema(...)` docstring documents the `flatten_records` parameter per master documentation.md: "When True, flatten sample records before inference; when False, infer from nested records. Default False." If tasks 02/03 did not add it, add one line to the docstring. |
| `tap_rest_api_msdk/streams.py` | Verify only | Confirm `DynamicStream.__init__` docstring documents `flatten_records` (see documentation.md). Confirm `post_process` docstring states that when `flatten_records` is True it returns `flatten_json(...)`, otherwise returns row unchanged. If missing, add. |
| `docs/AI_CONTEXT/AI_CONTEXT_PATTERNS.md` | Modify | In the "No Pydantic/dataclasses" bullet: mention that flattening is conditional on `flatten_records` (when true, post_process flattens; when false, nested preserved). In Q&A "Where is stream schema defined or inferred?": mention that inference respects `flatten_records` (flatten samples then infer vs infer from nested). In Q&A "How is post-processing applied?": state that when `flatten_records` is true, post_process returns `flatten_json(...)`; when false, returns row unchanged. Keep edits minimal to stay under content-length. |
| `docs/AI_CONTEXT/AI_CONTEXT_tap_rest_api_msdk.md` | Modify | In get_schema description: add that behaviour depends on `flatten_records` (flatten then infer vs infer from nested). In DynamicStream post_process row: add that when `flatten_records` is true, result is `flatten_json(...)`; when false, row unchanged. In Discovery/Sync lifecycle bullets: mention `flatten_records` where schema inference and post_process are described. Keep under 500 lines. |
| `docs/AI_CONTEXT/AI_CONTEXT_QUICK_REFERENCE.md` | Modify (if applicable) | If config or tap behaviour is summarized there, add a one-line mention of `flatten_records` (optional, default false; when true, flatten records and schema). Only if space and relevance allow; otherwise skip to stay within content-length. |

No new files. No changes to test logic beyond config or expectations (no new assertions on call counts or logs).

---

## Test Strategy (TDD order)

This task does **not** add new tests. It fixes and documents.

1. **Run full suite first**  
   With tasks 01–04 complete, run `uv run pytest` and `uv run tox -e py`. Record which tests fail and why (e.g. assertion on flattened key, schema shape, or record shape).

2. **Fix failing tests only**  
   For each failing test:
   - **Option A:** Set `flatten_records: true` in the config used for that test (or in the shared `config()` in `test_streams.py` if most tests need flattened behaviour). Use when the test is intended to validate “current” (flattened) behaviour.
   - **Option B:** Keep `flatten_records: false` and change expectations to nested record/schema shape. Use when the test is intended to validate non-flattened behaviour.

3. **Prefer minimal, consistent change**  
   If the majority of existing tests assume flattened output (e.g. SDK standard tests, schema inference vs BASIC_SCHEMA), add `flatten_records: true` once to the shared `config()` in `tests/test_streams.py` so all callers get it. If only one or two tests fail, add `flatten_records: true` (or `false`) only in those tests’ config to keep default-false behaviour exercised elsewhere.

4. **No new test files or new cases**  
   Task 02/03 already added tests for sync and schema inference with true/false. This task only updates existing tests and documentation.

---

## Implementation Order

1. **Run suite and audit**  
   - Run `uv run pytest` and `uv run tox -e py`.  
   - For each failure, identify: (a) test file and name, (b) whether it assumes flattened records or flattened schema, (c) whether to fix by config (`flatten_records: true` or `false`) or by changing expected output.

2. **Adjust test config and expectations**  
   - Update `tests/test_streams.py` `config()` if a single shared default is chosen.  
   - Or update individual test files to pass a config that includes `flatten_records` as needed.  
   - Change assertions only where Option B (nested expectations) is chosen.  
   - Re-run the suite until all tests pass.

3. **README.md**  
   - Add `flatten_records` to top-level and stream-level configuration sections.  
   - Add to Meltano `settings` list if present.  
   - Keep to one to two sentences per level; state default false and that stream overrides top-level.

4. **config.sample.json**  
   - Add `"flatten_records": false` at top-level.  
   - Optionally add inside one stream object.  
   - Add a short comment only if the project supports comments in this file.

5. **Docstrings (tap.py, streams.py)**  
   - Verify `get_schema` and `DynamicStream.__init__` and `post_process` docstrings per master `documentation.md`.  
   - Add or adjust one-line parameter/behaviour text only if missing.

6. **AI_CONTEXT updates**  
   - Edit `AI_CONTEXT_PATTERNS.md`: conditional flattening and Q&A for schema/post_process.  
   - Edit `AI_CONTEXT_tap_rest_api_msdk.md`: get_schema and post_process behaviour and lifecycle.  
   - Optionally add one line in `AI_CONTEXT_QUICK_REFERENCE.md` if config is summarized there.  
   - Ensure each file remains under 500 lines (content_length rule).

7. **Final validation**  
   - Run `uv run pytest` and `uv run tox -e py` again.  
   - Confirm README and config.sample.json document the option and AI_CONTEXT is updated.

---

## Validation Steps

- [ ] `uv run pytest` passes with no regressions.  
- [ ] `uv run tox -e py` passes (pytest, ruff, mypy).  
- [ ] README.md documents `flatten_records` in configuration (top-level and stream-level) and in Meltano settings if applicable.  
- [ ] config.sample.json includes `"flatten_records": false` (and optionally stream-level example).  
- [ ] Docstrings in `tap.py` (`get_schema`) and `streams.py` (`DynamicStream.__init__`, `post_process`) describe `flatten_records` per documentation.md.  
- [ ] docs/AI_CONTEXT files that describe config, schema inference, or post_process mention `flatten_records`; all docs under 500 lines.

---

## Documentation Updates

| Document | Update |
|----------|--------|
| README.md | Configuration section: `flatten_records` (optional, boolean, default false). When true: flatten records and schema; when false: preserve nested structure. Stream overrides top-level. Meltano settings: add `flatten_records` boolean if listed. |
| config.sample.json | Top-level `"flatten_records": false`; optional stream-level example; optional short comment. |
| tap.py | get_schema docstring: document `flatten_records` parameter (when True flatten then infer, when False infer from nested; default False). |
| streams.py | DynamicStream.__init__ docstring: document `flatten_records`. post_process docstring: when True return flatten_json(...), when False return row unchanged. |
| docs/AI_CONTEXT/AI_CONTEXT_PATTERNS.md | Conditional flattening; Q&A for schema inference and post_process mention `flatten_records`. |
| docs/AI_CONTEXT/AI_CONTEXT_tap_rest_api_msdk.md | get_schema and post_process descriptions and lifecycle mention `flatten_records`. |
| docs/AI_CONTEXT/AI_CONTEXT_QUICK_REFERENCE.md | Optional one-line config mention if relevant and within length. |

All documentation must reflect the code (do not change code to match docs). Keep wording concise; respect content_length (500 lines per file).
