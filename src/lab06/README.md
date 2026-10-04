# ЛР-6 — Generics и typing

## 1. Цель работы
Освоить аннотации типов, обобщённые классы (`TypeVar`, `Generic`) и структурную
типизацию через `typing.Protocol`.

## 2. Описание реализованных типов и контейнеров
**Аннотации** добавлены ко всем классам из ЛР-1/ЛР-3 (`models.py`, `validate.py`,
`interfaces.py`): параметры конструкторов, атрибуты в `__init__`, возвращаемые значения.

**`TypedCollection[T]`** (`container.py`) — Generic-версия `Fleet`. Тип элементов
задаётся при создании (`TypedCollection(Car)`) и проверяется в `add()` через `isinstance`.
Перенесены все методы `Fleet`: `add/remove/get_all`, `__len__/__iter__/__contains__/__getitem__`,
`remove_at`, `sort`, `sort_by`, `filter_by`, `apply`; добавлены `find`, `filter`, `map`.

**TypeVar**:
- `T` — любой тип элемента;
- `R` — тип результата `map()` (может отличаться от `T`);
- `S = TypeVar("S", bound=Scorable)` — только объекты с `score()`;
- `Z = TypeVar("Z", bound=Serializable)` — только объекты с `to_dict()`.

**Протоколы** (`@runtime_checkable`): `Scorable` (`score() -> float`), `Serializable`
(`to_dict() -> dict`). Классы `Car`, `Taxi`, `Truck` **не наследуются** от них — у них просто
есть эти методы (добавлены `score()` и `to_dict()`). Класс `Driver` из демо тоже подходит
под `Scorable`, хотя к машинам отношения не имеет.

Функции с ограниченными TypeVar: `best_by_score(TypedCollection[S])`, `average_score`,
`serialize_all(TypedCollection[Z])`.

## 3. Демонстрация работы (`python demo.py`)
1. Типизированные коллекции `Car` и `str`, валидация типа при добавлении, дубликаты.
2. `find()` (найден / `None`), `filter()`, `map()` с четырьмя разными типами результата.
3. `TypedCollection[Scorable]` с `Car`, `Taxi`, `Truck`, `Driver` без наследования от протокола.
4. `TypedCollection[Serializable]` — тот же класс, другое ограничение; `json.dumps`.

> ![скриншот](../../images/lab06/demo.png) — *вставить скриншот терминала*

