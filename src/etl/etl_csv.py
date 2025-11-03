import csv

from etl.etl_source_data import ETLDataProcess, TestData
from test.test_endpoint import EndpointData


class LoaderCsv:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load_data(self) -> ETLDataProcess:
        etlData = ETLDataProcess()
        with open(self.file_path) as file:
            csv_reader = csv.reader(file)
            for index, row in enumerate(csv_reader):
                if index == 0:
                    continue  # Skip header row
                try:
                    source_data = EndpointData(
                        url=row[0],
                        method=row[1],
                        params={
                            k: v
                            for k, v in (
                                param.split("=") for param in row[2].split("&")
                            )
                        }
                        if row[2]
                        else {},
                        headers={
                            k: v
                            for k, v in (
                                header.split("=") for header in row[3].split("&")
                            )
                        }
                        if row[3]
                        else {},
                    )
                    new_data = EndpointData(
                        url=row[4],
                        method=row[5],
                        params={
                            k: v
                            for k, v in (
                                param.split("=") for param in row[6].split("&")
                            )
                        }
                        if row[6]
                        else {},
                        headers={
                            k: v
                            for k, v in (
                                header.split("=") for header in row[7].split("&")
                            )
                        }
                        if row[7]
                        else {},
                    )
                    etlData.add_test_data(
                        test_data=TestData(source=source_data, new=new_data)
                    )
                except Exception as e:
                    etlData.add_load_error(f"Error processing row {index + 1}: {e}")
        return etlData
