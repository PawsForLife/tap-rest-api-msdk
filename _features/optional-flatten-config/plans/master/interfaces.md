# Interfaces — Optional Flatten Config

## Config (JSON schema)

- **Property**: `flatten_records` (boolean).
- **Location**: `tap_rest_api_msdk/tap.py`, inside `common_properties` (after `store_raw_json_message`), so it appears in both top-level and stream-level config.
- **Default**: `false`.
- **Description**: When true, flatten records and infer flattened schema (current behaviour). When false, preserve nested structure in records and inferred schema.

## TapRestApiMsdk

### discover_streams()

- **Resolve**: `flatten_records = stream.get("flatten_records", self.config.get("flatten_records", False))`.
- **Pass to get_schema**: When calling `self.get_schema(...)` for inference, add keyword argument `flatten_records=flatten_records`.
- **Pass to DynamicStream**: Add argument `flatten_records=flatten_records` to `DynamicStream(...)`.

### get_schema(..., flatten_records=False)

- **Signature**: Add optional parameter `flatten_records: bool = False` to existing `get_schema(records_path, except_keys, inference_records, path, params, headers)`.
- **Behaviour**:
  - If `flatten_records` is true: for each sample record, `flat_record = flatten_json(record, except_keys, store_raw_json_message=False)`; `builder.add_object(flat_record)`; if `self.config.get("store_raw_json_message")`, `builder.add_object({"_sdc_raw_json": {}})` (unchanged).
  - If `flatten_records` is false: for each sample record, `builder.add_object(record)` (no flatten); if `store_raw_json_message`, optionally add `_sdc_raw_json` to schema as today.
- **Returns**: Same as today (dict schema from `builder.to_schema()`).

## DynamicStream

### __init__(..., flatten_records=False)

- **New parameter**: `flatten_records: Optional[bool] = False`.
- **Storage**: `self.flatten_records = flatten_records` (after existing attributes, e.g. after `store_raw_json_message`).

### post_process(row, context=None)

- **Behaviour**:
  - If `self.flatten_records` is true: return `flatten_json(row, self.except_keys, self.store_raw_json_message)` (unchanged).
  - If `self.flatten_records` is false: return `row` unchanged (no `_sdc_raw_json` added in post_process when not flattening; see overview.md constraints).
- **Signature**: Unchanged (row, context); return type remains `Optional[dict]`.

## utils.flatten_json

- **Signature**: Unchanged. No new parameters or return type changes.
- **Contract**: Call sites in tap and streams invoke it only when the corresponding `flatten_records` is true.
