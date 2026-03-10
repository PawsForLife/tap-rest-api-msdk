# Cursor Path Conventions

Path placeholders used by agents, commands, and workflows in this folder. Defaults apply unless the project overrides them (e.g. in README or `.cursor/rules`).

## Placeholders

| Placeholder | Purpose | Default |
| ---------- | -------- | ------- |
| `{features_dir}` | Feature request docs and planning | `_features` |
| `{bugs_dir}` | Bug investigation and fix artifacts | `_bugs` |
| `{archive_dir}` | Completed feature/bug artifacts | `_archive` |
| `{context_docs_dir}` | AI/context documentation output | `docs/AI_CONTEXT` |
| `{scratchpad}` | Handoff file for pipeline phases | `.cursor/scratchpad.md` |

## Usage

- In agents, commands, and workflows: use these placeholders (or the default paths) so paths stay consistent and overridable.
- **Components/libraries**: use discovery-oriented language — e.g. "each major package or library in the repository", "affected component(s) as identified from the plan". Do not hardcode component names (e.g. `python_service/`, `src/`, `webview-ui/`). Discover components from repo layout (e.g. top-level packages or directories, or as documented in README).

## Overriding

To use different paths in a repo: document them in the project README or in `.cursor/rules`. Agents and commands should resolve placeholders using those conventions when present.
