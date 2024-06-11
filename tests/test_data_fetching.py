import pytest
from tasks import DataFetchingTask


@pytest.fixture
def cities():
    return {
        "MOSCOW": "https://code.s3.yandex.net/async-module/moscow-response.json",
        "PARIS": "https://code.s3.yandex.net/async-module/paris-response.json",
    }


def test_fetch_weather_data_success(mocker, cities):
    mock_response = {
        "forecasts": [
            {
                "date": "2022-05-26",
                "hours": [
                    {"hour": "10", "temp": 20, "condition": "clear"},
                    {"hour": "11", "temp": 22, "condition": "cloudy"},
                ],
            }
        ]
    }

    mocker.patch(
        "external.client.YandexWeatherAPI.get_forecasting", return_value=mock_response
    )

    task = DataFetchingTask(cities)
    result = task.run()

    assert "MOSCOW" in result
    assert "PARIS" in result
    assert result["MOSCOW"] == mock_response
    assert result["PARIS"] == mock_response
