# Task 05: Update existing tests and documentation

## Background

Default `flatten_records: false` changes default behaviour: existing tests that assume flattened output may fail. All such tests must be updated (set `flatten_records: true` in config or adjust expectations to nested). Documentation (README, config.sample.json, docstrings) and AI_CONTEXT must reflect the new option.

**Dependencies:** Tasks 01–04 complete (full implementation in place).

## This Task

- **Audit existing tests:** Identify tests that assume flattened output (e.g. assert on `record["some_flat_key"]` or flattened schema). Either set `flatten_records: true` in the config used for that test, or change expectations to nested shape and keep default.
- **Standard tap tests:** `tests/test_core.py` uses `get_tap_test_class(TapRestApiMsdk, config=config())`. Ensure `config()` or the test config includes `flatten_records: true` if those tests expect flattened records; or adjust default and expectations per product choice (default off).
- **README.md:** In configuration/options section, document `flatten_records` (optional, boolean, default false). One to two sentences: when true, records and schema are flattened (current behaviour); when false, nested structure is preserved.
- **config.sample.json:** Add optional key `"flatten_records": false` at top-level and/or inside a stream example, with short comment if format allows.
- **Docstrings:** Already updated in tasks 02 and 03; verify `tap.py` get_schema and `streams.py` DynamicStream.__init__ and post_process docstrings are complete per documentation.md.
- **docs/AI_CONTEXT:** If tap config or post_process is described in AI_CONTEXT_REPOSITORY.md or AI_CONTEXT_QUICK_REFERENCE.md, add mention of `flatten_records` where stream/tap config or post_process is described. Keep under content-length limits.

**Acceptance:** `uv run pytest` and `uv run tox -e py` pass; README and config.sample.json document the option; AI_CONTEXT updated if applicable.

## Testing Needed

- Run full test suite: `uv run pytest` and `uv run tox -e py`. All tests must pass (no regressions).
- No new test files required; this task fixes and documents.
