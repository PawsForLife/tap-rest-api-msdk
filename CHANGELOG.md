# Changelog

## [Unreleased]

### Added

- Config property `flatten_records` (boolean, default `false`) in tap and stream-level config schema for optional-flatten-config.
  - Plan: [01-add-flatten-records-config-property](_features/optional-flatten-config/plans/tasks/01-add-flatten-records-config-property.md)
  - Task: [01-add-flatten-records-config-property](_features/optional-flatten-config/tasks/01-add-flatten-records-config-property.md)
- DynamicStream `flatten_records` parameter and post_process branch: when true, records are flattened; when false, row returned unchanged. Sync tests for both paths (optional-flatten-config).
  - Plan: [02-sync-tests-and-post-process-branch](_features/optional-flatten-config/plans/tasks/02-sync-tests-and-post-process-branch.md)
  - Task: [02-sync-tests-and-post-process-branch](_features/optional-flatten-config/tasks/02-sync-tests-and-post-process-branch.md)
- Parameter `flatten_records` on `get_schema()` and branch in schema inference: when true, flatten sample records then infer; when false, infer from raw nested records.
  - Plan: [03-schema-inference-tests-and-get-schema-branch](_features/optional-flatten-config/plans/tasks/03-schema-inference-tests-and-get-schema-branch.md)
  - Task: [03-schema-inference-tests-and-get-schema-branch](_features/optional-flatten-config/tasks/03-schema-inference-tests-and-get-schema-branch.md)
