import requests
import json
from deepdiff import DeepDiff

class EndpointData:
    def __init__(self, url: str, method: str, params: dict[str, str], headers: dict[str, str]):
        self.url = url
        self.method = method
        self.params = params
        self.headers = headers

class ComparationResult:
    def __init__(self, are_equal: bool, diff_status_code: dict, diff_body: list):
        self._are_equal = are_equal
        self._diff_status_code = diff_status_code
        self._diff_body = diff_body
    
    def is_equal(self) -> bool:
        return self._are_equal
    
    def get_diffs(self) -> dict:
        return self._diff_status_code, self._diff_body
    
    def get_diff_status_code(self) -> dict:
        return self._diff_status_code
    
    def get_diff_body(self) -> list:
        return self._diff_body

class TestResult:
    def __init__(self, source: EndpointData, new: EndpointData, comparation_result: ComparationResult):
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
        "options": requests.options
    }.get(method.lower())

def test_endpoint(source: EndpointData, new: EndpointData) -> TestResult:
    """
    Test the given endpoint function by making a request to the specified URL
    :param source: EndpointData object containing URL, method, params, headers
    :param new: EndpointData object containing URL, method, params, headers
    """
    
    response_source = get_rest_function(source.method)(url=source.url, params=source.params, headers=source.headers)
    response_new = get_rest_function(new.method)(url=new.url, params=new.params, headers=new.headers)
    
    comparation_result = _compare_responses(response_source, response_new)

    return TestResult(source, new, comparation_result)
    

def _compare_responses(r1, r2) -> ComparationResult:
    respoinse_comparation_equals = True
    
    diffs = {}

    if r1.status_code != r2.status_code:
        respoinse_comparation_equals = False
        diffs['status_code'] = {
            'old_value': r1.status_code, 
            'new_value': r2.status_code
            }

    try:
        j1, j2 = r1.json(), r2.json()
    except json.JSONDecodeError:
        diffs.append("Una de las respuestas no es JSON.")
        return diffs

    deep_diff_body = DeepDiff(j1, j2, ignore_order=True)
    #print(type(diff_body))
    
    diffs_body = []
    # Valores cambiados
    for path, change in deep_diff_body.get('values_changed', {}).items():
        diffs_body.append(_create_body_diff("Cambio de valor", path, change['old_value'], change['new_value']))
    
    # Elementos añadidos
    for path, value in deep_diff_body.get('iterable_item_added', {}).items():
        diffs_body.append(_create_body_diff("Elemento añadido", path, "", value))
    
    # Elementos eliminados
    for path, value in deep_diff_body.get('iterable_item_removed', {}).items():
        diffs_body.append(_create_body_diff("Elemento eliminado", path, value, ""))
    
    # Nuevas claves añadidas
    for path, value in deep_diff_body.get('dictionary_item_added', []):
        diffs_body.append(_create_body_diff("Clave añadida", path, "", value))
    # Claves eliminadas
    for path, value in deep_diff_body.get('dictionary_item_removed', []):
        diffs_body.append(_create_body_diff("Clave eliminada", path, value, ""))
    
    if len(diffs_body) > 0:
        respoinse_comparation_equals = False
        diffs['body'] = diffs_body
    
    return ComparationResult(respoinse_comparation_equals, diffs.get('status_code', {}), diffs.get('body', []))

def _create_body_diff(type: str, path: str, old_value: str, new_value: str) -> dict:
    return {
            "Tipo": type,
            "Ruta": path,
            "Valor anterior": old_value,
            "Valor nuevo": new_value
        }

