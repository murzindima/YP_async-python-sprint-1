import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from external.client import YandexWeatherAPI
from utils import get_url_by_city_name

logger = logging.getLogger(__name__)

class DataFetchingTask:
    def __init__(self, cities: dict[str, str]):
        self.cities = cities

    def fetch_weather_data(self, city: str) -> dict[str, any]:
        url = get_url_by_city_name(city)
        try:
            data = YandexWeatherAPI.get_forecasting(url)
            #logger.debug(f"Fetched data for {city}: {data}")
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {city}: {e}")
            return {}

    def run(self) -> dict[str, dict[str, any]]:
        with ThreadPoolExecutor() as executor:
            future_to_city = {executor.submit(self.fetch_weather_data, city): city for city in self.cities.keys()}
            weather_data = {}
            for future in as_completed(future_to_city):
                city = future_to_city[future]
                try:
                    data = future.result()
                    if data:
                        weather_data[city] = data
                except Exception as e:
                    logger.error(f"Error processing data for {city}: {e}")
        #logger.debug(f"Weather data fetched: {weather_data}")
        return weather_data

class DataCalculationTask:
    def __init__(self, weather_data: dict[str, dict[str, any]]):
        self.weather_data = weather_data

    def calculate_city_weather(self, city: str, data: dict[str, any]) -> dict:
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
                    if hour["condition"] in ["clear", "partly-cloudy", "cloudy", "overcast"]:
                        daily_no_precipitation_hours += 1

            if daily_hours_count > 0:
                avg_daily_temp = daily_temp / daily_hours_count
                daily_data.append({
                    "date": forecast["date"],
                    "avg_temp": int(avg_daily_temp),
                    "no_precipitation_hours": daily_no_precipitation_hours
                })
                total_temp += daily_temp
                total_hours_count += daily_hours_count
                total_no_precipitation_hours += daily_no_precipitation_hours

        avg_temp = int(total_temp / total_hours_count) if total_hours_count else 0

        result = {
            "city": city,
            "daily_data": daily_data,
            "avg_temp": avg_temp,
            "no_precipitation_hours": total_no_precipitation_hours
        }

        logger.debug(f"Calculated weather for {city}: {result}")
        return result

    def run(self) -> dict[str, dict]:
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
    def __init__(self, city_weather: dict[str, dict]):
        self.city_weather = city_weather

    def run(self) -> list[dict[str, any]]:
        aggregated_data = []
        for city, data in self.city_weather.items():
            aggregated_data.append(data)
        logger.debug(f"Aggregated data: {aggregated_data}")
        return aggregated_data

class DataAnalyzingTask:
    def __init__(self, aggregated_data: list[dict[str, any]]):
        self.aggregated_data = aggregated_data

    def run(self) -> list[dict[str, any]]:
        sorted_by_temp = sorted(self.aggregated_data, key=lambda x: x["avg_temp"], reverse=True)
        sorted_by_precipitation = sorted(self.aggregated_data, key=lambda x: x["no_precipitation_hours"], reverse=True)

        for rank, city in enumerate(sorted_by_temp):
            city["temp_rank"] = rank + 1
        for rank, city in enumerate(sorted_by_precipitation):
            city["precipitation_rank"] = rank + 1

        best_cities = sorted(self.aggregated_data, key=lambda x: (x["temp_rank"], x["precipitation_rank"]))

        for rank, city in enumerate(best_cities):
            city["rank"] = rank + 1

        best_cities = [city for city in best_cities if city["rank"] == 1]

        for city in self.aggregated_data:
            city.pop("temp_rank", None)
            city.pop("precipitation_rank", None)

        logger.debug(f"Best cities: {best_cities}")
        return best_cities
