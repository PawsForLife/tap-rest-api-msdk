# Possible solutions — optional flatten config

## Summary

Two approaches: (A) internal config + conditional logic in this tap, or (B) delegate to Singer SDK flattening where applicable. Recommendation: **internal** (A) for minimal change and full control over semantics and default.

---

## Option A: Internal config and branching

**Description:** Add a tap/stream boolean property (e.g. `flatten_records`, default `false`). In `post_process()` and `get_schema()`, call `flatten_json` only when the property is true; otherwise pass through the record or infer from nested structure.

**Pros:**

- Small, local change: two call sites and config schema.
- No new dependencies; `genson` already infers from nested dicts.
- Default-off matches feature requirement; no behaviour change for existing configs that do not set the property (default false = no flatten).
- Full control over semantics (e.g. `_sdc_raw_json` when flatten is off).

**Cons:**

- Duplicates concept of “flatten or not” in this tap rather than reusing SDK machinery (if SDK were to support it for this flow).

---

## Option B: Use Singer SDK flattening

**Description:** Singer SDK has `flattening_enabled`, `flattening_max_depth`, and related options (stream maps / schema flattening). Refactor the tap to use SDK record/schema flattening instead of custom `flatten_json` in `post_process` and in discovery.

**Pros:**

- Aligns with SDK conventions; one place for flatten behaviour if other taps use it.
- Possible future sharing of behaviour and fixes with SDK.

**Cons:**

- This tap currently flattens in Python before writing records; SDK flattening is tied to stream maps and may not apply in the same place (e.g. schema vs record at sync).
- Larger refactor: replace custom discovery/sync flatten path with SDK mechanisms; may require different config names and defaults.
- SDK flattening has known edge cases (e.g. typeless properties, nulls) that could affect this tap’s behaviour.

---

## Recommendation

**Option A (internal).** The feature is “optional flatten, default off.” Implementing that with a single boolean and conditional use of existing `flatten_json` is the smallest, clearest change and keeps schema and record shape under this tap’s control. Option B is viable only if we later decide to standardise on SDK flattening and accept a larger refactor and config shape.
