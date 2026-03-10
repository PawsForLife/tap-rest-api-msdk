# Pipeline Scratchpad

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
