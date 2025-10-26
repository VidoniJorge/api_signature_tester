from etl.etl_source_data import LoaderData, ETLDataProcess
from etl.etl_csv import LoaderCsv
from test.test_endpoint import test_endpoint
from report.markdown_report_generator import MarkdownReportGenerator
from report.html_report_genetaror import HTMLReportGenerator


def load_test_cases(etl: LoaderData) -> ETLDataProcess:
    return etl.load_data()

def main():
    test_cases = load_test_cases(LoaderCsv("src/request.csv"))
    results_tests = []
    for test_case in test_cases.get_rest_data():
        results_tests.append(
            test_endpoint(test_case.source, test_case.new)
        )
    
    reportGenerator = MarkdownReportGenerator()
    reportGenerator.generate(results_tests, 'reports/comparisons_report.md')
    re = HTMLReportGenerator()
    re.generate(results_tests, 'reports/comparisons_report.html')


if __name__ == "__main__":
    main()    



