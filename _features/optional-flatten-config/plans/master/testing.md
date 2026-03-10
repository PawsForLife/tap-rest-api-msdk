# Testing — Optional Flatten Config

## Strategy

- **TDD**: Add or update tests first so they fail, then implement until they pass. Per `.cursor/rules/development_practices.mdc`: tests validate functionality (black-box); no assertions on call counts or log lines.
- **Observable outcomes**: Assert on emitted records (shape: flattened vs nested), inferred schema (flattened vs nested properties), and stream-level override (stream config overrides top-level).
- **Regression**: All tests must pass before task complete; fix or adjust any test that assumes flattening so it either sets `flatten_records: true` or asserts on nested shape.

## Test cases by component

### Config and discovery

- **Config default**: With no `flatten_records` in config, resolved value is `false` (e.g. discover streams and assert stream has `flatten_records` false or assert sync output is nested). Can be covered indirectly via sync/schema tests.
- **Stream override**: Top-level `flatten_records: false`, stream-level `flatten_records: true` for one stream → that stream emits flattened records and has flattened schema; other streams nested. And vice versa: top-level true, stream-level false for one stream → that stream nested, others flattened.
- **Location**: `tests/test_tap.py` or `tests/test_streams.py` (wherever stream discovery and config resolution are exercised). Prefer reusing existing helpers (e.g. `config()`, `setup_api`, `requests_mock`).

### Schema inference (get_schema)

- **flatten_records true**: Mock GET response with nested payload; call code path that infers schema with `flatten_records=True`; assert inferred schema has flattened-style keys (e.g. `customer_id` at root, not nested `customer.id`).
- **flatten_records false**: Same nested payload; infer with `flatten_records=False`; assert schema has nested structure (e.g. `properties.customer.properties.id` or equivalent genson output for nested dicts).
- **Location**: `tests/test_tap.py` if get_schema is unit-testable with a mock tap and config; otherwise integration-style in test_streams with discovery + schema from API.

### Sync / post_process (DynamicStream)

- **flatten_records true**: Config with `flatten_records: true`; sync one stream; assert records are flattened (e.g. keys like `user_name` not nested `user.name`). Reuse existing test helpers and request mocks.
- **flatten_records false**: Config with `flatten_records: false`; sync one stream; assert records are nested (e.g. `record["user"]["name"]` present). Same style as existing sync tests (e.g. `get_records`, assert on list of records).
- **Location**: `tests/test_streams.py` (existing pattern: config, mock API, get stream from tap, call `get_records`, assert on records). See AI_CONTEXT_PATTERNS.md: “How do I test that sync returns the correct records for a stream?”

### Existing tests

- **Audit**: Identify tests that assume flattened output (e.g. assert on `record["some_flat_key"]`). Either:
  - Set `flatten_records: true` in the config used for that test, or
  - Change expectations to nested shape and set `flatten_records: false`.
- **Standard tap tests**: `tests/test_core.py` uses `get_tap_test_class(TapRestApiMsdk, config=config())`. Ensure `config()` includes `flatten_records: true` if the standard tests expect flattened records; or adjust default in test config and expectations per product choice (default off).

## Test implementation order

1. Add tests for sync with `flatten_records: false` (nested records) and `flatten_records: true` (flattened records); run and see failures.
2. Add tests for schema inference (flattened vs nested schema) if not covered by discovery tests; run and see failures.
3. Add stream-override test (one stream true, one false).
4. Implement code (implementation.md); re-run tests until they pass.
5. Update any existing tests that break (set `flatten_records: true` or adjust expectations).
6. Run full suite: `uv run pytest` and `uv run tox -e py`.

## Black-box and validity

- Do not assert on: number of times `flatten_json` is called, or specific log messages.
- Do assert on: structure of returned records (nested vs flat keys), structure of inferred schema (nested vs flat properties), and that stream-level config overrides top-level for the same stream.
- Tests must be able to fail: use distinct data (e.g. nested input) and assert a condition that is false when the feature is not implemented or is wrong (e.g. key missing or wrong shape).
