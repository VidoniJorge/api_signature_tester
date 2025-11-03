import pytest

from etl.etl_csv import LoaderCsv
from etl.etl_source_data import ETLDataProcess


@pytest.fixture
def temp_csv(tmp_path):
    csv_content = """url_source,method_source,params_source,headers_source,url_new,\
        method_new,params_new,headers_new
http://api.test/v1,GET,param1=value1&param2=value2,header1=value1,http://api.test/v2,POST,param3=value3,header2=value2
http://api.test/v1/users,POST,,,http://api.test/v2/users,GET,,"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(csv_content)
    return str(csv_file)


@pytest.fixture
def temp_csv_invalid(tmp_path):
    csv_content = """url_source,method_source
http://api.test/v1,GET"""
    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text(csv_content)
    return str(csv_file)


def test_load_data_success(temp_csv):
    # Given
    loader = LoaderCsv(temp_csv)

    # When
    result = loader.load_data()

    # Then
    assert isinstance(result, ETLDataProcess)
    assert len(result.get_rest_data()) == 2
    assert len(result.get_load_errors()) == 0

    # Verificar primera fila
    first_test = result.get_rest_data()[0]
    assert first_test.get_source().get_url() == "http://api.test/v1"
    assert first_test.get_source().get_method() == "GET"
    assert first_test.get_source().get_params() == {
        "param1": "value1",
        "param2": "value2",
    }
    assert first_test.get_source().get_headers() == {"header1": "value1"}

    assert first_test.get_new().get_url() == "http://api.test/v2"
    assert first_test.get_new().get_method() == "POST"
    assert first_test.get_new().get_params() == {"param3": "value3"}
    assert first_test.get_new().get_headers() == {"header2": "value2"}

    # Verificar segunda fila (campos vacíos)
    second_test = result.get_rest_data()[1]
    assert second_test.get_source().get_url() == "http://api.test/v1/users"
    assert second_test.get_source().get_method() == "POST"
    assert second_test.get_source().get_params() == {}
    assert second_test.get_source().get_headers() == {}


def test_load_data_file_not_found():
    pass
    # Given
    loader = LoaderCsv("csv_no_exist.csv")

    # When/Then
    with pytest.raises(FileNotFoundError):
        loader.load_data()


def test_load_data_invalid_format(temp_csv_invalid):
    pass
    # Given
    loader = LoaderCsv(temp_csv_invalid)

    # When
    result = loader.load_data()

    # Then
    assert isinstance(result, ETLDataProcess)
    assert len(result.get_rest_data()) == 0
    assert len(result.get_load_errors()) == 1
    assert "Error processing row 2" in result.get_load_errors()[0]


def test_empty_csv(tmp_path):
    pass
    # Given
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text(
        "url_source,method_source,params_source,headers_source,url_new,method_new,params_new,headers_new"
    )
    loader = LoaderCsv(str(csv_file))

    # When
    result = loader.load_data()

    # Then
    assert isinstance(result, ETLDataProcess)
    assert len(result.get_rest_data()) == 0
    assert len(result.get_load_errors()) == 0
