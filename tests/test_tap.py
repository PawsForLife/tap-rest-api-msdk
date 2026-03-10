import json

from tap_rest_api_msdk.tap import TapRestApiMsdk
from tests.test_streams import config, setup_api

with open("tests/schema.json", "r") as f:
    BASIC_SCHEMA = json.load(f)


def test_schema_inference(requests_mock):
    setup_api(requests_mock)

    stream0 = TapRestApiMsdk(config=config(), parse_env_config=True).discover_streams()[
        0
    ]

    assert stream0.schema == BASIC_SCHEMA


def test_schema_from_file():
    configs = config()
    configs["streams"][0]["schema"] = "tests/schema.json"

    s0 = TapRestApiMsdk(config=configs, parse_env_config=True).discover_streams()[0]

    assert s0.schema == BASIC_SCHEMA


def test_schema_from_object():
    configs = config()
    configs["streams"][0]["schema"] = BASIC_SCHEMA

    s0 = TapRestApiMsdk(config=configs, parse_env_config=True).discover_streams()[0]

    assert s0.schema == BASIC_SCHEMA


def test_config_schema_includes_flatten_records():
    """Assert the tap config schema exposes flatten_records with default false.

    This validates acceptance that the property exists in the schema (top-level
    and stream-level) before any behaviour uses it, so discovery/config
    validation and later tasks can rely on it.
    """
    schema = TapRestApiMsdk.config_jsonschema
    assert "properties" in schema
    assert "flatten_records" in schema["properties"]
    prop = schema["properties"]["flatten_records"]
    assert prop.get("default") is False
    type_val = prop.get("type")
    assert type_val == "boolean" or (
        isinstance(type_val, list) and "boolean" in type_val
    )


# Nested payload used by get_schema flatten_records tests. flatten_json produces
# customer_id, customer_name at root; without flatten, schema has customer.id, customer.name.
NESTED_RESPONSE = {"records": [{"customer": {"id": 1, "name": "a"}}]}


def test_get_schema_flatten_records_true(requests_mock):
    """Schema inference with flatten_records=True produces flattened property keys.

    Ensures the True branch matches current behaviour: sample records are flattened
    before genson inference, so inferred schema has root-level keys (e.g. customer_id)
    not nested (customer.properties.id).
    """
    setup_api(requests_mock, json_extras=NESTED_RESPONSE)
    tap = TapRestApiMsdk(config=config(), parse_env_config=True)
    inference_records = int(tap.config.get("num_inference_records", 50))
    schema = tap.get_schema(
        records_path="$.records[*]",
        except_keys=[],
        inference_records=inference_records,
        path="/path_test",
        params={},
        headers={},
        flatten_records=True,
    )
    assert "properties" in schema
    assert "customer_id" in schema["properties"]
    assert "customer_name" in schema["properties"]
    assert "customer" not in schema["properties"]


def test_get_schema_flatten_records_false(requests_mock):
    """Schema inference with flatten_records=False preserves nested structure.

    Ensures inferred schema matches emitted record shape when flattening is off:
    schema has customer.properties.id (and customer.properties.name) instead of
    root-level customer_id, customer_name.
    """
    setup_api(requests_mock, json_extras=NESTED_RESPONSE)
    tap = TapRestApiMsdk(config=config(), parse_env_config=True)
    inference_records = int(tap.config.get("num_inference_records", 50))
    schema = tap.get_schema(
        records_path="$.records[*]",
        except_keys=[],
        inference_records=inference_records,
        path="/path_test",
        params={},
        headers={},
        flatten_records=False,
    )
    assert "properties" in schema
    assert "customer" in schema["properties"]
    assert "properties" in schema["properties"]["customer"]
    assert "id" in schema["properties"]["customer"]["properties"]
    assert "name" in schema["properties"]["customer"]["properties"]


def test_multiple_streams(requests_mock):
    setup_api(requests_mock)
    setup_api(requests_mock, url_path="https://example.com/path_test2")
    configs = config({"records_path": "$.records[*]"})
    configs["streams"].append(
        {
            "name": "stream_name2",
            "path": "/path_test2",
            "primary_keys": ["key4", "key5"],
            "replication_key": "key6",
        }
    )

    streams = TapRestApiMsdk(config=configs, parse_env_config=True).discover_streams()

    assert streams[0].name == "stream_name"
    assert streams[0].records_path == "$.records[*]"
    assert streams[0].path == "/path_test"
    assert streams[0].primary_keys == ["key1", "key2"]
    assert streams[0].replication_key == "key3"
    assert streams[1].name == "stream_name2"
    assert streams[1].records_path == "$.records[*]"
    assert streams[1].path == "/path_test2"
    assert streams[1].primary_keys == ["key4", "key5"]
    assert streams[1].replication_key == "key6"
