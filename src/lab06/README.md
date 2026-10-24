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

**Сценарий 1.** Типизированная коллекция и проверка типов (задание на 3)

![Сценарий 1](../../image/lab06/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-10-04%20133702.png)

**Сценарий 2.** `find()`, `filter()`, `map()` (задание на 4)

![Сценарий 2](../../image/lab06/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-10-04%20133706.png)

**Сценарий 3.** `Protocol Scorable`: `TypedCollection[S]` без наследования (задание на 5)

![Сценарий 3](../../image/lab06/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-10-04%20133710.png)

**Сценарий 4.** `Protocol Serializable`: тот же `TypedCollection`, другое ограничение

![Сценарий 4](../../image/lab06/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-10-04%20133717.png)

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
