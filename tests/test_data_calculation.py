import pytest
from tasks import DataCalculationTask


@pytest.fixture
def weather_data():
    return {
        "MOSCOW": {
            "forecasts": [
                {
                    "date": "2022-05-26",
                    "hours": [
                        {"hour": "10", "temp": 20, "condition": "clear"},
                        {"hour": "11", "temp": 22, "condition": "cloudy"},
                        {"hour": "12", "temp": 21, "condition": "rain"}
                    ]
                }
            ]
        }
    }


def test_calculate_city_weather(weather_data):
    task = DataCalculationTask(weather_data)
    result = task.calculate_city_weather("MOSCOW", weather_data["MOSCOW"])

    assert result["city"] == "MOSCOW"
    assert result["avg_temp"] == 21
    assert result["no_precipitation_hours"] == 2
    assert len(result["daily_data"]) == 1
    assert result["daily_data"][0]["avg_temp"] == 21
    assert result["daily_data"][0]["no_precipitation_hours"] == 2
