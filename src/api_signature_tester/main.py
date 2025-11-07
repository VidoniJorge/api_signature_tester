from api_signature_tester.etl.etl_csv import LoaderCsv
from api_signature_tester.etl.etl_source_data import ETLDataProcess, LoaderData
from api_signature_tester.report.html_report_genetaror import HTMLReportGenerator
from api_signature_tester.report.markdown_report_generator import (
    MarkdownReportGenerator,
)
from api_signature_tester.test.test_endpoint import test_endpoint


def load_test_cases(etl: LoaderData) -> ETLDataProcess:
    return etl.load_data()


def run():
    test_cases = load_test_cases(LoaderCsv("src/api_signature_tester/request.csv"))
    results_tests = []
    for test_case in test_cases.get_rest_data():
        results_tests.append(test_endpoint(test_case.get_source(), test_case.get_new()))

    reportGenerator = MarkdownReportGenerator()
    reportGenerator.generate(results_tests, "reports/comparisons_report.md")
    re = HTMLReportGenerator()
    re.generate(results_tests, "reports/comparisons_report.html")


if __name__ == "__main__":
    run()
