import json

import pytest

from api_signature_tester.validator.test_endpoint import (
    ComparationResult,
    _compare_responses,
    _create_body_diff,
    _find_http_status_code,
)


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

    result = _find_http_status_code(r1, r2)
    assert result == {}


def test_find_http_status_code_change():
    r1 = FakeResponse(200, json_data={})
    r2 = FakeResponse(404, json_data={})

    result = _find_http_status_code(r1, r2)
    assert "status_code" in result
    assert result["status_code"]["old_value"] == 200
    assert result["status_code"]["new_value"] == 404


def test_create_body_diff_structure():
    diff = _create_body_diff("Cambio", "root['a']", "1", "2")
    assert isinstance(diff, dict)
    assert set(diff.keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert diff["Tipo"] == "Cambio"
    assert diff["Ruta"] == "root['a']"
    assert diff["Valor anterior"] == "1"
    assert diff["Valor nuevo"] == "2"


cases = [
    (None, {"a": 1}, "source_is_json False", "new_is_json True"),
    ({"a": 1}, None, "source_is_json True", "new_is_json False"),
    (None, None, "source_is_json False", "new_is_json False"),
]
ids = ["source_not_json", "target_not_json", "both_not_json"]


@pytest.mark.parametrize(
    "source_response, target_response, source_expected, target_expected", cases, ids=ids
)
def test_compare_responses_non_json(
    source_response, target_response, source_expected, target_expected
):
    r1 = FakeResponse(200, json_data=source_response)
    r2 = FakeResponse(200, json_data=target_response)

    result = _compare_responses(r1, r2)
    assert isinstance(result, ComparationResult)
    assert result.is_equal() is False
    # When one response is not JSON, diff status_code should be empty (if status same)
    status_diff, body_diff = result.get_diffs()
    assert status_diff == {}
    assert set(body_diff[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    print(body_diff)
    assert body_diff[0]["Tipo"] == "format_error"
    assert body_diff[0]["Ruta"] == "."
    assert body_diff[0]["Valor anterior"] == source_expected
    assert body_diff[0]["Valor nuevo"] == target_expected


def test_compare_responses_body_diff_values_change():
    r1 = FakeResponse(200, json_data={"a": 1, "b": [1, 2]})
    r2 = FakeResponse(200, json_data={"a": 2, "b": [1, 2]})

    result = _compare_responses(r1, r2)
    assert isinstance(result, ComparationResult)
    assert result.is_equal() is False
    status_diff, body_diff = result.get_diffs()
    # no status code change
    assert status_diff == {}
    # body_diff should contain at least one change describing the modified value
    assert isinstance(body_diff, list)
    assert len(body_diff) >= 1
    assert set(body_diff[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert body_diff[0]["Tipo"] == "Cambio de valor"


def test_compare_responses_body_diff_iterable_item_add():
    r1 = FakeResponse(200, json_data={"a": 1, "b": [1, 2]})
    r2 = FakeResponse(200, json_data={"a": 1, "b": [1, 2, 10]})

    result = _compare_responses(r1, r2)
    assert isinstance(result, ComparationResult)
    assert result.is_equal() is False
    status_diff, body_diff = result.get_diffs()
    # no status code change
    assert status_diff == {}
    # body_diff should contain at least one change describing the modified value
    assert isinstance(body_diff, list)
    assert len(body_diff) >= 1
    assert set(body_diff[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert body_diff[0]["Tipo"] == "Elemento añadido"


def test_compare_responses_body_diff_iterable_item_removed():
    r1 = FakeResponse(200, json_data={"a": 1, "b": [1, 2, 3]})
    r2 = FakeResponse(200, json_data={"a": 1, "b": [1, 2]})

    result = _compare_responses(r1, r2)
    assert isinstance(result, ComparationResult)
    assert result.is_equal() is False
    status_diff, body_diff = result.get_diffs()
    # no status code change
    assert status_diff == {}
    # body_diff should contain at least one change describing the modified value
    assert isinstance(body_diff, list)
    assert len(body_diff) >= 1
    assert set(body_diff[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert body_diff[0]["Tipo"] == "Elemento eliminado"


def test_compare_responses_body_diff_dictionary_item_add():
    r1 = FakeResponse(200, json_data={"a": 1, "b": [1, 2]})
    r2 = FakeResponse(200, json_data={"a": 1, "b": [1, 2], "c": [1, 2], "d": {"x": 10}})

    result = _compare_responses(r1, r2)
    assert isinstance(result, ComparationResult)
    assert result.is_equal() is False
    status_diff, body_diff = result.get_diffs()
    # no status code change
    assert status_diff == {}
    # body_diff should contain at least one change describing the modified value
    assert isinstance(body_diff, list)
    assert len(body_diff) == 2
    assert set(body_diff[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert body_diff[0]["Tipo"] == "Clave añadida"


def test_compare_responses_body_diff_dictionary_item_removed():
    r1 = FakeResponse(200, json_data={"a": 1, "b": [1, 2], "c": 3})
    r2 = FakeResponse(200, json_data={"a": 1, "b": [1, 2]})

    result = _compare_responses(r1, r2)
    assert isinstance(result, ComparationResult)
    assert result.is_equal() is False
    status_diff, body_diff = result.get_diffs()
    # no status code change
    assert status_diff == {}
    # body_diff should contain at least one change describing the modified value
    assert isinstance(body_diff, list)
    assert len(body_diff) == 1
    assert set(body_diff[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert body_diff[0]["Tipo"] == "Clave eliminada"


def test_compare_responses_status_code_and_body():
    # different status codes and different bodies
    r1 = FakeResponse(200, json_data={"a": 1})
    r2 = FakeResponse(500, json_data={"a": 2})

    result = _compare_responses(r1, r2)
    assert isinstance(result, ComparationResult)
    assert result.is_equal() is False
    status_diff, body_diff = result.get_diffs()
    # status diff present
    assert status_diff["old_value"] == 200
    assert status_diff["new_value"] == 500
    # body diff should be present because values differ
    assert isinstance(body_diff, list)
    assert len(body_diff) == 1
