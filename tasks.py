import logging
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor, as_completed

from config import configure_logging
from external.client import YandexWeatherAPI
#from utils import get_url_by_city_name

configure_logging()
logger = logging.getLogger(__name__)


class DataFetchingTask:
    def __init__(self, cities: dict[str, str]):
        self.cities = cities

    def fetch_weather_data(self, city: str, url: str) -> dict[str, any]:
        try:
            data = YandexWeatherAPI.get_forecasting(url)
            logger.debug(f"Fetched data for {city}: {data}")
            return data
        except Exception as e:
            logging.error(f"Error fetching data for {city}: {e}")
            return {}

    def run(self) -> dict[str, dict[str, any]]:
        with ThreadPoolExecutor() as executor:
            future_to_city = {executor.submit(self.fetch_weather_data, city, url): city for city, url in self.cities.items()}
            weather_data = {}
            for future in as_completed(future_to_city):
                city = future_to_city[future]
                try:
                    data = future.result()
                    if data:
                        weather_data[city] = data
                except Exception as e:
                    logging.error(f"Error processing data for {city}: {e}")
        logger.debug(f"Weather data fetched: {weather_data}")
        return weather_data


class DataCalculationTask:
    def __init__(self, weather_data: dict[str, dict[str, any]]):
        self.weather_data = weather_data

    def calculate_city_weather(self, city: str, data: dict[str, any]) -> tuple[float, int]:
        total_temp = 0
        hours_count = 0
        no_precipitation_hours = 0

        for forecast in data.get("forecasts", []):
            for hour in forecast.get("hours", []):
                if 9 <= int(hour["hour"]) <= 19:
                    hours_count += 1
                    total_temp += hour["temp"]
                    if hour["condition"] in ["clear", "partly-cloudy", "cloudy"]:
                        no_precipitation_hours += 1

        if hours_count == 0:
            avg_temp = 0
        else:
            avg_temp = total_temp / hours_count

        logger.debug(f"Calculated weather for {city}: avg_temp={avg_temp}, no_precipitation_hours={no_precipitation_hours}")
        return avg_temp, no_precipitation_hours

    def run(self) -> dict[str, tuple[float, int]]:
        with ProcessPoolExecutor() as executor:
            future_to_city = {executor.submit(self.calculate_city_weather, city, data): city for city, data in self.weather_data.items()}
            city_weather = {}
            for future in as_completed(future_to_city):
                city = future_to_city[future]
                try:
                    city_weather[city] = future.result()
                except Exception as e:
                    logging.error(f"Error calculating weather for {city}: {e}")
        logger.debug(f"City weather calculated: {city_weather}")
        return city_weather


class DataAggregationTask:
    def __init__(self, city_weather: dict[str, tuple[float, int]]):
        self.city_weather = city_weather

    def run(self) -> list[dict[str, any]]:
        aggregated_data = []
        for city, data in self.city_weather.items():
            avg_temp, no_precipitation_hours = data
            aggregated_data.append({
                "city": city,
                "avg_temp": avg_temp,
                "no_precipitation_hours": no_precipitation_hours
            })
        logger.debug(f"Aggregated data: {aggregated_data}")
        return aggregated_data


class DataAnalyzingTask:
    def __init__(self, aggregated_data: list[dict[str, any]]):
        self.aggregated_data = aggregated_data

    def run(self) -> list[dict[str, any]]:
        max_temp = max(self.aggregated_data, key=lambda x: x["avg_temp"])["avg_temp"]
        max_no_precipitation_hours = max(self.aggregated_data, key=lambda x: x["no_precipitation_hours"])["no_precipitation_hours"]

        best_cities = [city for city in self.aggregated_data if
                       city["avg_temp"] == max_temp and city["no_precipitation_hours"] == max_no_precipitation_hours]

        if not best_cities:
            # Find cities with max avg_temp and max no_precipitation_hours separately
            cities_with_max_temp = [city for city in self.aggregated_data if city["avg_temp"] == max_temp]
            cities_with_max_no_precipitation_hours = [city for city in self.aggregated_data if city["no_precipitation_hours"] == max_no_precipitation_hours]

            logger.debug(f"Cities with max temp: {cities_with_max_temp}")
            logger.debug(f"Cities with max no precipitation hours: {cities_with_max_no_precipitation_hours}")

            best_cities = cities_with_max_temp + cities_with_max_no_precipitation_hours

        logger.debug(f"Best cities: {best_cities}")
        return best_cities
