import requests

from api_signature_tester.validator.pipeline_json_api import (
    PipelineFullJsonApiValidator,
)
from api_signature_tester.validator.validator_model import ComparationResult


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

    response_source, response_new = _exetute_requests(source, new)

    p = PipelineFullJsonApiValidator()
    comparation_result = p.execute(response_source, response_new)

    return TestResult(source, new, comparation_result)


def _exetute_requests(
    source: EndpointData, new: EndpointData
) -> tuple[requests.Response, requests.Response]:
    response_source = get_rest_function(source.get_method())(
        url=source.get_url(), params=source.get_params(), headers=source.get_headers()
    )
    response_new = get_rest_function(new.get_method())(
        url=new.get_url(), params=new.get_params(), headers=new.get_headers()
    )
    return response_source, response_new
