import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import Any
from queue import Queue

from external.analyzer import INPUT_DAY_SUITABLE_CONDITIONS
from external.client import YandexWeatherAPI
from utils import get_url_by_city_name

logger = logging.getLogger(__name__)


class DataFetchingTask:
    def __init__(self, cities: dict[str, str], output_queue: Queue):
        self.cities = cities
        self.output_queue = output_queue

    @staticmethod
    def fetch_weather_data(city: str) -> dict[str, Any]:
        url = get_url_by_city_name(city)
        try:
            data = YandexWeatherAPI.get_forecasting(url)
            logger.debug(f"Fetched data for {city}: {data}")
            return {city: data}
        except Exception as e:
            logger.error(f"Error fetching data for {city}: {e}")
            return {city: {}}

    def run(self) -> None:
        with ThreadPoolExecutor() as executor:
            future_to_city = {
                executor.submit(self.fetch_weather_data, city): city
                for city in self.cities.keys()
            }
            for future in as_completed(future_to_city):
                city_data = future.result()
                self.output_queue.put(city_data)
        logger.debug("All data fetched and put in the queue.")


class DataCalculationTask:
    def __init__(self, input_queue: Queue, output_queue: Queue):
        self.input_queue = input_queue
        self.output_queue = output_queue

    @staticmethod
    def calculate_city_weather(city: str, data: dict[str, Any]) -> dict:
        total_temp = 0
        total_hours_count = 0
        total_no_precipitation_hours = 0
        daily_data = []

        for forecast in data.get("forecasts", []):
            daily_temp = 0
            daily_hours_count = 0
            daily_no_precipitation_hours = 0
            for hour in forecast.get("hours", []):
                if 9 <= int(hour["hour"]) <= 19:
                    daily_hours_count += 1
                    daily_temp += hour["temp"]
                    if hour["condition"] in INPUT_DAY_SUITABLE_CONDITIONS:
                        daily_no_precipitation_hours += 1

            if daily_hours_count > 0:
                avg_daily_temp = daily_temp / daily_hours_count
                daily_data.append(
                    {
                        "date": forecast["date"],
                        "avg_temp": int(avg_daily_temp),
                        "no_precipitation_hours": daily_no_precipitation_hours,
                    }
                )
                total_temp += daily_temp
                total_hours_count += daily_hours_count
                total_no_precipitation_hours += daily_no_precipitation_hours

        avg_temp = int(total_temp / total_hours_count) if total_hours_count else 0

        result = {
            "city": city,
            "daily_data": daily_data,
            "avg_temp": avg_temp,
            "no_precipitation_hours": total_no_precipitation_hours,
        }

        logger.debug(f"Calculated weather for {city}: {result}")
        return result

    def run(self) -> None:
        with ProcessPoolExecutor() as executor:
            future_to_city = {}
            while True:
                city_data = self.input_queue.get()
                if city_data is None:
                    break
                for city, data in city_data.items():
                    if data:
                        future = executor.submit(self.calculate_city_weather, city, data)
                        future_to_city[future] = city

            for future in as_completed(future_to_city):
                city = future_to_city[future]
                try:
                    result = future.result()
                    self.output_queue.put(result)
                except Exception as e:
                    logging.error(f"Error calculating weather for {city}: {e}")
        logger.debug("All data calculated and put in the queue.")


class DataAggregationTask:
    def __init__(self, city_weather: list[dict]):
        self.city_weather = city_weather

    def run(self) -> list[dict[str, Any]]:
        aggregated_data = []
        for data in self.city_weather:
            aggregated_data.append(data)
        logger.debug(f"Aggregated data: {aggregated_data}")
        return aggregated_data


class DataAnalyzingTask:
    def __init__(self, aggregated_data: list[dict[str, Any]]):
        self.aggregated_data = aggregated_data

    def run(self) -> list[dict[str, Any]]:
        sorted_by_temp = sorted(
            self.aggregated_data, key=lambda x: x["avg_temp"], reverse=True
        )
        sorted_by_precipitation = sorted(
            self.aggregated_data,
            key=lambda x: x["no_precipitation_hours"],
            reverse=True,
        )

        for rank, city in enumerate(sorted_by_temp):
            city["temp_rank"] = rank + 1
        for rank, city in enumerate(sorted_by_precipitation):
            city["precipitation_rank"] = rank + 1

        best_cities = sorted(
            self.aggregated_data,
            key=lambda x: (x["temp_rank"], x["precipitation_rank"]),
        )

        for rank, city in enumerate(best_cities):
            city["rank"] = rank + 1

        best_cities = [city for city in best_cities if city["rank"] == 1]

        for city in self.aggregated_data:
            city.pop("temp_rank", None)
            city.pop("precipitation_rank", None)

        logger.debug(f"Best cities: {best_cities}")
        return best_cities
