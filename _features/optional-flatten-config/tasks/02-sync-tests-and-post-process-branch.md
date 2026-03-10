# Task 02: Sync tests and post_process branch (DynamicStream)

## Background

When `flatten_records` is false, sync must emit records unchanged (nested); when true, current behaviour (flatten in post_process). This task adds the DynamicStream constructor parameter and attribute, and branches in `post_process()`. Task 01 must be complete so the config property exists; discovery will pass the value in task 04.

**Dependencies:** Task 01 (config property). This task implements the stream-side interface and behaviour; discovery pass-through is task 04.

## This Task

- **File:** `tap_rest_api_msdk/streams.py`.
- **DynamicStream.__init__:** Add parameter `flatten_records: Optional[bool] = False` (e.g. after `store_raw_json_message`). Set `self.flatten_records = flatten_records`. Update docstring Args per documentation.md.
- **post_process():** Replace the single `return flatten_json(...)` with:
  - If `self.flatten_records`: return `flatten_json(row, self.except_keys, self.store_raw_json_message)`.
  - Else: return `row` unchanged.
- **Docstring:** In `post_process`, add a line that when `flatten_records` is True, returns `flatten_json(...)`; otherwise returns row unchanged (per interfaces.md).

**Acceptance:** With `flatten_records=True` (passed from tap in task 04), sync emits flattened records; with `False`, nested. For this task, tests can construct `DynamicStream(..., flatten_records=True/False)` directly to verify post_process behaviour without discovery.

## Testing Needed

- **TDD (tests first):**
  - **flatten_records true:** Build a stream with `flatten_records=True` (e.g. via tap with config or direct instantiation in test). Sync one stream with nested API response; assert emitted records have flattened keys (e.g. no nested `record["user"]["name"]`; flat key present).
  - **flatten_records false:** Same setup with `flatten_records=False`; assert records preserve nested structure (e.g. `record["user"]["name"]` present, no flattened `user_name`).
- **Location:** `tests/test_streams.py`; use existing helpers (`config()`, `setup_api`, `requests_mock`). See AI_CONTEXT_PATTERNS.md: “How do I test that sync returns the correct records for a stream?”
- **Black-box:** Assert on structure of returned records only; do not assert on call counts or log lines.
