import json
from typing import Any

import jmespath
from deepdiff import DeepDiff
from deepdiff.helper import SetOrdered
from requests.models import Response

from api_signature_tester.validator.pipeline_api_validaror import PipelineApiValidaror


class PipelineFullJsonApiValidator(PipelineApiValidaror):
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
                self.create_body_diff(
                    "Cambio de valor", path, change["old_value"], change["new_value"]
                )
            )

        # Elementos añadidos
        for path, value in deep_diff_body.get("iterable_item_added", {}).items():
            diffs_body.append(
                self.create_body_diff("Elemento añadido", path, "", value)
            )

        # Elementos eliminados
        for path, value in deep_diff_body.get("iterable_item_removed", {}).items():
            diffs_body.append(
                self.create_body_diff("Elemento eliminado", path, value, "")
            )

        # Nuevas claves añadidas
        added = deep_diff_body.get("dictionary_item_added", {})
        if isinstance(added, (set, list, tuple, SetOrdered)):
            # elementos como "root['newkey']" (sin valor).
            # usamos "" como value por defecto.
            iterator = ((path, "") for path in added)
            for path, value in iterator:
                diffs_body.append(
                    self.create_body_diff("Clave añadida", path, "", value)
                )

        # Claves eliminadas
        removed = deep_diff_body.get("dictionary_item_removed", {})
        if isinstance(removed, (set, list, tuple, SetOrdered)):
            # elementos como "root['newkey']" (sin valor).
            # usamos "" como value por defecto.
            iterator = ((path, "") for path in removed)
            for path, value in iterator:
                diffs_body.append(
                    self.create_body_diff("Clave eliminada", path, "", value)
                )

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
