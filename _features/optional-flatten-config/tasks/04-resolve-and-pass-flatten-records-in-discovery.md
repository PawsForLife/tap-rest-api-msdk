# Task 04: Resolve and pass flatten_records in discovery

## Background

Discovery must resolve `flatten_records` per stream (stream overrides top-level, same pattern as `store_raw_json_message`) and pass it to `get_schema()` and `DynamicStream()`. This wires the config from task 01 to the behaviour implemented in tasks 02 and 03.

**Dependencies:** Tasks 01, 02, 03 (config property, DynamicStream param and post_process branch, get_schema param and branch).

## This Task

- **File:** `tap_rest_api_msdk/tap.py`.
- **discover_streams():**
  - Before the block that builds `schema` (see implementation.md), resolve: `flatten_records = stream.get("flatten_records", self.config.get("flatten_records", False))`.
  - In the `else` branch where `self.get_schema(...)` is called, add keyword argument `flatten_records=flatten_records`.
  - In the `DynamicStream(...)` instantiation, add argument `flatten_records=flatten_records` (e.g. after `store_raw_json_message`).

**Acceptance:** Top-level `flatten_records: false` with no stream override yields nested records and nested schema; top-level `true` yields flattened. Stream-level value overrides top-level for that stream.

## Testing Needed

- **Stream override (top-level false, stream true):** Config with top-level `flatten_records: false` and one stream with `flatten_records: true`. Assert that stream emits flattened records and has flattened schema; other streams (if any) emit nested.
- **Stream override (top-level true, stream false):** Config with top-level `flatten_records: true` and one stream with `flatten_records: false`. Assert that stream emits nested records and has nested schema; others flattened.
- **Location:** `tests/test_tap.py` or `tests/test_streams.py`; reuse existing discovery/sync helpers.
- **Black-box:** Assert on emitted records and schema structure only.
