from etl.etl_source_data import LoaderData, ETLDataProcess
from etl.etl_csv import LoaderCsv
from test.test_endpoint import test_endpoint

def load_test_cases(etl: LoaderData) -> ETLDataProcess:
    return etl.load_data()

def main():
    test_cases = load_test_cases(LoaderCsv("src/request.csv"))
    for test_case in test_cases.get_rest_data():
        result_test = test_endpoint(test_case.source, test_case.new)

if __name__ == "__main__":
    main()    



