import json
from typing import Any

import requests
from deepdiff import DeepDiff


class EndpointData:
    def __init__(
        self, url: str, method: str, params: dict[str, str], headers: dict[str, str]
    ):
        self._url = url
        self._method = method
        self._params = params
        self._headers = headers

    def get_url(self) -> str:
        return self._url

    def get_method(self) -> str:
        return self._method

    def get_params(self) -> dict[str, str]:
        return self._params

    def get_headers(self) -> dict[str, str]:
        return self._headers


class ComparationResult:
    def __init__(
        self,
        are_equal: bool,
        diff_status_code: dict[str, Any],
        diff_body: list[dict[str, Any]],
    ):
        self._are_equal = are_equal
        self._diff_status_code = diff_status_code
        self._diff_body = diff_body

    def is_equal(self) -> bool:
        return self._are_equal

    def get_diffs(self) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Devuelve una tupla (diff_status_code, diff_body).

        - diff_status_code: dict con cambios en código de estado
        - diff_body: lista de dicts con cambios en el body
        """
        return self._diff_status_code, self._diff_body

    def get_diff_status_code(self) -> dict[str, Any]:
        return self._diff_status_code

    def get_diff_body(self) -> list[dict[str, Any]]:
        return self._diff_body


class TestResult:
    def __init__(
        self,
        source: EndpointData,
        new: EndpointData,
        comparation_result: ComparationResult,
    ):
        self._source = source
        self._new = new
        self._comparation_result = comparation_result

    def get_source(self) -> EndpointData:
        return self._source

    def get_new(self) -> EndpointData:
        return self._new

    def get_comparation_result(self) -> ComparationResult:
        return self._comparation_result


def get_rest_function(method: str):
    return {
        "get": requests.get,
        "post": requests.post,
        "head": requests.head,
        "options": requests.options,
    }.get(method.lower())


def test_endpoint(source: EndpointData, new: EndpointData) -> TestResult:
    """
    Test the given endpoint function by making a request to the specified URL
    :param source: EndpointData object containing URL, method, params, headers
    :param new: EndpointData object containing URL, method, params, headers
    """

    response_source = get_rest_function(source.get_method())(
        url=source.get_url(), params=source.get_params(), headers=source.get_headers()
    )
    response_new = get_rest_function(new.get_method())(
        url=new.get_url(), params=new.get_params(), headers=new.get_headers()
    )

    comparation_result = _compare_responses(response_source, response_new)

    return TestResult(source, new, comparation_result)


def _compare_responses(r1, r2) -> ComparationResult:
    respoinse_comparation_equals = True

    diffs = {}

    if r1.status_code != r2.status_code:
        respoinse_comparation_equals = False
        diffs["status_code"] = {
            "old_value": r1.status_code,
            "new_value": r2.status_code,
        }

    # Intentamos parsear ambas respuestas a JSON; si fallan, las marcamos como None
    j1 = None
    j2 = None
    try:
        j1 = r1.json()
    except json.JSONDecodeError:
        j1 = None

    try:
        j2 = r2.json()
    except json.JSONDecodeError:
        j2 = None

    # Si alguna respuesta no es JSON, registramos el error y devolvemos
    # un ComparationResult
    if j1 is None or j2 is None:
        respoinse_comparation_equals = False
        diffs["internal-error"] = {
            "message": "Una de las respuestas no es JSON.",
            "source_is_json": j1 is not None,
            "new_is_json": j2 is not None,
        }
        return ComparationResult(
            respoinse_comparation_equals,
            diffs.get("status_code", {}),
            [],
        )

    deep_diff_body = DeepDiff(j1, j2, ignore_order=True)
    # print(type(diff_body))

    diffs_body = []
    # Valores cambiados
    for path, change in deep_diff_body.get("values_changed", {}).items():
        diffs_body.append(
            _create_body_diff(
                "Cambio de valor", path, change["old_value"], change["new_value"]
            )
        )

    # Elementos añadidos
    for path, value in deep_diff_body.get("iterable_item_added", {}).items():
        diffs_body.append(_create_body_diff("Elemento añadido", path, "", value))

    # Elementos eliminados
    for path, value in deep_diff_body.get("iterable_item_removed", {}).items():
        diffs_body.append(_create_body_diff("Elemento eliminado", path, value, ""))

    # Nuevas claves añadidas
    for path, value in deep_diff_body.get("dictionary_item_added", []):
        diffs_body.append(_create_body_diff("Clave añadida", path, "", value))
    # Claves eliminadas
    for path, value in deep_diff_body.get("dictionary_item_removed", []):
        diffs_body.append(_create_body_diff("Clave eliminada", path, value, ""))

    if len(diffs_body) > 0:
        respoinse_comparation_equals = False

    return ComparationResult(
        respoinse_comparation_equals,
        diffs.get("status_code", {}),
        diffs_body,
    )


def _create_body_diff(type: str, path: str, old_value: str, new_value: str) -> dict:
    return {
        "Tipo": type,
        "Ruta": path,
        "Valor anterior": old_value,
        "Valor nuevo": new_value,
    }
