# Task 03: Schema inference tests and get_schema branch

## Background

Schema inference must respect `flatten_records`: when true, flatten sample records then infer (current behaviour); when false, infer from raw nested records so inferred schema matches emitted record shape. This task adds the `get_schema(..., flatten_records=False)` parameter and branches in the inference loop. Task 01 must be complete.

**Dependencies:** Task 01 (config property). Discovery will pass `flatten_records` into `get_schema` in task 04.

## This Task

- **File:** `tap_rest_api_msdk/tap.py`.
- **get_schema() signature:** Add parameter `flatten_records: bool = False` to `get_schema(..., path, params, headers)` (e.g. after `headers`). Update docstring per documentation.md.
- **Body (inference loop):** In the loop over sample records (see implementation.md):
  - If `flatten_records`: keep current logic (`flat_record = flatten_json(record, except_keys, store_raw_json_message=False)`, `builder.add_object(flat_record)`).
  - Else: `builder.add_object(record)` (no flatten).
  - Keep existing `store_raw_json_message` / `_sdc_raw_json` handling in both branches (or once after record add, as today).

**Acceptance:** When `get_schema(..., flatten_records=True)` is called with nested payload, inferred schema has flattened-style keys; when `flatten_records=False`, schema has nested structure (e.g. `properties.customer.properties.id` or equivalent genson output).

## Testing Needed

- **TDD (tests first):**
  - **flatten_records true:** Mock GET response with nested payload; call code path that infers schema with `flatten_records=True`; assert inferred schema has flattened-style keys (e.g. root-level `customer_id`, not nested `customer.id`).
  - **flatten_records false:** Same nested payload; infer with `flatten_records=False`; assert schema has nested structure (e.g. `properties.customer.properties.id` or equivalent).
- **Location:** `tests/test_tap.py` if `get_schema` is unit-testable with a mock tap and config; otherwise integration-style with discovery + schema from API.
- **Black-box:** Assert on structure of inferred schema only.
