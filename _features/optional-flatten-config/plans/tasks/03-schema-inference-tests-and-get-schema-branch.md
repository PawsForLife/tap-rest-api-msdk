# Task 03: Schema inference tests and get_schema branch — Implementation plan

## Overview

This task adds a **`flatten_records`** parameter to `get_schema()` and branches inside the inference loop: when `True`, sample records are flattened before schema inference (current behaviour); when `False`, raw nested records are passed to the builder so inferred schema matches nested structure. Discovery does **not** pass `flatten_records` in this task (task 04). Acceptance: calling `get_schema(..., flatten_records=True)` with nested payload yields flattened-style schema keys; calling with `flatten_records=False` yields nested schema structure. Existing `test_schema_inference` uses flat payload and continues to pass with the default parameter.

## Files to create/modify

| File | Action |
|------|--------|
| `tap_rest_api_msdk/tap.py` | **Modify**: Add parameter `flatten_records: bool = False` to `get_schema()` (after `headers`). In the loop over sample records (lines ~622–637), branch: if `flatten_records` then `flatten_json` then `builder.add_object(flat_record)`; else `builder.add_object(record)`. Keep `store_raw_json_message` / `_sdc_raw_json` handling unchanged (once per record after `add_object`). Update docstring for the new parameter. |
| `tests/test_tap.py` | **Modify**: Add two tests that mock a nested API payload, call `get_schema(..., flatten_records=True)` or `flatten_records=False`, and assert on inferred schema shape (flattened vs nested). |

No new files. No changes to `streams.py` or `discover_streams()` in this task.

## Test strategy (TDD order)

1. **Write tests first** (red):
   - **test_get_schema_flatten_records_true**: Mock GET with nested payload (e.g. `{"records": [{"customer": {"id": 1, "name": "x"}}]}`). Build tap with `config()` (ensure `num_inference_records` present). Call `tap.get_schema(records_path, except_keys, inference_records, path, params, headers, flatten_records=True)`. Assert inferred schema has flattened-style root-level properties (e.g. `"customer_id"` and/or `"customer_name"` or equivalent genson key names from flattened dict). **What**: Schema inference with `flatten_records=True` produces flattened property keys. **Why**: Ensures the True branch matches current behaviour and product requirement for flattened schema when flattening is on.
   - **test_get_schema_flatten_records_false**: Same nested payload and tap. Call `get_schema(..., flatten_records=False)`. Assert inferred schema has nested structure (e.g. `schema["properties"]["customer"]["properties"]["id"]` or equivalent genson nested output). **What**: Schema inference with `flatten_records=False` preserves nested structure. **Why**: Ensures inferred schema matches emitted record shape when flattening is off.
   - **Location**: `tests/test_tap.py`. Use `requests_mock`, `config()`, and a nested `json_resp` variant (e.g. `{"records": [{"customer": {"id": 1, "name": "a"}}]}`). Use `records_path="$.records[*]"`, `except_keys=[]`, and appropriate `path`/`params`/`headers` so the mocked URL matches. Get `inference_records` from config (e.g. `tap.config["num_inference_records"]`) or use a small constant (e.g. `5`).
   - **Black-box**: Assert only on the structure of the returned schema dict (presence of flattened vs nested property paths). Do not assert on call counts or log lines.

2. **Run tests**: New tests fail (parameter and branch not present; or branch always flattens).

3. **Implement**: Add parameter and conditional in `get_schema()` (see Implementation order).

4. **Run tests**: New tests pass. Run full suite; `test_schema_inference` must still pass (flat payload + default `flatten_records=False` still yields same flat schema).

## Implementation order

1. **Add tests in `tests/test_tap.py`**
   - Define a nested response payload used by both tests, e.g. `NESTED_RESPONSE = {"records": [{"customer": {"id": 1, "name": "a"}}]}`.
   - In each test: `setup_api(requests_mock, json_extras=...)` or override response with `requests_mock.get(url_path(), json=NESTED_RESPONSE)`. Ensure `records_path` in config is `"$.records[*]"` so extraction yields `[{"customer": {"id": 1, "name": "a"}}]`.
   - Build tap: `TapRestApiMsdk(config=config(), parse_env_config=True)`. Ensure config has `num_inference_records` (add to `config()` extras if not already present).
   - Call `tap.get_schema(records_path="$.records[*]", except_keys=[], inference_records=tap.config["num_inference_records"], path="/path_test", params={}, headers={}, flatten_records=True)` (or `False`).
   - **True test**: Assert schema has flattened keys. Genson with flattened input produces root-level keys; e.g. `assert "customer_id" in schema["properties"] or "customer_name" in schema["properties"]` (or the exact key names produced by `flatten_json` for `customer.id` / `customer.name` — check `utils.flatten_json` key format). Prefer one clear structural assertion (e.g. no nested `schema["properties"]["customer"]` with sub-properties, or presence of a known flattened key).
   - **False test**: Assert schema has nested structure; e.g. `assert "customer" in schema["properties"]` and `assert "properties" in schema["properties"]["customer"]` and `"id" in schema["properties"]["customer"]["properties"]`.
   - Add docstrings: what is being tested (schema shape for flatten_records True/False) and why (acceptance criteria for optional flatten config).

2. **Run pytest for the two new tests**: Expect failure (get_schema does not accept `flatten_records` or always flattens).

3. **Update `get_schema()` in `tap_rest_api_msdk/tap.py`**
   - **Signature**: Add `flatten_records: bool = False` after `headers: dict`.
   - **Docstring**: In Args, add a line: `flatten_records: When true, flatten sample records before inference; when false, infer from raw nested records.`
   - **Loop body** (current block over `records`):
     - If `flatten_records`: keep current logic — `flat_record = flatten_json(record, except_keys, store_raw_json_message=False)`, then `builder.add_object(flat_record)`.
     - Else: `builder.add_object(record)` (no flatten).
     - Keep the existing `if self.config.get("store_raw_json_message"): builder.add_object({"_sdc_raw_json": {}})` unchanged (one block after the single `add_object` so it runs for each record in both branches).
   - Do not change request construction, `extract_jsonpath`, or `SchemaBuilder` setup.

4. **Run tests**: Both new tests pass. Run `uv run pytest tests/test_tap.py` then full suite `uv run pytest` (and `uv run tox -e py` if applicable).

## Validation steps

- [ ] Two new tests in `tests/test_tap.py` with nested payload and clear docstrings (what/why).
- [ ] Tests assert only on schema structure (flattened vs nested); no assertions on call counts or logs.
- [ ] New tests fail before implementation and pass after.
- [ ] `get_schema()` has parameter `flatten_records: bool = False` and updated docstring.
- [ ] Inference loop branches on `flatten_records`; `_sdc_raw_json` handling unchanged.
- [ ] `test_schema_inference` still passes (flat payload + default False → same flat schema).
- [ ] Full test suite passes: `uv run pytest` and project quality command.
- [ ] No changes to `discover_streams()` or `streams.py` in this task.

## Documentation updates

- **None required for this task.** Component context (e.g. `docs/AI_CONTEXT/AI_CONTEXT_tap_rest_api_msdk.md`) can be updated in task 05 when all behaviour and tests are wired. The master plan and interfaces already describe `get_schema(..., flatten_records)`.
