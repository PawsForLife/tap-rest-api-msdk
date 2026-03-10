# Architecture — Optional Flatten Config

## System design

The feature is a **config-driven branch** over existing behaviour. Two code paths already exist conceptually (flatten vs pass-through); the new config only selects which path runs. No new services, processes, or data stores; no change to package layout (see AI_CONTEXT_REPOSITORY.md).

## Component breakdown

| Component | Responsibility |
|-----------|----------------|
| **tap (config)** | Define `flatten_records` in `common_properties`; default `false`. |
| **tap (discovery)** | Resolve `flatten_records` per stream (stream overrides top-level); pass to `DynamicStream` and to `get_schema()` when inferring. |
| **tap (get_schema)** | When `flatten_records` true: flatten each sample record then `add_object(flat_record)`. When false: `add_object(record)` (nested). Optional `_sdc_raw_json` in schema when `store_raw_json_message` is true, unchanged. |
| **streams (DynamicStream)** | New `flatten_records` constructor arg; in `post_process()`, if true return `flatten_json(...)`, else return row unchanged. |
| **utils** | No change; `flatten_json` remains the single implementation of flattening. |

## Data flow

- **Discovery (schema inference)**  
  Config → `discover_streams()` → for each stream without schema: resolve `flatten_records` → `get_schema(..., flatten_records=...)` → GET response → extract records → if `flatten_records`: flatten each sample then `builder.add_object(flat_record)`; else `builder.add_object(record)` → optional `_sdc_raw_json` in schema → return schema. Schema is passed to `DynamicStream(schema=schema, flatten_records=..., ...)`.

- **Sync**  
  For each stream: `parse_response()` yields raw records → `post_process(row)`: if `self.flatten_records` then `flatten_json(row, ...)` else return `row` → emit. No change to pagination, auth, or client.

## Design patterns

- **Config resolution**: Same pattern as `store_raw_json_message`: `stream.get("flatten_records", self.config.get("flatten_records", False))` in `discover_streams()`.
- **Conditional behaviour**: Branch in two places only—`get_schema()` (flatten samples or not) and `post_process()` (flatten row or not). No new abstractions.
- **Single implementation**: Flattening logic stays in `utils.flatten_json`; no duplication.
- **Dependency injection**: `flatten_records` is passed from tap into `DynamicStream` and into `get_schema()` as an explicit parameter (deterministic config, not injected from outside).

## References

- Data flow diagram and component boundaries: `docs/AI_CONTEXT/AI_CONTEXT_REPOSITORY.md`.
- Adding stream/top-level config: `docs/AI_CONTEXT/AI_CONTEXT_PATTERNS.md` (Q: “How do I add a new stream-level or top-level config property?”).
- Post-processing: `docs/AI_CONTEXT/AI_CONTEXT_PATTERNS.md` (Q: “How is post-processing applied to each record?”).
