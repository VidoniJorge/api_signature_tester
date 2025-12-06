import logging
from abc import ABC, abstractmethod

from api_signature_tester.config import Settings
from api_signature_tester.etl.etl_csv import LoaderCsv
from api_signature_tester.etl.etl_source_data import ETLDataProcess, ETLProccess
from api_signature_tester.report.html_report_genetaror import HTMLReportGenerator
from api_signature_tester.report.markdown_report_generator import (
    MarkdownReportGenerator,
)
from api_signature_tester.validator.test_endpoint import test_endpoint


class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\033[37m",  # Gris
        logging.INFO: "\033[36m",  # Cyan
        logging.WARNING: "\033[33m",  # Amarillo
        logging.ERROR: "\033[31m",  # Rojo
        logging.CRITICAL: "\033[41m",  # Rojo fondo
    }

    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelno, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


class ApiSignatureTester(ABC):
    @abstractmethod
    def run(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def load_test_cases(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def execute_test_case(self, test_case):
        raise NotImplementedError

    @abstractmethod
    def generate_report(self, results_tests, **kwargs):
        raise NotImplementedError


class ApiSignatureTesterSynch(ApiSignatureTester):
    def run(self, **kwargs):
        """
        Main function to run the API signature tester.
        :param \*\*kwargs: Arbitrary keyword arguments containing input paths.
            input_csv_path (str): Path to the input CSV file.
            input_md_report_path (str): Path to the output Markdown report file.
            input_html_report_path (str): Path to the output HTML report file.
        Returns:
            None
        """
        logger.info("Starting API Signature Tester...")
        logger.debug(kwargs)
        test_cases = self.load_test_cases(input_csv_path=kwargs.get("input_csv_path"))
        results_tests = []

        for test_case in test_cases.get_rest_data():
            results_tests.append(self.execute_test_case(test_case))

        self.generate_report(
            results_tests,
            file_path_md=kwargs.get("input_md_report_path"),
            file_path_html=kwargs.get("input_html_report_path"),
        )
        logger.info("API Signature Tester finished.")

    @abstractmethod
    def load_test_cases(self, **kwargs):
        pass

    @abstractmethod
    def execute_test_case(self, test_case):
        pass

    @abstractmethod
    def generate_report(self, results_tests, **kwargs):
        pass


class ApiSignatureTesterSynchBase(ApiSignatureTesterSynch):
    """
    Implementación base de ApiSignatureTesterSynch.
    Proporciona métodos para cargar casos de prueba, ejecutar casos de prueba
    y generar informes.
    """

    def load_test_cases(self, **kwargs) -> ETLDataProcess:
        """
        Carga los casos de prueba desde un archivo CSV.
        :param \*\*kwargs: Arbitrary keyword arguments containing input paths.
            input_csv_path (str): Path to the input CSV file.
        Returns:
            ETLDataProcess: An instance of ETLDataProcess containing the
            loaded test cases.
        """

        csv_path_default = settings.get_properties("csv_path")
        csv_path_value = (
            csv_path_default
            if csv_path_default is not None
            else kwargs.get("input_csv_path")
        )

        if not isinstance(csv_path_value, str):
            raise ValueError("CSV path must be provided as a string")
        csv_path: str = csv_path_value

        etl: ETLProccess = LoaderCsv()
        return etl.load_data(csv_path)

    def execute_test_case(self, test_case):
        return test_endpoint(test_case.get_source(), test_case.get_new())

    def generate_report(self, results_tests, **kwargs):
        """
        Generate reports in Markdown and HTML formats.
        :param results_tests: List of TestResult objects containing test results.
        :param \*\*kwargs: Arbitrary keyword arguments containing output file paths.
            file_path_md (str): Path to the output Markdown report file.
            file_path_html (str): Path to the output HTML report file.
        Returns:
            None
        """
        default_md_path = settings.get_properties("report_md_path")
        default_html_path = settings.get_properties("report_html_path")

        md_path_value = (
            kwargs.get("file_path_md")
            if kwargs.get("file_path_md") is not None
            else default_md_path
        )
        html_path_value = (
            kwargs.get("file_path_html")
            if kwargs.get("file_path_html") is not None
            else default_html_path
        )

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


def run(**kwargs):
    ApiSignatureTesterSynchBase().run(**kwargs)


global settings
settings = Settings()
handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter("%(asctime)s [%(levelname)s] %(message)s"))
global logger
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


if __name__ == "__main__":
    input_csv_path = settings.get_properties("csv_path")
    input_md_report_path = settings.get_properties("report_md_path")
    input_html_report_path = settings.get_properties("report_html_path")
    run(
        input_csv_path=input_csv_path,
        input_md_report_path=input_md_report_path,
        input_html_report_path=input_html_report_path,
    )
    # run()
