# Documentation — Optional Flatten Config

## Code documentation

- **tap.py — new property**: In `common_properties`, the `flatten_records` property description is in the schema (see interfaces.md). No separate docstring beyond the `description` string.
- **tap.py — get_schema**: In the docstring for `get_schema(...)`, add the new parameter: `flatten_records: When True, flatten sample records before inference; when False, infer from nested records. Default False.`
- **streams.py — DynamicStream.__init__**: In the docstring Args section, add: `flatten_records: When True, post_process flattens records; when False, records are emitted as-is. Default False.`
- **streams.py — post_process**: If the current docstring does not mention flattening, add a line: “When flatten_records is True, returns flatten_json(row, ...); otherwise returns row unchanged.” Keep docstrings concise (Google style per project rules).

## User-facing documentation

- **README.md**: In the configuration or options section, document `flatten_records` (optional, boolean, default false). One to two sentences: when true, records and schema are flattened (current behaviour); when false, nested structure is preserved.
- **config.sample.json**: Add an optional commented or uncommented key `"flatten_records": false` at top-level and/or inside a stream example, with a short comment if the format allows.

## Developer documentation

- **docs/AI_CONTEXT**: After implementation, if the tap’s config or behaviour is documented in AI_CONTEXT_REPOSITORY.md or AI_CONTEXT_QUICK_REFERENCE.md, add a mention of `flatten_records` where stream/tap config or post_process is described. Keep under 500 lines per file (content_length rule).

## What not to do

- Do not update code to match documentation; update documentation to match code (per project rules).
