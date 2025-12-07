import json

import pytest

from api_signature_tester.validator.pipeline_json_api import (
    PipelineFullJsonApiValidator,
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

    pipelline = PipelineFullJsonApiValidator()
    j1, j2 = pipelline.get_body_response(r1, r2)
    result = pipelline.compare_format_body(j1, j2)
    assert set(result[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert result[0]["Tipo"] == "format_error"
    assert result[0]["Ruta"] == "."
    assert result[0]["Valor anterior"] == source_expected
    assert result[0]["Valor nuevo"] == target_expected


def test_compare_responses_body_diff_values_change():
    r1 = FakeResponse(200, json_data={"a": 1, "b": [1, 2]})
    r2 = FakeResponse(200, json_data={"a": 2, "b": [1, 2]})
    pipelline = PipelineFullJsonApiValidator()
    j1, j2 = pipelline.get_body_response(r1, r2)
    result = pipelline.compare_body(j1, j2)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert set(result[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert result[0]["Tipo"] == "Cambio de valor"


def test_compare_responses_body_diff_iterable_item_add():
    r1 = FakeResponse(200, json_data={"a": 1, "b": [1, 2]})
    r2 = FakeResponse(200, json_data={"a": 1, "b": [1, 2, 10]})
    pipelline = PipelineFullJsonApiValidator()
    j1, j2 = pipelline.get_body_response(r1, r2)
    result = pipelline.compare_body(j1, j2)
    assert isinstance(result, list)
    assert len(result) >= 1
    assert set(result[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert result[0]["Tipo"] == "Elemento añadido"


def test_compare_responses_body_diff_iterable_item_removed():
    r1 = FakeResponse(200, json_data={"a": 1, "b": [1, 2, 3]})
    r2 = FakeResponse(200, json_data={"a": 1, "b": [1, 2]})

    pipelline = PipelineFullJsonApiValidator()
    j1, j2 = pipelline.get_body_response(r1, r2)
    body_diff = pipelline.compare_body(j1, j2)
    assert isinstance(body_diff, list)
    assert len(body_diff) >= 1
    assert set(body_diff[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert body_diff[0]["Tipo"] == "Elemento eliminado"


def test_compare_responses_body_diff_dictionary_item_add():
    r1 = FakeResponse(200, json_data={"a": 1, "b": [1, 2]})
    r2 = FakeResponse(200, json_data={"a": 1, "b": [1, 2], "c": [1, 2], "d": {"x": 10}})

    pipelline = PipelineFullJsonApiValidator()
    j1, j2 = pipelline.get_body_response(r1, r2)
    body_diff = pipelline.compare_body(j1, j2)
    assert isinstance(body_diff, list)
    assert len(body_diff) == 2
    assert set(body_diff[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert body_diff[0]["Tipo"] == "Clave añadida"


def test_compare_responses_body_diff_dictionary_item_removed():
    r1 = FakeResponse(200, json_data={"a": 1, "b": [1, 2], "c": 3})
    r2 = FakeResponse(200, json_data={"a": 1, "b": [1, 2]})

    pipelline = PipelineFullJsonApiValidator()
    j1, j2 = pipelline.get_body_response(r1, r2)
    body_diff = pipelline.compare_body(j1, j2)
    assert isinstance(body_diff, list)
    assert len(body_diff) == 1
    assert set(body_diff[0].keys()) == {"Tipo", "Ruta", "Valor anterior", "Valor nuevo"}
    assert body_diff[0]["Tipo"] == "Clave eliminada"
