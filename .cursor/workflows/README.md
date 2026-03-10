# Pipeline Workflows

Phase workflow definitions used by the feature and bug pipelines. The orchestrator commands (`feature-pipeline`, `bug-pipeline`) in `.cursor/commands/` invoke subagents (`/researcher`, `/architect`, `/debug-specialist`, `/task-decomposer`, `/implementer`, `/archivist`); each subagent executes the workflow in the corresponding file here. Do not invoke these workflow files directly—use `/feature-pipeline` or `/bug-pipeline` in Composer.

- **Archive (Phase 6/7)**: The `/archivist` subagent runs `6-archive-feature-summary.md` or `6-archive-bug-summary.md` to produce a single summary document; the pipeline then deletes the request and artifact folder so the archive holds only the summary.

Path conventions (e.g. `{features_dir}`, `{bugs_dir}`, `{archive_dir}`, `{context_docs_dir}`) are documented in [cursor/CONVENTIONS.md](../CONVENTIONS.md).
