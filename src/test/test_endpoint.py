import requests
import json
from deepdiff import DeepDiff

class EndpointData:
    def __init__(self, url: str, method: str, params: dict[str, str], headers: dict[str, str]):
        self.url = url
        self.method = method
        self.params = params
        self.headers = headers

def get_rest_function(method: str):
    return {
        "get": requests.get,
        "post": requests.post,
        "head": requests.head,
        "options": requests.options
    }.get(method.lower())

def test_endpoint(source: EndpointData, new: EndpointData):
    """
    Test the given endpoint function by making a request to the specified URL
    :param source: EndpointData object containing URL, method, params, headers
    :param new: EndpointData object containing URL, method, params, headers
    """
    
    response_source = get_rest_function(source.method)(url=source.url, params=source.params, headers=source.headers)
    response_new = get_rest_function(new.method)(url=new.url, params=new.params, headers=new.headers)
    
    compare_responses(response_source, response_new)
    

def compare_responses(r1, r2):
    diffs = []
    if r1.status_code != r2.status_code:
        diffs.append(f"Status code distinto: {r1.status_code} vs {r2.status_code}")

    try:
        j1, j2 = r1.json(), r2.json()
    except json.JSONDecodeError:
        diffs.append("Una de las respuestas no es JSON.")
        return diffs

    diff = DeepDiff(j1, j2, ignore_order=True)
    for key, value in diff.items():
        print(f"error {key}: {value}")
    # Opcional: comparar tipos o valores si hace falta
    
    return diffs