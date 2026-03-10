# Feature: Optional flatten config (off by default)

## Background

The tap currently flattens all extracted JSON records by default. Flattening turns nested objects into a single level with path-based keys (e.g. `customer.custom_id` → `customer_custom_id`). This behaviour is applied in stream `post_process` and in schema inference. Users who want to preserve the original nested structure (e.g. to align with existing nested schemas or downstream consumers) cannot do so.

## This Task

- Add an optional tap/stream config property to control whether records are flattened.
- Default the new config to **off** (no flattening): extracted JSON is emitted as-is.
- When the config is **on**, retain current behaviour (flatten records as today).
- Ensure schema inference respects this setting (inferred schema matches emitted record shape).

## Testing Needed

- Unit tests: config off → records not flattened; config on → records flattened as today.
- Unit tests: schema inference with config off produces nested schema; with config on produces flattened schema.
- Existing tests that assume flattening must be updated or run with flatten enabled where appropriate.
