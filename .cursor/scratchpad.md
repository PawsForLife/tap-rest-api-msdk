# Pipeline Scratchpad

## Feature: optional-flatten-config

**Pipeline State:** Phase 3 Complete; Phase 4–6 Not started.

**Task Completion Status:** None completed.

**Task count:** 5.

**Execution Order:** 01-add-flatten-records-config-property.md, 02-sync-tests-and-post-process-branch.md, 03-schema-inference-tests-and-get-schema-branch.md, 04-resolve-and-pass-flatten-records-in-discovery.md, 05-update-existing-tests-and-documentation.md.

**Output directory:** `_features/optional-flatten-config/planning/`

**Plan location:** `_features/optional-flatten-config/plans/master/`

**Key decisions:**
- Single boolean `flatten_records` (default `false`): stream overrides top-level; when false, no flatten in sync or schema inference; when true, current behaviour.
- When `flatten_records` is false, `post_process` returns row unchanged (no `_sdc_raw_json` added); raw-copy when not flattening deferred to follow-up if needed.
- Implementation is config-driven branching only in `tap.py` and `streams.py`; `utils.flatten_json` unchanged, called only when `flatten_records` is true.

**Key findings:**
- Flattening is implemented in `tap.py` (`get_schema()` flattens sample records before genson inference) and `streams.py` (`post_process()` always calls `flatten_json`). Config is resolved in `discover_streams()` and passed into `DynamicStream`; no existing property controls flattening.
- Schema inference: when flatten is off, use `SchemaBuilder.add_object(record)` on raw nested records (genson supports nested dicts). When on, keep current behaviour (flatten then add_object).
- No new modules or dependencies; `utils.flatten_json` is unchanged and invoked only when config is on.

**Selected solution:** Internal config only. Add boolean `flatten_records` (default `false`) at top-level and stream-level; stream overrides top-level. In `post_process()`: if `flatten_records` true, return `flatten_json(row, ...)`; else return row unchanged. In `get_schema()`: add parameter `flatten_records`; when true flatten samples then infer; when false infer from raw records. Pass `flatten_records` from discover_streams into `DynamicStream` and into `get_schema()`.

---

## Bug: stella-feedback-local-run-failure

**Pipeline State:** Phase 1 Complete.

**Investigation directory:** `_bugs/stella-feedback-local-run-failure/investigation/`

### Root cause (hypothesis)

- target-jsonl validates RECORDs using the schema from the tap’s SCHEMA message. The failing schema has root-level `customer_custom_id` with `type: 'string'`; the API sends `customer_custom_id: null`, so validation fails.
- The project schema (`schemas/feedback.json`) does **not** define `customer_custom_id` (it uses nested `customer.custom_id`). So the schema in use is **not** the project file; it is the tap’s **inferred** (flattened) schema.
- tap-rest-api-msdk **always** flattens records (`post_process` → `flatten_json`). So RECORDs have flattened keys (e.g. `customer_custom_id`). When no schema path is used (or path is wrong/missing), the tap infers schema from flattened records; inferred schema can have `customer_custom_id` as `string` (not nullable), causing the error.
- Even if the tap used the project schema, that schema is **nested** while records are **flattened**, so schema and record shape would not match. A fix must use a **flattened** schema that matches the tap’s record shape and allows nulls (e.g. `customer_custom_id: ["null", "string"]`).

### Affected components

- tap-stella-feedback (stream `feedback`, `schema: schemas/feedback.json` in meltano.yml)
- tap-rest-api-msdk (schema loading from path vs inference; record flattening)
- target-jsonl (Draft4Validator; fails when property type is `string` and value is `None`)
- schemas/feedback.json (nested; not aligned with flattened records)

### Task completion status

- Phase 1 (Investigate): Complete.
- Phases 2–7: Pending.
