# Selected solution — optional flatten config (internal)

## Approach

Add a boolean config property **`flatten_records`**, default **`false`** (no flattening). When `true`, keep current behaviour (flatten in sync and in schema inference). When `false`, emit records as-is and infer schema from nested sample records. Implement with internal branching only; no new dependencies.

---

## Config

- **Property:** `flatten_records` (boolean).
- **Scope:** Top-level and stream-level; stream overrides top-level (same merge as `store_raw_json_message`).
- **Default:** `false`.
- **Schema:** Add to stream-level config (e.g. in `common_properties` in `tap.py`) so it appears in both top-level and per-stream config.

---

## Interfaces and behaviour

### tap.py

1. **Config schema**  
   Add `flatten_records` to the stream/top-level properties, default `false`, description: when true, flatten records and infer flattened schema; when false, preserve nested structure.

2. **discover_streams()**  
   Resolve: `flatten_records = stream.get("flatten_records", self.config.get("flatten_records", False))`.  
   When calling `get_schema()`, pass this value (e.g. add argument or derive from stream/config in the same way).  
   Pass `flatten_records` into `DynamicStream(...)`.

3. **get_schema(..., flatten_records=False)**  
   - If `flatten_records`: for each sample record, `flat_record = flatten_json(record, except_keys, store_raw_json_message=False)`; `builder.add_object(flat_record)`. (Current behaviour.)  
   - If not `flatten_records`: `builder.add_object(record)` (no flatten).  
   Keep `store_raw_json_message` handling unchanged (add `_sdc_raw_json` to schema when config says so).

### streams.py

4. **DynamicStream.__init__**  
   Add parameter `flatten_records: bool = False`; set `self.flatten_records = flatten_records`.

5. **post_process()**  
   - If `self.flatten_records`: return `flatten_json(row, self.except_keys, self.store_raw_json_message)`.  
   - Else: return `row` as-is. (If we want `_sdc_raw_json` when not flattening, add a single top-level key `_sdc_raw_json` with the full row; otherwise omit for simplicity. Document choice; recommended: when not flattening, do not add `_sdc_raw_json` unless we explicitly define and test it.)

Recommendation: when `flatten_records` is false, do not add `_sdc_raw_json` in `post_process` (keep behaviour “emit row unchanged”). If product later requires raw copy when not flattening, add it in a follow-up.

---

## Algorithm (discovery, flatten off)

- GET response → extract records via `records_path`.
- For each sample record (up to `inference_records`): validate `type(record) is dict`, then `builder.add_object(record)` (no flatten).
- Optional: if `store_raw_json_message`, add `builder.add_object({"_sdc_raw_json": {}})` so schema includes the field when inference is used with that config.
- Return `builder.to_schema()`.

---

## Fit with existing code

- **utils.flatten_json** — Unchanged; called only when `flatten_records` is true.
- **Tests** — New: config off ⇒ nested records and nested schema; config on ⇒ flattened records and flattened schema; stream override. Update existing tests that assume flattening to set `flatten_records: true` or adjust expectations.

---

## Summary

Single boolean `flatten_records` (default false), resolved at stream level from stream then config. Tap: add to schema, pass into `DynamicStream` and `get_schema`. Stream: `post_process` flattens only if true. Discovery: `get_schema` flattens sample records only if true. No new modules; no new deps.
