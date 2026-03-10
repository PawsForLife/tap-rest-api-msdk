# Task 01: Add flatten_records config property — Implementation plan

## Overview

This task adds the **`flatten_records`** config property to the tap’s JSON Schema only. It is the first interface change for optional-flatten-config: no discovery, schema inference, or sync behaviour is changed. The property is added to `common_properties` in `tap.py`, so it appears in both top-level and stream-level config. Acceptance: the tap’s config schema (e.g. from `config_jsonschema` or discovery) includes `flatten_records` with default `false`; runtime behaviour is unchanged.

## Files to create/modify

| File | Action |
|------|--------|
| `tap_rest_api_msdk/tap.py` | **Modify**: Add one `th.Property` for `flatten_records` inside `common_properties`, immediately after the `store_raw_json_message` property (after line 351, before `pagination_page_size`). |
| `tests/test_tap.py` | **Modify**: Add one test that the tap’s config schema includes `flatten_records` with type boolean and default false. |

No new files. No changes to `streams.py`, discovery, `get_schema`, or documentation in this task.

## Test strategy (TDD order)

1. **Write test first** (red): Add a test that asserts the tap’s config schema contains a `flatten_records` property with:
   - `"flatten_records"` present in the schema’s `properties`
   - Property has `"default": False` and type consistent with boolean (e.g. `"type": "boolean"` in JSON Schema).
   - **Location**: `tests/test_tap.py`.
   - **What is tested**: That the tap’s config schema (exposed via `TapRestApiMsdk.config_jsonschema` or equivalent) declares the new property so that discovery/config validation and later tasks can rely on it.
   - **Why**: Black-box; we assert on the observable config schema, not on implementation details. The test must be able to fail before the property exists and pass after it is added.

2. **Run tests**: Run the new test; it must fail (property missing).

3. **Implement**: Add the `flatten_records` property to `common_properties` in `tap.py` (see Implementation order below).

4. **Run tests**: Re-run the test; it must pass. Run the full test suite to confirm no regressions.

## Implementation order

1. **Add test in `tests/test_tap.py`**
   - Obtain the tap’s config schema (e.g. `TapRestApiMsdk.config_jsonschema` — the class-level schema built from `top_level_properties.to_dict()` in `tap.py`).
   - Assert `"properties" in schema` and `"flatten_records" in schema["properties"]`.
   - Assert `schema["properties"]["flatten_records"].get("default") is False`.
   - Assert the property type is boolean (e.g. `schema["properties"]["flatten_records"].get("type") == "boolean"` or equivalent depending on SDK output).
   - Add a short docstring: what is being tested (config schema exposes `flatten_records`) and why (acceptance that the property exists with default false before any behaviour uses it).

2. **Run pytest for the new test**: Expect failure.

3. **Add property in `tap_rest_api_msdk/tap.py`**
   - **Location**: Inside `common_properties`, immediately after the `store_raw_json_message` block (after the closing `),` of that `th.Property`, before the `th.Property("pagination_page_size", ...)`).
   - **Code**: Add:
     ```python
     th.Property(
         "flatten_records",
         th.BooleanType,
         default=False,
         required=False,
         description="When true, flatten records and infer flattened schema; "
         "when false, preserve nested structure.",
     ),
     ```
   - **Exact placement**: Between `store_raw_json_message` and `pagination_page_size` so that `flatten_records` is part of `common_properties` and thus appears in both top-level and stream-level config.

4. **Run tests**: New test passes. Run full suite: `uv run pytest` (and `uv run tox -e py` if applicable).

## Validation steps

- [ ] New test exists in `tests/test_tap.py` and documents what/why.
- [ ] New test fails when the property is not present (optional sanity check: comment out the property and run test).
- [ ] Property added in `tap.py` in `common_properties` after `store_raw_json_message`, before `pagination_page_size`.
- [ ] Property has: name `"flatten_records"`, type `th.BooleanType`, `default=False`, `required=False`, and the specified description.
- [ ] New test passes.
- [ ] Full test suite passes: `uv run pytest` (and project’s standard quality run, e.g. `uv run tox -e py`).
- [ ] No changes to `streams.py`, `get_schema()`, `discover_streams()`, or `post_process()` — behaviour unchanged.

## Documentation updates

- **None required for this task.** The master plan and interfaces already describe `flatten_records`. No README or user-facing config table update is required for a schema-only change; later tasks (e.g. 05) will update existing tests and documentation when behaviour is wired.
