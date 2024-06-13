# Комментарии для ревьюера

Здравствуйте, Владислав. Спасибо за ревью!

## Про Any

Исправил.

## Про ошибку при запуске тестов 

Я использую poetry и эта зависимость в файле pyproject.toml

```toml
[tool.poetry.dev-dependencies]
pytest = "^8.2.2"
pytest-mock = "^3.14.0"
```
этот пакет -- pytest-mock = "^3.14.0"

```shell
$ poetry show
black              24.4.2   The uncompromising code formatter.
certifi            2024.6.2 Python package for providing Mozilla's CA Bundle.
charset-normalizer 3.3.2    The Real First Universal Charset Detector. Open, modern and actively maintained alternative to Chardet.
click              8.1.7    Composable command line interface toolkit
idna               3.7      Internationalized Domain Names in Applications (IDNA)
iniconfig          2.0.0    brain-dead simple config-ini parsing
mypy-extensions    1.0.0    Type system extensions for programs checked with the mypy type checker.
packaging          24.1     Core utilities for Python packages
pathspec           0.12.1   Utility library for gitignore style pattern matching of file paths.
platformdirs       4.2.2    A small Python package for determining appropriate platform-specific dirs, e.g. a `user data dir`.
pluggy             1.5.0    plugin and hook calling mechanisms for python
pytest             8.2.2    pytest: simple powerful testing with Python
pytest-mock        3.14.0   Thin-wrapper around the mock package for easier use with pytest
requests           2.32.3   Python HTTP for Humans.
ruff               0.4.8    An extremely fast Python linter and code formatter, written in Rust.
urllib3            2.2.1    HTTP library with thread-safe connection pooling, file post, and more.

$ pytest
=== test session starts ==
platform darwin -- Python 3.12.3, pytest-8.2.2, pluggy-1.5.0
rootdir: /...........
configfile: pyproject.toml
plugins: mock-3.14.0
collected 4 items

tests/test_data_aggregation.py .                                                                                                                                                                     [ 25%]
tests/test_data_analyzing.py .                                                                                                                                                                       [ 50%]
tests/test_data_calculation.py .                                                                                                                                                                     [ 75%]
tests/test_data_fetching.py .                                                                                                                                                                        [100%]

== 4 passed in 0.02s =====
```

## Про очереди




# Проектное задание первого спринта

Ваша задача — проанализировать данные по погодным условиям, полученные от API Яндекс Погоды.

## Описание задания

**1. Получите информацию о погодных условиях для указанного списка городов, используя API Яндекс Погоды.**

<details>
<summary> Описание </summary>

Список городов находится в переменной `CITIES` в файле [utils.py](utils.py). 
Для взаимодействия с API используйте готовый класс `YandexWeatherAPI` в модуле `external/client.py`. 
Пример работы с классом `YandexWeatherAPI` описан в <a href="#apiusingexample">примере</a>. 
Пример ответа от API для анализа вы найдёте в [файле](examples/response.json).

</details>

**2. Вычислите среднюю температуру и проанализируйте информацию об осадках за указанный период для всех городов.**

<details>
<summary> Описание </summary>

Условия и требования:
- период вычислений в течение дня — с 9 до 19 часов;
- средняя температура рассчитывается за указанный промежуток времени;
- сумма времени (часов), когда погода без осадков (без дождя, снега, града или грозы), рассчитывается за указанный промежуток времени;
- информация о температуре для указанного дня за определённый час находится по следующему пути: `forecasts> [день]> hours> temp`;
- информация об осадках для указанного дня за определённый час находится по следующему пути: `forecasts> [день]> hours> condition`.

[Пример данных](examples/response-day-info.png) с информацией о температуре и осадках за день.

Список вариантов погодных условий находится [в таблице в блоке `condition`](https://yandex.ru/dev/weather/doc/dg/concepts/forecast-test.html#resp-format__forecasts) или в [файле](examples/conditions.txt).

Для анализа данных используйте подготовленный скрипт в модуле `external/analyzer.py`. Скрипт имеет два параметра запуска:
- `-i` – путь до файла с данными, как результат ответа от `YandexWeatherAPI` в формате `json`;
- `-o` – путь до файла для сохранения результата выполнения работы.

Пример запуска скрипта:
```bash
python3 external/analyzer.py -i examples/response.json -o output.json
```

[Пример данных](examples/output.json) с информацией об анализе данных для одного города за период времени, указанный во входном файле.


</details>

**3. Объедините полученные данные и сохраните результат в текстовом файле.**

<details>
<summary> Описание </summary>

Формат сохраняемого файла – **json**, **yml**, **csv** или **xls/xlsx**.

Возможный формат таблицы для сохранения, где рейтинг — это позиция города относительно других при анализе «благоприятности поездки» (п.4).

| Город/день  |                           | 14-06 | ... | 19-06 | Среднее | Рейтинг |
|-------------|:--------------------------|:-----:|:---:|:-----:|--------:|--------:|
| Москва      | Температура, среднее      |  24   |     |  27   |    25.6 |       8 |
|             | Без осадков, часов        |   8   |     |   4   |       6 |         |
| Абу-Даби    | Температура, среднее      |  34   |     |  37   |    35.5 |       2 |
|             | Без осадков, часов        |   9   |     |  10   |     9.5 |         |
| ...         |                           |       |     |       |         |         |

</details>


**4. Проанализируйте результат и сделайте вывод, какой из городов наиболее благоприятен для поездки.**

<details>
<summary> Описание </summary>

Наиболее благоприятным городом считать тот, в котором средняя температура за всё время была самой высокой, а количество времени без осадков — максимальным.
Если таких городов более одного, то выводить все.

</details>

## Требования к решению

1. Используйте для решения как процессы, так и потоки. Для этого разделите все задачи по их типу – IO-bound или CPU-bound.
2. Используйте для решения и очередь, и пул задач.
3. Опишите этапы решения в виде отдельных классов в модуле [tasks.py](tasks.py):
  - `DataFetchingTask` — получение данных через API;
  - `DataCalculationTask` — вычисление погодных параметров;
  - `DataAggregationTask` — объединение вычисленных данных;
  - `DataAnalyzingTask` — финальный анализ и получение результата.
4. Используйте концепции ООП.
5. Предусмотрите обработку исключительных ситуаций.
6. Логируйте результаты действий.
7. Используйте аннотацию типов.
8. Приведите стиль кода в соответствие pep8, flake8, mypy.


## Рекомендации к решению

1. Предусмотрите и обработайте ситуации с некорректным обращением к внешнему API: отсутствующая/битая ссылка, неверный ответ, невалидное содержимое или иной формат ответа.  
2. Покройте написанный код тестами.
3. Используйте таймауты для ограничения времени выполнения частей программы и принудительного завершения при зависаниях или нештатных ситуациях.


---

<a name="apiusingexample"></a>

## Пример использования `YandexWeatherAPI` для работы с API

```python
from external.client import YandexWeatherAPI
from utils import get_url_by_city_name

city_name = "MOSCOW"
url_with_data = get_url_by_city_name(city_name)
resp = YandexWeatherAPI.get_forecasting(data_url)
```
