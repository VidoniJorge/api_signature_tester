from typing import Any


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


class TestEndpointModel:
    def __init__(
        self, source: EndpointData, new: EndpointData, test_path_json: str | None = None
    ):
        self._source = source
        self._new = new
        self._test_path_json = test_path_json

    def get_source(self) -> EndpointData:
        return self._source

    def get_new(self) -> EndpointData:
        return self._new

    def get_test_path_json(self) -> str | None:
        return self._test_path_json


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
