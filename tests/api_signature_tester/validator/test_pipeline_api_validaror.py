import json
from typing import Any
from unittest.mock import Mock

import pytest
import requests
from requests.models import Response

from api_signature_tester.validator.pipeline_api_validaror import PipelineApiValidaror
from api_signature_tester.validator.validator_model import (
    EndpointData,
)


class FakePipelineApiValidaror(PipelineApiValidaror):
    def get_body_response(self, r1: Response, r2: Response) -> tuple[Any, Any]:
        raise NotImplementedError

    def compare_body(self, j1, j2) -> list[dict[str, Any]]:
        raise NotImplementedError


class FakeResponse:
    def __init__(self, status_code: int, json_data=None, raise_json: bool = False):
        self.status_code = status_code
        self._json_data = json_data
        self._raise_json = raise_json

    def json(self):
        if self._raise_json:
            # simulate a JSON decoding error
            raise json.JSONDecodeError("Expecting value", "", 0)
        return self._json_data


def test_find_http_status_code_no_change():
    r1 = FakeResponse(200, json_data={})
    r2 = FakeResponse(200, json_data={})

    pipeline = FakePipelineApiValidaror()
    result = pipeline.compare_status_code(r1, r2)
    assert result == {}


def test_find_http_status_code_change():
    r1 = FakeResponse(200, json_data={})
    r2 = FakeResponse(404, json_data={})

    pipeline = FakePipelineApiValidaror()
    result = pipeline.compare_status_code(r1, r2)
    assert "status_code" in result
    assert result["status_code"]["old_value"] == 200
    assert result["status_code"]["new_value"] == 404


def test_create_body_diff_structure():
    p = FakePipelineApiValidaror()

    diff = p.create_body_diff("Cambio", "root['a']", "1", "2")
    assert isinstance(diff, dict)
    assert set(diff.keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert diff["Tipo"] == "Cambio"
    assert diff["Ruta"] == "root['a']"
    assert diff["Valor anterior"] == "1"
    assert diff["Valor nuevo"] == "2"


def test__get_rest_function_mappings():
    p = FakePipelineApiValidaror()
    # Correct functions mapping
    assert p._get_rest_function("GET") is requests.get
    assert p._get_rest_function("gEt") is requests.get  # case-insensitive
    assert p._get_rest_function("POST") is requests.post
    assert p._get_rest_function("head") is requests.head
    assert p._get_rest_function("options") is requests.options


def test__get_rest_function_returns_none_for_unknown_methods():
    p = FakePipelineApiValidaror()
    with pytest.raises(TypeError, match="Unknown HTTP method for new: PATCH"):
        assert p._get_rest_function("PATCH") is TypeError

    with pytest.raises(TypeError, match="Unknown HTTP method for new: "):
        assert p._get_rest_function("") is TypeError

    with pytest.raises(TypeError, match="Unknown HTTP method for new: RANDOM"):
        assert p._get_rest_function("RANDOM") is TypeError


def test__exetute_requests_calls_correct_methods(monkeypatch):
    src_resp = FakeResponse(200, json_data={"a": 1})
    new_resp = FakeResponse(200, json_data={"a": 2})

    def side_effect(url=None, params=None, headers=None):
        if url == "http://src.test":
            return src_resp
        if url == "http://new.test":
            return new_resp
        raise AssertionError(f"Unexpected URL: {url}")

    fake_get = Mock(side_effect=side_effect)
    monkeypatch.setattr(requests, "get", fake_get)

    source = EndpointData(
        url="http://src.test",
        method="GET",
        params={"p": "1"},
        headers={"h": "1"},
    )
    new = EndpointData(
        url="http://new.test",
        method="GET",
        params={"p": "2"},
        headers={"h": "2"},
    )

    p = FakePipelineApiValidaror()
    r1, r2 = p._exetute_requests(source, new)
    assert r1 is src_resp
    assert r2 is new_resp
    assert fake_get.call_count == 2
    fake_get.assert_any_call(
        url="http://src.test", params={"p": "1"}, headers={"h": "1"}
    )
    fake_get.assert_any_call(
        url="http://new.test", params={"p": "2"}, headers={"h": "2"}
    )


def test_compare_responses_status_code_and_body():
    # different status codes and different bodies
    r1 = FakeResponse(200, json_data={"a": 1})
    r2 = FakeResponse(500, json_data={"a": 2})

    pipelline = FakePipelineApiValidaror()
    status_diff = pipelline.compare_status_code(r1, r2)
    # status diff present
    assert status_diff["status_code"]["old_value"] == 200
    assert status_diff["status_code"]["new_value"] == 500
