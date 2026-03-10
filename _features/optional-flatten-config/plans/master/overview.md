# Implementation Plan — Optional Flatten Config

## Executive summary

Add an optional tap/stream config property **`flatten_records`** (boolean, default **`false`**) so users can choose whether extracted JSON records are flattened (current behaviour) or emitted as-is (nested). Schema inference will respect this setting so inferred schema matches emitted record shape. No new modules or external dependencies; changes are confined to config schema, discovery, schema inference, and stream post-processing.

## Objectives

- **Config**: Expose `flatten_records` at top-level and stream-level; stream overrides top-level (same pattern as `store_raw_json_message`).
- **Sync**: When `flatten_records` is true, keep current behaviour (flatten in `post_process`). When false, emit records unchanged (no flatten).
- **Discovery**: When inferring schema, if `flatten_records` is true, flatten sample records then infer; if false, infer from raw nested records.
- **Backward compatibility**: Default `false` means existing configs that do not set the property get no flattening. Configs that need current behaviour must set `flatten_records: true`.

## Success criteria

- With `flatten_records: false` (default): records and inferred schema preserve nested structure; no call to `flatten_json` in sync or discovery for that stream.
- With `flatten_records: true`: behaviour matches current tap (flattened records and flattened schema).
- Stream-level `flatten_records` overrides top-level for that stream.
- All existing tests that assume flattening either set `flatten_records: true` in config or assert on nested shape where appropriate; full test suite passes.

## Constraints

- **Internal only**: No Singer SDK schema/record flattening; use existing `utils.flatten_json` behind a config gate.
- **No new dependencies**: `genson.SchemaBuilder.add_object()` already accepts nested dicts.
- **`_sdc_raw_json` when flatten is off**: When `flatten_records` is false, `post_process` does not add `_sdc_raw_json` (emit row unchanged). If product later requires raw copy without flattening, address in a follow-up.
- Adhere to project TDD, black-box testing, and content-length rules (see architecture.md and testing.md).

## Relationship to existing systems

- **tap**: Config schema and discovery own the new property and pass it into streams and `get_schema()`.
- **streams**: `DynamicStream` gains a constructor argument and branches in `post_process()`.
- **utils**: `flatten_json` is unchanged; call sites become conditional.
- **client / auth / pagination**: No changes.