```text

============================================================
Сценарий 1. Типизированная коллекция и проверка типов (задание на 3)
============================================================
Автопарк[Car] (4 шт.):
  1. Toyota Camry (А123ВС777), 2018 г., пробег 145 300 км, бак 65 %, в гараже
  2. Skoda Octavia (Т001ТТ77), 2022 г., пробег 90 000 км, бак 90 %, в гараже, тариф 35 руб/км
  3. KamAZ 5490 (Н500НН50), 2020 г., пробег 400 000 км, бак 100 %, в гараже, груз 0/20000 кг
  4. Lada Vesta (В777АА199), 2021 г., пробег 30 000 км, бак 100 %, в гараже

Валидация типа при добавлении:
  TypeError: В Автопарк можно добавить только Car, получено str
  TypeError: В Автопарк можно добавить только Car, получено int
Дубликат по гос. номеру:
  ValueError: Объект Car(plate='А123ВС777', brand='Toyota', model='Camry', year=2018, mileage=0, tank_capacity=50.0, fuel_level=0.0) уже есть в коллекции

Коллекция другого типа — строк — тем же классом:
Номера[str] (2 шт.):
  1. А123ВС777
  2. Т001ТТ77
  TypeError: В Номера можно добавить только str, получено Car

get_all() и перебор:
    Toyota Camry (А123ВС777), 2018 г., пробег 145 300 км, бак 65 %, в гараже
    Skoda Octavia (Т001ТТ77), 2022 г., пробег 90 000 км, бак 90 %, в гараже, тариф 35 руб/км
    KamAZ 5490 (Н500НН50), 2020 г., пробег 400 000 км, бак 100 %, в гараже, груз 0/20000 кг
    Lada Vesta (В777АА199), 2021 г., пробег 30 000 км, бак 100 %, в гараже

============================================================
Сценарий 2. find(), filter(), map() (задание на 4)
============================================================
find(brand == 'Lada')   -> Lada Vesta (В777АА199), 2021 г., пробег 30 000 км, бак 100 %, в гараже
find(year > 2030)       -> None
filter(mileage > 50000) ->
    А123ВС777 145300
    Т001ТТ77 90000
    Н500НН50 400000

map() меняет ТИП результата (для этого нужен второй TypeVar R):
    map(-> plate):        ['А123ВС777', 'Т001ТТ77', 'Н500НН50', 'В777АА199']  тип элементов: str
    map(-> year):         [2018, 2022, 2020, 2021]  тип элементов: int
    map(-> fuel_percent): [64.5, 90.0, 100.0, 100.0]  тип элементов: float
    map(-> to_dict)[0]:   {'type': 'Car', 'plate': 'А123ВС777', 'brand': 'Toyota', 'model': 'Camry', 'year': 2018, 'mileage': 145300, 'tank_capacity': 62.0, 'fuel_level': 40.0, 'status': 'в гараже'}

Цепочка из ЛР-5 работает и здесь:
    ['2022 Т001ТТ77', '2021 В777АА199', '2020 Н500НН50', '2018 А123ВС777']

============================================================
Сценарий 3. Protocol Scorable: TypedCollection[S] без наследования (задание на 5)
============================================================
Классы НЕ наследуются от Scorable, но у них есть score():
    Car.__mro__ содержит Scorable? False
    isinstance(Car(...), Scorable) = True  <- @runtime_checkable смотрит на наличие метода
Оценки[Scorable] (4 шт.):
  1. Toyota Camry (А123ВС777), 2018 г., пробег 145 300 км, бак 65 %, в гараже
  2. Skoda Octavia (Т001ТТ77), 2022 г., пробег 90 000 км, бак 90 %, в гараже, тариф 35 руб/км
  3. KamAZ 5490 (Н500НН50), 2020 г., пробег 400 000 км, бак 100 %, в гараже, груз 0/20000 кг
  4. водитель Иван, стаж 7 лет

Вызов метода протокола для каждого типа:
    Car    -> score() =  45.5
    Taxi   -> score() =  71.0
    Truck  -> score() =  62.0
    Driver -> score() =  85.0
best_by_score()  -> Driver: водитель Иван, стаж 7 лет
average_score()  -> 65.9

Объект БЕЗ score() в коллекцию Scorable не пройдёт:
  TypeError: В Оценки можно добавить только Scorable, получено str
  TypeError: В Оценки можно добавить только Scorable, получено float

============================================================
Сценарий 4. Protocol Serializable: тот же TypedCollection, другое ограничение
============================================================
isinstance(car, Serializable) = True, isinstance(Driver, Serializable) = False (нет to_dict)
  TypeError: В Для JSON можно добавить только Serializable, получено Driver

serialize_all() — список словарей, готовых для json.dump():
{
  "type": "Taxi",
  "plate": "Т001ТТ77",
  "brand": "Skoda",
  "model": "Octavia",
  "year": 2022,
  "mileage": 90000,
  "tank_capacity": 50.0,
  "fuel_level": 45.0,
  "status": "в гараже",
  "tariff": 35.0,
  "earnings": 0.0,
  "rides": 0
}
Всего записей: 4

Один и тот же класс TypedCollection, три разных ограничения:
    TypedCollection(Car, name='Автопарк', items=4)
    TypedCollection(str, name='Номера', items=2)
    TypedCollection(Scorable, name='Оценки', items=4)
    TypedCollection(Serializable, name='Для JSON', items=4)
```

Статическая проверка (`python -m mypy typecheck_demo.py`) находит ошибки до запуска:
```text
typecheck_demo.py:5: error: Argument 1 to "add" of "TypedCollection" has incompatible type "str"; expected "Car"  [arg-type]
typecheck_demo.py:6: error: Argument 1 to "map" of "TypedCollection" has incompatible type "Callable[[Car], int]"; expected "Callable[[Car], str]"  [arg-type]
typecheck_demo.py:6: error: Incompatible return value type (got "int", expected "str")  [return-value]
typecheck_demo.py:8: error: Item "None" of "Car | None" has no attribute "plate"  [union-attr]
typecheck_demo.py:14: error: Argument 1 to "add" of "TypedCollection" has incompatible type "Rock"; expected "Scorable"  [arg-type]
Found 5 errors in 1 file (checked 1 source file)
```

## 4. Вывод
Изучены аннотации типов, `Generic`/`TypeVar` (в т.ч. с `bound=`), `Protocol` как
структурный интерфейс и то, как типизация помогает читать и проверять код.
