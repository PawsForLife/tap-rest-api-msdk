# Task 01: Add flatten_records config property

## Background

The optional-flatten-config feature requires a tap/stream config property `flatten_records` (boolean, default `false`) so users can control whether records are flattened or emitted as nested. This task adds the property to the config schema only; no behaviour changes yet. Same pattern as `store_raw_json_message` in `common_properties`.

**Dependencies:** None (first interface change).

## This Task

- **File:** `tap_rest_api_msdk/tap.py`.
- **Location:** Inside `common_properties`, after the `store_raw_json_message` property (see implementation.md).
- **Change:** Add a new `th.Property`:
  - Name: `"flatten_records"`.
  - Type: `th.BooleanType`.
  - `default=False`, `required=False`.
  - Description: When true, flatten records and infer flattened schema; when false, preserve nested structure.

**Acceptance:** Config schema (e.g. from `--about` or discovery) includes `flatten_records` with default false; no runtime behaviour change.

## Testing Needed

- Optional: Assert that the tap’s config schema (e.g. from `config_jsonschema` or a minimal discover run) contains a `flatten_records` property with default `false`. Can be covered indirectly by later tasks that use the property in discovery/sync.
