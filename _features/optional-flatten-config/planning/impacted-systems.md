# Impacted systems — optional flatten config

## Summary

The feature adds an optional config to control whether records are flattened. Default is **off** (no flatten). These existing modules and interfaces are impacted.

---

## Modules

| Module | Impact |
|--------|--------|
| **tap_rest_api_msdk/tap.py** | Config schema: add property (tap + stream). `discover_streams()`: pass value into `DynamicStream` and into `get_schema()` when inferring. `get_schema()`: only flatten sample records when config is on; otherwise infer from raw nested records. |
| **tap_rest_api_msdk/streams.py** | `DynamicStream`: new constructor argument; `post_process()`: call `flatten_json` only when config is on, otherwise return row as-is. |
| **tap_rest_api_msdk/utils.py** | No signature change. `flatten_json` remains as-is; call sites become conditional. |

---

## Interfaces

- **Config (JSON schema)**  
  New optional boolean property (e.g. `flatten_records`), default `false`. Supported at top-level and per-stream; stream overrides top-level (same pattern as `store_raw_json_message`).

- **TapRestApiMsdk.discover_streams()**  
  Resolve the property from stream then config (e.g. `stream.get("flatten_records", self.config.get("flatten_records", False))`). Pass into `DynamicStream(...)` and, when calling `get_schema()`, pass so inference uses same behaviour.

- **TapRestApiMsdk.get_schema(..., flatten_records)**  
  When `flatten_records` is true: keep current behaviour (flatten sample records, then infer). When false: infer from raw records (no `flatten_json`); `SchemaBuilder.add_object(record)` supports nested dicts.

- **DynamicStream**  
  New optional constructor parameter (e.g. `flatten_records: bool = False`). Stored as instance attribute. Used in `post_process()` to decide whether to return `flatten_json(row, ...)` or `row`.

---

## Functionality

- **Schema inference**  
  Today: sample records are always flattened, then schema is inferred. After change: when flatten is off, sample records are not flattened; inference runs on nested structure so emitted schema matches emitted record shape.

- **Record emission**  
  Today: every record is flattened in `post_process()`. After change: when flatten is off, `post_process()` returns the row unchanged (except optional `_sdc_raw_json` handling if present; behaviour for that when not flattening should be defined—e.g. omit or keep as-is).

- **Tests**  
  Tests that assume flattened records or flattened schema must be updated: either set `flatten_records: true` where flattening is required, or assert on nested shape when testing non-flattened behaviour. New tests for config off (nested output + nested schema) and config on (current behaviour).

---

## Dependencies

- No new package dependencies. `genson.SchemaBuilder` already supports nested objects for inference.
