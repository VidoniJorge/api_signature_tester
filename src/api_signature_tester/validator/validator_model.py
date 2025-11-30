from typing import Any


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
