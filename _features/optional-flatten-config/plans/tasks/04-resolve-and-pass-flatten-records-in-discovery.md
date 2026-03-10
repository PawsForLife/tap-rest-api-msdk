# Task 04: Resolve and pass flatten_records in discovery — Implementation plan

## Overview

This task wires the `flatten_records` config from discovery into schema inference and stream behaviour. In `discover_streams()` we resolve `flatten_records` per stream (stream overrides top-level, same pattern as `store_raw_json_message`), then pass the resolved value into `get_schema()` and `DynamicStream()`. No new behaviour is implemented here; tasks 02 and 03 already add the `get_schema(..., flatten_records)` parameter and the `DynamicStream(..., flatten_records)` parameter plus `post_process` branch. This task only performs the resolution and argument passing in `tap.py`.

**Scope:** `tap_rest_api_msdk/tap.py` — `discover_streams()` only.

**Dependencies:** Tasks 01 (config property), 02 (DynamicStream param and post_process branch), 03 (get_schema param and inference branch) must be complete so that `get_schema` and `DynamicStream` accept `flatten_records`.

**Acceptance:** Top-level `flatten_records: false` with no stream override yields nested records and nested schema for that stream; top-level `true` yields flattened. A stream-level `flatten_records` overrides the top-level value for that stream.

---

## Files to Create/Modify

| File | Action | Changes |
|------|--------|--------|
| `tap_rest_api_msdk/tap.py` | Modify | In `discover_streams()`: (1) resolve `flatten_records` with other stream config; (2) pass `flatten_records=flatten_records` to `self.get_schema(...)` in the inference branch; (3) pass `flatten_records=flatten_records` to `DynamicStream(...)` (e.g. after `store_raw_json_message`). |
| `tests/test_tap.py` or `tests/test_streams.py` | Modify | Add black-box tests for stream override: top-level false + one stream true; top-level true + one stream false. Assert on emitted record shape and schema structure only. |

No new files. No changes to `streams.py` or `utils.py` in this task.

---

## Test Strategy (TDD order)

Tests must be written first so they fail before implementation, then pass after the three changes in `discover_streams()`.

1. **Stream override — top-level false, stream true**
   - **What:** Config has top-level `flatten_records: false` and one stream with `flatten_records: true`. Other streams (if any) have no stream-level override.
   - **Assert:** The stream with override emits flattened records (e.g. flat keys like `user_id`) and has a flattened inferred schema; other streams emit nested records and nested schema.
   - **Why:** Ensures stream-level `true` overrides top-level `false` for discovery, get_schema, and sync.

2. **Stream override — top-level true, stream false**
   - **What:** Config has top-level `flatten_records: true` and one stream with `flatten_records: false`.
   - **Assert:** That stream emits nested records (e.g. `record["user"]["id"]`) and has nested schema; other streams remain flattened.
   - **Why:** Ensures stream-level `false` overrides top-level `true`.

**Location:** Prefer `tests/test_streams.py` to reuse `config()`, `setup_api`, `requests_mock`, and the pattern of building tap → `discover_streams()` → `stream.get_records({})` and asserting on record list and stream schema. If discovery/schema assertions are better placed in `tests/test_tap.py` (e.g. `discover_streams()` then assert on stream’s `schema` property), add the schema part there and sync/record assertions in `test_streams.py`, or keep both in one file for clarity.

**Black-box:** Assert only on observable outcomes: record keys/structure (nested vs flat) and schema `properties` shape (nested vs flat). Do not assert on call counts, log lines, or internal function calls.

**Data:** Use a small nested payload (e.g. `{"user": {"id": 1, "name": "x"}}`) so that flattened vs nested shape is unambiguous.

---

## Implementation Order

1. **Add tests** (TDD)
   - Add the two stream-override tests above. Use `requests_mock` to stub the API; build config with the appropriate top-level and stream-level `flatten_records`; get the stream(s) via `tap.discover_streams()`; for override stream call `list(stream.get_records({}))` and assert record shape; assert stream `schema` has the expected structure (nested vs flat properties).
   - Run the new tests and confirm they fail (e.g. missing keyword argument or wrong behaviour until discovery passes `flatten_records`).

2. **Resolve `flatten_records` in `discover_streams()`**
   - In `tap_rest_api_msdk/tap.py`, inside the `for stream in self.config["streams"]:` loop, add resolution immediately after the existing `offset_records_jsonpath = stream.get(...)` block and before `schema = {}`:
     - `flatten_records = stream.get("flatten_records", self.config.get("flatten_records", False))`

3. **Pass `flatten_records` into `get_schema()`**
   - In the `else` branch where schema is inferred (the block that calls `self.get_schema(records_path, except_keys, ...)`), add the keyword argument:
     - `flatten_records=flatten_records`
   - Ensure it is the last or an explicitly named argument in the call.

4. **Pass `flatten_records` into `DynamicStream()`**
   - In the `streams.append(DynamicStream(...))` call, add the argument:
     - `flatten_records=flatten_records`
   - Place it after `store_raw_json_message=...` for consistency with the existing pattern.

5. **Run tests and fix**
   - Run the new tests; they should pass. Run the full test suite (`uv run pytest`, and `uv run tox -e py` if applicable); fix any regressions (e.g. tests that assume flattening but do not set `flatten_records: true` in config — those are updated in task 05, but if something fails here, note it).

---

## Validation Steps

- [ ] Two new stream-override tests exist and are clearly named (e.g. `test_flatten_records_stream_override_top_level_false_stream_true`, `test_flatten_records_stream_override_top_level_true_stream_false` or similar).
- [ ] New tests fail before adding the three discovery changes and pass after.
- [ ] `discover_streams()` resolves `flatten_records` per stream with `stream.get("flatten_records", self.config.get("flatten_records", False))`.
- [ ] The inference branch calls `self.get_schema(..., flatten_records=flatten_records)`.
- [ ] `DynamicStream(..., flatten_records=flatten_records)` is passed in the discovery loop.
- [ ] Full test suite passes (no regressions; any tests that still assume global flattening are out of scope for this task and handled in task 05).

---

## Documentation Updates

- **In-repo:** No new docs required. If a feature doc or AI context describes discovery flow, add a single line that `flatten_records` is resolved per stream (stream overrides top-level) and passed to `get_schema()` and `DynamicStream()`; otherwise skip.
- **Code:** Ensure the resolution line is clear (e.g. one-line comment: “Stream overrides top-level for flatten_records.”) if the project style allows; otherwise the pattern matches `store_raw_json_message` and is self-explanatory.
