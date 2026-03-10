# Implementation — Optional Flatten Config

## Implementation order

1. **Config and interfaces** (tap schema, DynamicStream parameter, get_schema parameter).
2. **Discovery and schema inference** (resolve flatten_records, pass into get_schema and DynamicStream; branch inside get_schema).
3. **Stream post_process** (branch in post_process using self.flatten_records).
4. **Tests** (TDD: tests written/updated first per testing.md; implementation satisfies them).

Per project rules: models/interfaces first, then implementation; tests before or alongside implementation so they can fail then pass.

## Step-by-step

### Step 1: Config schema (tap.py)

- **File**: `tap_rest_api_msdk/tap.py`.
- **Location**: Inside `common_properties`, after the `store_raw_json_message` property (around line 352).
- **Change**: Add a new `th.Property`:
  - Name: `"flatten_records"`.
  - Type: `th.BooleanType`.
  - `default=False`, `required=False`.
  - Description: When true, flatten records and infer flattened schema; when false, preserve nested structure.

### Step 2: Resolve and pass flatten_records in discover_streams() (tap.py)

- **File**: `tap_rest_api_msdk/tap.py`.
- **Location**: In `discover_streams()`, before the block that builds `schema` (around line 479), add:
  - `flatten_records = stream.get("flatten_records", self.config.get("flatten_records", False))`.
- **get_schema call**: In the `else` branch where `self.get_schema(...)` is called (lines 495–505), add keyword argument `flatten_records=flatten_records`.
- **DynamicStream call**: In the `DynamicStream(...)` instantiation (lines 507–552), add argument `flatten_records=flatten_records` (e.g. after `store_raw_json_message`).

### Step 3: get_schema() signature and body (tap.py)

- **File**: `tap_rest_api_msdk/tap.py`.
- **Signature**: Add `flatten_records: bool = False` to `get_schema(..., path, params, headers)` (e.g. after `headers`).
- **Body**: In the loop over records (around 622–637):
  - If `flatten_records`: keep current logic (`flat_record = flatten_json(record, except_keys, store_raw_json_message=False)`, `builder.add_object(flat_record)`).
  - Else: `builder.add_object(record)` (no flatten).
  - Keep the existing `if self.config.get("store_raw_json_message"): builder.add_object({"_sdc_raw_json": {}})` in both branches (or once after the record add, as today).

### Step 4: DynamicStream constructor and attribute (streams.py)

- **File**: `tap_rest_api_msdk/streams.py`.
- **Location**: `DynamicStream.__init__` parameter list; add `flatten_records: Optional[bool] = False` (e.g. after `store_raw_json_message`).
- **Docstring**: Document the new parameter (see documentation.md).
- **Body**: After `self.store_raw_json_message = store_raw_json_message`, add `self.flatten_records = flatten_records`.

### Step 5: post_process() branch (streams.py)

- **File**: `tap_rest_api_msdk/streams.py`.
- **Location**: `post_process()` method (lines 589–605).
- **Change**: Replace the single `return flatten_json(...)` with:
  - If `self.flatten_records`: return `flatten_json(row, self.except_keys, self.store_raw_json_message)`.
  - Else: return `row` unchanged.

## Files modified

| File | Changes |
|------|---------|
| `tap_rest_api_msdk/tap.py` | New property in common_properties; resolve flatten_records in discover_streams; pass to get_schema and DynamicStream; get_schema parameter and conditional flatten in loop. |
| `tap_rest_api_msdk/streams.py` | New __init__ parameter and attribute; conditional in post_process. |

## Dependency injection

- No new non-deterministic or external dependencies. `flatten_records` is read from config (deterministic per run) and passed explicitly into `DynamicStream` and `get_schema()`. No new injectable dependencies.

## Implementation dependencies

- Step 1 must be done before Step 2 (config must exist to be read).
- Step 2 depends on Step 3 (get_schema must accept the parameter).
- Step 4 must be done before Step 5 (stream must have the attribute).
- Tests (testing.md) should be added/updated so they fail before Steps 3 and 5 and pass after.
