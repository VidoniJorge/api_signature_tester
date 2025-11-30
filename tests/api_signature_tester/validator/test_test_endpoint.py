from unittest.mock import Mock

import pytest
import requests

from api_signature_tester.validator.test_endpoint import (
    EndpointData,
    _exetute_requests,
    _get_rest_function,
)


class FakeResponse:
    def __init__(self, status_code: int, json_data=None):
        self.status_code = status_code
        self._json_data = json_data

    def json(self):
        return self._json_data


def test__get_rest_function_mappings():
    # Correct functions mapping
    assert _get_rest_function("GET") is requests.get
    assert _get_rest_function("gEt") is requests.get  # case-insensitive
    assert _get_rest_function("POST") is requests.post
    assert _get_rest_function("head") is requests.head
    assert _get_rest_function("options") is requests.options


def test__get_rest_function_returns_none_for_unknown_methods():
    with pytest.raises(TypeError, match="Unknown HTTP method for new: PATCH"):
        assert _get_rest_function("PATCH") is TypeError

    with pytest.raises(TypeError, match="Unknown HTTP method for new: "):
        assert _get_rest_function("") is TypeError

    with pytest.raises(TypeError, match="Unknown HTTP method for new: RANDOM"):
        assert _get_rest_function("RANDOM") is TypeError


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

    r1, r2 = _exetute_requests(source, new)
    assert r1 is src_resp
    assert r2 is new_resp
    assert fake_get.call_count == 2
    fake_get.assert_any_call(
        url="http://src.test", params={"p": "1"}, headers={"h": "1"}
    )
    fake_get.assert_any_call(
        url="http://new.test", params={"p": "2"}, headers={"h": "2"}
    )
