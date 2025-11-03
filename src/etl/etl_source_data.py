from typing import Protocol

from test.test_endpoint import EndpointData


class TestData:
    def __init__(self, source: EndpointData, new: EndpointData):
        self._source = source
        self._new = new

    def get_source(self) -> EndpointData:
        return self._source

    def get_new(self) -> EndpointData:
        return self._new


class ETLDataProcess:
    def __init__(self):
        self._list_data: list[TestData] = []
        self._load_errors: list[str] = []

    def add_test_data(self, test_data: TestData) -> None:
        self._list_data.append(test_data)

    def add_load_error(self, error_message: str) -> None:
        self._load_errors.append(error_message)

    def get_rest_data(self) -> list[TestData]:
        return self._list_data

    def get_load_errors(self) -> list[str]:
        return self._load_errors


class LoaderData(Protocol):
    def load_data(self) -> ETLDataProcess: ...
