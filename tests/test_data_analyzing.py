import pytest
from tasks import DataAnalyzingTask


@pytest.fixture
def aggregated_data():
    return [
        {
            "city": "MOSCOW",
            "avg_temp": 21,
            "no_precipitation_hours": 2,
            "daily_data": [
                {"date": "2022-05-26", "avg_temp": 21, "no_precipitation_hours": 2}
            ]
        },
        {
            "city": "PARIS",
            "avg_temp": 25,
            "no_precipitation_hours": 3,
            "daily_data": [
                {"date": "2022-05-26", "avg_temp": 25, "no_precipitation_hours": 3}
            ]
        }
    ]


def test_analyze(aggregated_data):
    task = DataAnalyzingTask(aggregated_data)
    result = task.run()

    assert len(result) == 1
    assert result[0]["city"] == "PARIS"
    assert result[0]["avg_temp"] == 25
    assert result[0]["no_precipitation_hours"] == 3
    assert result[0]["rank"] == 1
