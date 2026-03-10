# New systems — optional flatten config

## Summary

No new modules or new external dependencies. The feature is a config-driven branch over existing behaviour (flatten vs pass-through) and schema inference (flatten then infer vs infer from nested).

---

## New config surface

- **Property name** (recommended): `flatten_records` (boolean).
- **Placement**: In `common_properties` (or equivalent stream-level schema) so it appears in both top-level and stream-level config. Same pattern as `store_raw_json_message`.
- **Default**: `false` (no flattening; emit and infer nested).
- **Semantics**: When `true`, retain current behaviour (flatten in `post_process` and in schema inference). When `false`, do not flatten; infer schema from raw nested records.

---

## New behaviour paths

| Path | When | Behaviour |
|------|------|------------|
| Sync, flatten on | `flatten_records === true` | `post_process()` returns `flatten_json(row, ...)` (current). |
| Sync, flatten off | `flatten_records === false` | `post_process()` returns `row` unchanged (no flatten). Optional: if `store_raw_json_message` is true, behaviour for `_sdc_raw_json` when not flattening to be defined (e.g. still add raw payload in a single field or omit). |
| Discovery, flatten on | `flatten_records === true` | `get_schema()` flattens sample records then infers (current). |
| Discovery, flatten off | `flatten_records === false` | `get_schema()` infers from raw (nested) records; no call to `flatten_json`. |

---

## New tests

- **Config off**: Assert records are not flattened (nested structure preserved); assert inferred schema has nested properties.
- **Config on**: Assert records are flattened (current behaviour); assert inferred schema is flattened.
- **Stream override**: Top-level `flatten_records: false`, stream-level `flatten_records: true` (and vice versa); assert stream-level wins and record shape matches.
- **Existing tests**: Update or parameterise so expectations align with config (flatten on where current behaviour is assumed).

---

## Optional: _sdc_raw_json when flatten is off

If `store_raw_json_message` is true and `flatten_records` is false, one option is to add a single top-level property `_sdc_raw_json` with the full record as value (no other flattening). This keeps a consistent “raw copy” behaviour. Document the chosen behaviour in selected-solution.
