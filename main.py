from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue

from tasks import DataFetchingTask
from utils import CITIES


#def main_worker(cities: list[str], queue: Queue):
def main_worker(cities: list[str]):
    fetcher = DataFetchingTask(cities)
    #analyzer = WeatherDataAnalyzer()
    #log_handler = LogHandler()

    with ThreadPoolExecutor(max_workers=5) as executor:
        weather_data_futures = [executor.submit(fetcher.fetch_weather_data, city) for city in cities]
        weather_data = [future.result() for future in weather_data_futures]

    #with ProcessPoolExecutor(max_workers=2) as executor:
    #    analysis_future = executor.submit(analyzer.analyze_data, weather_data)
    #    analysis_result = analysis_future.result()

    #log_handler.log_results(analysis_result)
    #queue.put(analysis_result)


if __name__ == '__main__':
    for city in CITIES:
        res = DataFetchingTask.fetch_weather_data(city)
    #result_queue = Queue()
    #main_worker(CITIES)
    #final_result = result_queue.get()
    #print(f"Final Analysis Result: {final_result}")
