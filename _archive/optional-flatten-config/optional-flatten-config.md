# Archive: Optional flatten config

## The request

The tap previously flattened all extracted JSON records by default (nested keys like `customer.id` became `customer_id`). Users who needed to preserve nested structure for downstream consumers or existing schemas had no way to turn flattening off.

**Goal:** Add an optional tap/stream config property to control flattening, default **off** (no flattening). When on, retain current behaviour. Schema inference must respect the setting so inferred schema matches emitted record shape.

**Testing:** Unit tests for config off → nested records and nested schema; config on → flattened records and schema; stream-level override. Existing tests that assume flattening were to be updated or run with flatten enabled.

---

## Planned approach

**Solution:** Internal config and branching only (no Singer SDK flattening). One boolean property `flatten_records` (default `false`) in `common_properties`; stream overrides top-level (same pattern as `store_raw_json_message`).

**Architecture:**

- **tap.py:** Add `flatten_records` to config schema; in `discover_streams()` resolve per stream and pass into `get_schema()` and `DynamicStream()`; in `get_schema(..., flatten_records)` branch: if true flatten samples then infer, if false `add_object(record)` (nested).
- **streams.py:** `DynamicStream` gains `flatten_records` constructor arg and attribute; `post_process()` returns `flatten_json(...)` when true, else returns row unchanged. No `_sdc_raw_json` when flatten is off (emit row unchanged).
- **utils:** `flatten_json` unchanged; call sites become conditional.

**Task breakdown (TDD):**

1. Add `flatten_records` to config schema; test that schema exposes it with default false.
2. Add `flatten_records` to `DynamicStream` and branch in `post_process`; add sync tests (flattened vs nested).
3. Add `flatten_records` to `get_schema` and branch in inference loop; add schema-inference tests (flattened vs nested).
4. In `discover_streams()` resolve and pass `flatten_records` to `get_schema` and `DynamicStream`; add stream-override tests.
5. Audit tests that assume flattening (set `flatten_records: true` or adjust expectations); update README, config.sample.json, docstrings, AI_CONTEXT.

---

## What was implemented

- **Config:** `flatten_records` (boolean, default false) added to `common_properties` in `tap.py`. Top-level and stream-level; stream overrides top-level in `discover_streams()`.
- **Sync:** `DynamicStream` has `flatten_records` parameter and attribute; `post_process()` flattens only when `self.flatten_records` is true, otherwise returns row unchanged.
- **Discovery / schema:** `get_schema(..., flatten_records=False)` added; inference loop flattens sample records only when `flatten_records` is true; `discover_streams()` resolves and passes `flatten_records` into `get_schema()` and `DynamicStream()`.
- **Tests:** Config-schema test (`test_config_schema_includes_flatten_records`); get_schema tests for true (flattened schema) and false (nested schema); sync tests for flattened vs nested records; two stream-override tests (top-level false + stream true, and top-level true + stream false). All black-box (record and schema structure only).
- **Docs:** README documents `flatten_records` in configuration and Meltano settings; `config.sample.json` includes `"flatten_records": false`; docstrings updated for `get_schema`, `DynamicStream.__init__`, and `post_process`. AI_CONTEXT updated per task 05 plan.

No new dependencies; `genson.SchemaBuilder.add_object()` already supports nested dicts. Default off means existing configs that omit the property get nested output; configs that need current (flattened) behaviour set `flatten_records: true`.
