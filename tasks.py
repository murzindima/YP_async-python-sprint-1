import json
import logging

import requests

from config import configure_logging
from external.client import YandexWeatherAPI
from utils import get_url_by_city_name

configure_logging()
logger = logging.getLogger(__name__)


class DataFetchingTask:
    def __init__(self, cities: list[str]):
        self.cities = cities

    @staticmethod
    def fetch_weather_data(city: str) -> dict:
        try:
            data_url = get_url_by_city_name(city)
            data = YandexWeatherAPI.get_forecasting(data_url)

            if not isinstance(data, dict):
                raise ValueError("Invalid JSON format: expected a dictionary")
            return data
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error fetching data for {city}: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error fetching data for {city}: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error fetching data for {city}: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"General error fetching data for {city}: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON for {city}: {e}")
        except ValueError as e:
            logger.error(f"Value error for {city}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred for {city}: {e}")
        return {}


class DataCalculationTask:
    pass


class DataAggregationTask:
    pass


class DataAnalyzingTask:
    pass
