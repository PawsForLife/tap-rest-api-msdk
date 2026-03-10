# Task list: Optional flatten config

High-level tasks and execution order. Each task document in `tasks/` has Background, This Task, and Testing Needed.

## Execution order

| Order | Task file | Summary |
|-------|-----------|---------|
| 1 | `01-add-flatten-records-config-property.md` | Add `flatten_records` (boolean, default false) to tap config schema in `common_properties`. |
| 2 | `02-sync-tests-and-post-process-branch.md` | Add DynamicStream `flatten_records` param and attribute; branch in `post_process()`. Add sync tests (nested vs flattened). |
| 3 | `03-schema-inference-tests-and-get-schema-branch.md` | Add `get_schema(..., flatten_records=False)` and branch in inference loop. Add schema inference tests. |
| 4 | `04-resolve-and-pass-flatten-records-in-discovery.md` | In `discover_streams()` resolve `flatten_records` (stream overrides top-level), pass to `get_schema()` and `DynamicStream()`. Add stream-override tests. |
| 5 | `05-update-existing-tests-and-documentation.md` | Audit tests that assume flattening; set `flatten_records: true` or adjust expectations. Update README, config.sample.json, docstrings, AI_CONTEXT. |

## Dependencies

- **01** has no dependencies.
- **02** and **03** depend on **01** (config property must exist).
- **04** depends on **01**, **02**, **03** (resolve and pass into existing params).
- **05** depends on **01–04** (full implementation and tests).

## Interface requirements

- **Config:** `flatten_records` in `common_properties`; stream-level overrides top-level in `discover_streams()`.
- **Tap → get_schema:** `get_schema(..., flatten_records=...)`; when true flatten samples then infer, when false `add_object(record)`.
- **Tap → DynamicStream:** `DynamicStream(..., flatten_records=...)`; when true `post_process` returns `flatten_json(...)`, else returns row unchanged.
- **utils.flatten_json:** Unchanged; called only when `flatten_records` is true.

## TDD

Tests are written first in tasks 02, 03, and 04; implementation in those tasks satisfies the tests. Task 05 updates any existing tests that break and completes documentation.
