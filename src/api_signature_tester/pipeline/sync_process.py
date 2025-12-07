import logging
from abc import ABC, abstractmethod

from api_signature_tester.config import Settings
from api_signature_tester.etl.etl_csv import LoaderCsv
from api_signature_tester.etl.etl_source_data import ETLDataProcess, ETLProccess
from api_signature_tester.report.html_report_genetaror import HTMLReportGenerator
from api_signature_tester.report.markdown_report_generator import (
    MarkdownReportGenerator,
)
from api_signature_tester.validator.pipeline_api_validaror import PipelineApiValidaror
from api_signature_tester.validator.validator_model import TestEndpointModel, TestResult


class ApiSignatureTesterSynch(ABC):
    def __init__(
        self,
        pipeline: PipelineApiValidaror,
        logger: logging.Logger,
        settings: Settings,
        input_csv_path: str | None = None,
        input_md_report_path: str | None = None,
        input_html_report_path: str | None = None,
    ):
        self._pipeline = pipeline
        self._logger = logger
        self._settings = settings
        self._input_csv_path = input_csv_path
        self._input_md_report_path = input_md_report_path
        self._input_html_report_path = input_html_report_path

    def execute(self):
        self._logger.info("Starting API Signature Tester...")

        test_cases = self.load_test_cases()
        results_tests = []

        for test_case in test_cases.get_rest_data():
            results_tests.append(self.execute_test_case(test_case))

        self.generate_report(results_tests)

        self._logger.info("API Signature Tester finished.")

    def get_input_csv_path(self) -> str:
        return str(
            self._input_csv_path
            if self._input_csv_path is not None
            else self._settings.get_properties("csv_path")
        )

    def get_input_md_report_path(self) -> str:
        return str(
            self._input_md_report_path
            if self._input_md_report_path is not None
            else self._settings.get_properties("report_md_path")
        )

    def get_input_html_report_path(self) -> str:
        return str(
            self._input_html_report_path
            if self._input_html_report_path is not None
            else self._settings.get_properties("report_html_path")
        )

    @abstractmethod
    def load_test_cases(self) -> ETLDataProcess:
        pass

    @abstractmethod
    def execute_test_case(self, test_case: TestEndpointModel) -> TestResult:
        pass

    @abstractmethod
    def generate_report(self, results_tests):
        pass


class ApiSignatureTesterSynchBase(ApiSignatureTesterSynch):
    """
    Implementación base de ApiSignatureTesterSynch.
    Proporciona métodos para cargar casos de prueba, ejecutar casos de prueba
    y generar informes.
    """

    def __init__(
        self,
        pipeline: PipelineApiValidaror,
        logger: logging.Logger,
        settings: Settings,
        input_csv_path: str | None = None,
        input_md_report_path: str | None = None,
        input_html_report_path: str | None = None,
    ):
        super().__init__(
            pipeline,
            logger,
            settings,
            input_csv_path,
            input_md_report_path,
            input_html_report_path,
        )

    def load_test_cases(self) -> ETLDataProcess:
        csv_path_value = self.get_input_csv_path()

        if not isinstance(csv_path_value, str):
            raise ValueError("CSV path must be provided as a string")
        csv_path: str = csv_path_value

        etl: ETLProccess = LoaderCsv()
        return etl.load_data(csv_path)

    def execute_test_case(self, test_case: TestEndpointModel) -> TestResult:
        return self._pipeline.execute(test_case.get_source(), test_case.get_new())

    def generate_report(self, results_tests):
        md_path_value = self.get_input_md_report_path()
        html_path_value = self.get_input_html_report_path()

        if not isinstance(md_path_value, str):
            raise ValueError("Markdown report path must be a string")
        if not isinstance(html_path_value, str):
            raise ValueError("HTML report path must be a string")

        md_path: str = md_path_value
        html_path: str = html_path_value

        reportGenerator = MarkdownReportGenerator()
        reportGenerator.generate(results_tests, md_path)
        re = HTMLReportGenerator()
        re.generate(results_tests, html_path)
