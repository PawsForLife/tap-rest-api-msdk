# Changelog

## [Unreleased]

### Changed

- Workflow `5-plan-task-bug.md`: normalized `{task_file}` to mean filename without `.md`; paths use `{task_file}.md`; example and scratchpad text updated.
- Workflows and commands: applied same `{task_file}` convention across `5-plan-task-feature.md`, `implement-task-fix.md`, `implement-task-feature.md`, `bug-pipeline.md`, `feature-pipeline.md`, and `architect.md` (paths use `{task_file}.md`; examples and mv/changelog links use `.md`; "task file name without extension" in prerequisites and invocations).

## [1.5.0] - 2026-03-10

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
- Discovery resolves `flatten_records` per stream (stream overrides top-level) and passes it to `get_schema()` and `DynamicStream()`.
  - Plan: [04-resolve-and-pass-flatten-records-in-discovery](_features/optional-flatten-config/plans/tasks/04-resolve-and-pass-flatten-records-in-discovery.md)
  - Task: [04-resolve-and-pass-flatten-records-in-discovery](_features/optional-flatten-config/tasks/04-resolve-and-pass-flatten-records-in-discovery.md)
- Documentation and test alignment for default `flatten_records: false`: README, config.sample.json, and AI_CONTEXT updated to document `flatten_records`; existing tests pass with default off.
  - Plan: [05-update-existing-tests-and-documentation](_features/optional-flatten-config/plans/tasks/05-update-existing-tests-and-documentation.md)
  - Task: [05-update-existing-tests-and-documentation](_features/optional-flatten-config/tasks/05-update-existing-tests-and-documentation.md)
