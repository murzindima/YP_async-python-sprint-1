import pytest
from tasks import DataAggregationTask


@pytest.fixture
def city_weather():
    return {
        "MOSCOW": {
            "city": "MOSCOW",
            "avg_temp": 21,
            "no_precipitation_hours": 2,
            "daily_data": [
                {"date": "2022-05-26", "avg_temp": 21, "no_precipitation_hours": 2}
            ],
        }
    }


def test_aggregation(city_weather):
    task = DataAggregationTask(city_weather)
    result = task.run()

    assert len(result) == 1
    assert result[0]["city"] == "MOSCOW"
    assert result[0]["avg_temp"] == 21
    assert result[0]["no_precipitation_hours"] == 2
