import json
from abc import ABC, abstractmethod
from typing import Any

import jmespath
from deepdiff import DeepDiff
from deepdiff.helper import SetOrdered
from requests.models import Response

from api_signature_tester.validator.validator_model import ComparationResult


class PipelineJsonApiValidartor(ABC):
    def execute(self, r1: Response, r2: Response) -> ComparationResult:
        compare_status_code_result = self.compare_status_code(r1, r2)

        body_all_diffs = []
        j1, j2 = self.get_body_response(r1, r2)
        compare_format_result = self.compare_format_body(j1, j2)
        body_all_diffs.extend(compare_format_result)

        if len(compare_format_result) == 0:
            compare_body_result = self.compare_body(j1, j2)
            body_all_diffs.extend(compare_body_result)

        respoinse_comparation_equals = True

        if compare_format_result is None or len(body_all_diffs) > 0:
            respoinse_comparation_equals = False

        return ComparationResult(
            respoinse_comparation_equals,
            compare_status_code_result.get("status_code", {}),
            body_all_diffs,
        )

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

    def compare_format_body(self, j1, j2) -> list[dict[str, Any]]:
        # Si alguna respuesta no es JSON, registramos el error y devolvemos
        # un ComparationResult
        if j1 is None or j2 is None:
            return [
                create_body_diff(
                    "format_error",
                    ".",
                    f"source_is_json {j1 is not None}",
                    f"new_is_json {j2 is not None}",
                )
            ]
        return []

    @abstractmethod
    def compare_body(self, j1, j2) -> list[dict[str, Any]]:
        raise NotImplementedError


class PipelineFullJsonApiValidator(PipelineJsonApiValidartor):
    def __init__(self):
        pass

    def get_body_response(self, r1: Response, r2: Response) -> tuple[Any, Any]:
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

        return j1, j2

    def compare_body(self, j1, j2) -> list[dict[str, Any]]:
        deep_diff_body = DeepDiff(j1, j2, ignore_order=True)
        diffs_body = []

        # Valores cambiados
        for path, change in deep_diff_body.get("values_changed", {}).items():
            diffs_body.append(
                create_body_diff(
                    "Cambio de valor", path, change["old_value"], change["new_value"]
                )
            )

        # Elementos añadidos
        for path, value in deep_diff_body.get("iterable_item_added", {}).items():
            diffs_body.append(create_body_diff("Elemento añadido", path, "", value))

        # Elementos eliminados
        for path, value in deep_diff_body.get("iterable_item_removed", {}).items():
            diffs_body.append(create_body_diff("Elemento eliminado", path, value, ""))

        # Nuevas claves añadidas
        added = deep_diff_body.get("dictionary_item_added", {})
        if isinstance(added, (set, list, tuple, SetOrdered)):
            # elementos como "root['newkey']" (sin valor).
            # usamos "" como value por defecto.
            iterator = ((path, "") for path in added)
            for path, value in iterator:
                diffs_body.append(create_body_diff("Clave añadida", path, "", value))

        # Claves eliminadas
        removed = deep_diff_body.get("dictionary_item_removed", {})
        if isinstance(removed, (set, list, tuple, SetOrdered)):
            # elementos como "root['newkey']" (sin valor).
            # usamos "" como value por defecto.
            iterator = ((path, "") for path in removed)
            for path, value in iterator:
                diffs_body.append(create_body_diff("Clave eliminada", path, "", value))

        return diffs_body


class PipelineJsonApiParcialValidator(PipelineFullJsonApiValidator):
    def __init__(self, path_to_validate: str):
        self._path_to_validate = path_to_validate

    def get_body_response(self, r1, r2):
        j1, j2 = super().get_body_response(r1, r2)
        if j1 is not None:
            j1 = jmespath.search(self._path_to_validate, j1)
        if j2 is not None:
            j2 = jmespath.search(self._path_to_validate, j2)
        return j1, j2


def create_body_diff(type: str, path: str, old_value: str, new_value: str) -> dict:
    return {
        "Tipo": type,
        "Ruta": path,
        "Valor anterior": old_value,
        "Valor nuevo": new_value,
    }
