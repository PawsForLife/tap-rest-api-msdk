# Dependencies — Optional Flatten Config

## External dependencies

- **None.** No new third-party packages or version changes. The feature uses existing `genson.SchemaBuilder.add_object()` (supports nested dicts), `tap_rest_api_msdk.utils.flatten_json`, and Singer SDK types/config.

## Internal dependencies

- **tap_rest_api_msdk.tap**: Depends on `streams.DynamicStream` (adds one constructor argument) and `utils.flatten_json` (unchanged; call site conditional). No new internal modules.
- **tap_rest_api_msdk.streams**: Depends on `utils.flatten_json` (unchanged; call site conditional). No new imports.

## System and environment

- No new environment variables or system requirements. Python 3.12+, existing venv and `uv` usage unchanged (see AI_CONTEXT_QUICK_REFERENCE.md).

## Configuration

- **New config key**: `flatten_records` (boolean, default `false`). Top-level and stream-level; stream overrides top-level. No new files; key is added to the existing JSON schema in `tap.py` (`common_properties`). Sample config and meltano.yml can be updated in documentation (see documentation.md).
