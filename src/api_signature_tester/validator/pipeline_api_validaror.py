from abc import ABC, abstractmethod
from typing import Any

import requests
from requests.models import Response

from api_signature_tester.validator.validator_model import (
    ComparationResult,
    EndpointData,
    TestResult,
)


class PipelineApiValidaror(ABC):
    def execute(self, source: EndpointData, new: EndpointData) -> TestResult:
        """
        Test the given endpoint function by making a request to the specified URL
        :param source: EndpointData object containing URL, method, params, headers
        :param new: EndpointData object containing URL, method, params, headers
        """
        response_source, response_new = self._exetute_requests(source, new)

        compare_status_code_result = self.compare_status_code(
            response_source, response_new
        )

        body_all_diffs = []
        j1, j2 = self.get_body_response(response_source, response_new)
        compare_format_result = self.compare_format_body(j1, j2)
        body_all_diffs.extend(compare_format_result)

        if len(compare_format_result) == 0:
            compare_body_result = self.compare_body(j1, j2)
            body_all_diffs.extend(compare_body_result)

        respoinse_comparation_equals = True

        if compare_format_result is None or len(body_all_diffs) > 0:
            respoinse_comparation_equals = False

        result = ComparationResult(
            respoinse_comparation_equals,
            compare_status_code_result.get("status_code", {}),
            body_all_diffs,
        )

        return TestResult(source, new, result)

    def _exetute_requests(
        self, source: EndpointData, new: EndpointData
    ) -> tuple[requests.Response, requests.Response]:
        """
        Docstring para _exetute_requests
        :param source: Descripción
        :type source: EndpointData
        :param new: Descripción
        :type new: EndpointData
        :return: Descripción
        :rtype: tuple[Response, Response]
        """
        response_source = self._get_rest_function(source.get_method())(
            url=source.get_url(),
            params=source.get_params(),
            headers=source.get_headers(),
        )
        response_new = self._get_rest_function(new.get_method())(
            url=new.get_url(), params=new.get_params(), headers=new.get_headers()
        )
        return response_source, response_new

    def _get_rest_function(self, method: str):
        """
        Docstring para _get_rest_function

        :param method: Descripción
        :type method: str
        """
        result = {
            "get": requests.get,
            "post": requests.post,
            "head": requests.head,
            "options": requests.options,
        }.get(method.lower())

        if result is None:
            raise TypeError(f"Unknown HTTP method for new: {method}")

        return result

    def compare_status_code(self, r1: Response, r2: Response) -> dict[str, Any]:
        """
        Devuelve un dict con la diferencia del status code o un dict
        vacío si no hay cambios.
        """
        if r1.status_code != r2.status_code:
            return {
                "status_code": {
                    "old_value": r1.status_code,
                    "new_value": r2.status_code,
                }
            }

        return {}

    @abstractmethod
    def get_body_response(self, r1: Response, r2: Response) -> tuple[Any, Any]:
        raise NotImplementedError

    @abstractmethod
    def compare_body(self, j1, j2) -> list[dict[str, Any]]:
        raise NotImplementedError

    def compare_format_body(self, j1, j2) -> list[dict[str, Any]]:
        # Si alguna respuesta no es JSON, registramos el error y devolvemos
        # un ComparationResult
        if j1 is None or j2 is None:
            return [
                self.create_body_diff(
                    "format_error",
                    ".",
                    f"source_is_json {j1 is not None}",
                    f"new_is_json {j2 is not None}",
                )
            ]
        return []

    def create_body_diff(
        self, type: str, path: str, old_value: str, new_value: str
    ) -> dict:
        return {
            "Tipo": type,
            "Ruta": path,
            "Valor anterior": old_value,
            "Valor nuevo": new_value,
        }
