# Task 02: Sync tests and post_process branch — Implementation plan

## Overview

This task implements the **DynamicStream** side of optional flatten: add a `flatten_records` constructor parameter and attribute, and branch in `post_process()` so that when `flatten_records` is true the stream flattens records (current behaviour), and when false it returns each row unchanged (nested). Discovery does not yet pass `flatten_records` (task 04); tests therefore obtain a stream via `discover_streams()` and set `stream.flatten_records` explicitly to verify post_process behaviour. No tap or discovery changes in this task.

**Scope:** `tap_rest_api_msdk/streams.py` only. Task 01 (config property) is done; task 04 (discovery pass-through) is not.

## Files to create/modify

| File | Action |
|------|--------|
| `tap_rest_api_msdk/streams.py` | **Modify**: Add `flatten_records` parameter to `DynamicStream.__init__` and set `self.flatten_records`; branch in `post_process()`; update docstrings for `__init__` and `post_process`. |
| `tests/test_streams.py` | **Modify**: Add two tests that assert sync output shape (flattened vs nested) by setting `stream.flatten_records` and calling `get_records()`. |

No new files.

## Test strategy (TDD order)

1. **Write tests first** (red), then implement until green. Per master testing.md and development_practices: black-box only; assert on emitted record structure, not call counts or logs.

2. **Test data**: Use a nested payload so that flattening is observable (e.g. `{"user": {"name": "a", "id": 1}}`). Flattened form has keys like `user_name`, `user_id`; nested form has `record["user"]["name"]`, `record["user"]["id"]`. Reuse or extend `json_resp()` / `setup_api()` so the mocked GET returns one or more records with nested objects.

3. **Test 1 — `flatten_records` true → flattened records**
   - **What:** Sync (get_records) returns records with flattened keys when the stream has `flatten_records=True`.
   - **Why:** Ensures post_process applies `flatten_json` when the flag is true; acceptance that current flatten behaviour is preserved.
   - **How:** Build tap with `config()`; mock API with `setup_api(requests_mock, ..., json_extras=...)` so response body contains nested records (e.g. `records: [{"user": {"name": "a", "id": 1}}]`). Call `tap.discover_streams()[0]`, set `stream.flatten_records = True`, then `list(stream.get_records({}))`. Assert the first record has flattened keys (e.g. `"user_name"`, `"user_id"`) and does not have a nested `"user"` key.
   - **Location:** `tests/test_streams.py`. Add a short docstring explaining what and why.

4. **Test 2 — `flatten_records` false → nested records**
   - **What:** Sync returns records with nested structure when the stream has `flatten_records=False`.
   - **Why:** Ensures post_process returns row unchanged when the flag is false; acceptance for no-flatten path.
   - **How:** Same setup as Test 1. Get stream, set `stream.flatten_records = False`, call `get_records`, collect records. Assert the first record has nested structure (e.g. `record["user"]["name"]`, `record["user"]["id"]` present) and that flattened keys like `user_name` are not present.
   - **Location:** `tests/test_streams.py`. Docstring as above.

5. **Run new tests:** They must fail before implementation (post_process always flattens today). After implementation they must pass.

6. **No assertions on:** `flatten_json` call count, log messages, or internal methods. Only on the shape of returned records.

## Implementation order

1. **Add nested response helper or payload in `tests/test_streams.py`**
   - Define a small nested record (e.g. `{"user": {"name": "a", "id": 1}}`) and a response that includes it under the existing `records_path` (e.g. `$.records[*]`). Use it in both new tests via `json_resp(...)` or a dedicated dict so the same GET mock serves both discovery and get_records.

2. **Add test_sync_returns_flattened_records_when_flatten_records_true**
   - Use `config()`, `setup_api(requests_mock, ...)` with nested payload, get stream from `TapRestApiMsdk(config=..., parse_env_config=True).discover_streams()[0]`, set `stream.flatten_records = True`, run `list(stream.get_records({}))`, assert flattened keys present and no top-level `"user"` dict.

3. **Add test_sync_returns_nested_records_when_flatten_records_false**
   - Same setup; set `stream.flatten_records = False`, run `get_records`, assert nested `record["user"]["name"]` and `record["user"]["id"]`, and no `user_name` / `user_id` at top level.

4. **Run pytest for the two new tests** — expect failures (post_process always flattens).

5. **Add parameter and attribute in `tap_rest_api_msdk/streams.py`**
   - In `DynamicStream.__init__`, add parameter `flatten_records: Optional[bool] = False` after `store_raw_json_message` (before `authenticator`).
   - In the body, after `self.store_raw_json_message = store_raw_json_message`, add `self.flatten_records = flatten_records`.
   - In the `__init__` docstring Args section, add a line: `flatten_records: when True, post_process flattens records; when False, returns row unchanged. Default False.`

6. **Branch in `post_process()`**
   - Replace the single `return flatten_json(row, self.except_keys, self.store_raw_json_message)` with:
     - If `self.flatten_records`: return `flatten_json(row, self.except_keys, self.store_raw_json_message)`.
     - Else: return `row` unchanged.
   - In the `post_process` docstring (Returns or a short note): state that when `flatten_records` is True the method returns `flatten_json(...)`; when False it returns the row unchanged.

7. **Run the two new tests** — they must pass. Run full suite: `uv run pytest` (and `uv run tox -e py` if applicable).

## Validation steps

- [ ] Two new tests in `tests/test_streams.py` with clear docstrings (what/why).
- [ ] Tests use nested payload and assert only on record structure (flattened vs nested).
- [ ] New tests fail when post_process is not branched (optional: temporarily revert branch to confirm).
- [ ] `DynamicStream.__init__` has `flatten_records: Optional[bool] = False` and `self.flatten_records = flatten_records`.
- [ ] `post_process()` branches on `self.flatten_records` and returns flattened record or row unchanged as specified.
- [ ] Docstrings updated for `__init__` and `post_process` per interfaces.md.
- [ ] New tests pass; full test suite passes (`uv run pytest`, and project quality run if any).
- [ ] No changes to `tap.py`, discovery, or `get_schema()` in this task.

## Documentation updates

- **None required.** Interfaces and master plan already describe DynamicStream and post_process. No user-facing docs or README changes in this task; task 05 covers broader test and documentation updates.
