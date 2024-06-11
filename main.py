import logging
from tasks import DataFetchingTask, DataCalculationTask, DataAggregationTask, DataAnalyzingTask
from utils import CITIES, save_to_json

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def main():
    data_fetching_task = DataFetchingTask(CITIES)
    weather_data = data_fetching_task.run()

    data_calculation_task = DataCalculationTask(weather_data)
    city_weather = data_calculation_task.run()

    data_aggregation_task = DataAggregationTask(city_weather)
    aggregated_data = data_aggregation_task.run()

    data_analyzing_task = DataAnalyzingTask(aggregated_data)
    best_cities = data_analyzing_task.run()

    save_to_json(aggregated_data, "aggregated_data.json")
    save_to_json(best_cities, "best_cities.json")

    print("Analysis complete. Best cities data saved to best_cities.json")
    print("Aggregated data saved to aggregated_data.json")

    if best_cities:
        print("\nBest city for travel:")
        for city in best_cities:
            print(f"City: {city['city']}")
            print(f"Average Temperature: {city['avg_temp']}°C")
            print(f"No Precipitation Hours: {city['no_precipitation_hours']} hours")
            print(f"Rank: {city['rank']}")
            for daily in city['daily_data']:
                print(f"Date: {daily['date']}, Average Temperature: {daily['avg_temp']}°C, No Precipitation Hours: {daily['no_precipitation_hours']} hours")
            print("\n")


if __name__ == '__main__':
    main()
