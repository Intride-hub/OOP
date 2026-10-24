# ЛР-5 — Функции как аргументы. Стратегии и делегаты

## 1. Цель работы
Передавать функции как аргументы, применять `map`/`filter`/`sorted`, `lambda`,
фабрики функций (замыкания), реализовать паттерн «Стратегия» через callable-объекты
и цепочки операций над коллекцией.

## 2. Реализованные функции и стратегии (`strategies.py`)
**Ключи сортировки** (для `key=`): `by_plate`, `by_year`, `by_mileage`, `by_fuel_percent`,
`by_brand_then_year` (кортеж — сортировка по двум атрибутам).

**Фильтры** (предикаты): `is_available`, `is_low_fuel`, `is_commercial` (по интерфейсу),
`is_taxi`, `is_truck` (по типу через `isinstance`).

**Фабрики функций**: `make_min_year_filter(year)`, `make_max_mileage_filter(km)`,
`make_brand_filter(brand)`, `make_status_filter(status)` — возвращают новую функцию,
которая «помнит» параметр (замыкание).

**Преобразования для `map`**: `to_short_string`, `to_plate`, `to_summary_dict`.

**Паттерн «Стратегия»** — классы с `__call__`, взаимозаменяемые с функциями и умеющие
хранить параметры и состояние: `FullRefuel`, `TopUpTo(percent)`, `TestDrive(distance)`,
`SendToServiceIfWorn(max_mileage)`, `CostEstimator(distance)`.

**Коллекция** (`collection.py`): `sort_by(key)`, `filter_by(predicate)` возвращают новый
`Fleet`; `apply(func)` применяет функцию ко всем и возвращает `self`; `map(transform)`
возвращает список; `first(predicate)`. Отсюда цепочки:
```python
fleet.filter_by(is_available).sort_by(by_mileage, reverse=True).apply(FullRefuel())
```

## 3. Демонстрация работы (`python demo.py`)
1. Три сортировки и три фильтра через `sorted()` и `filter()`.
2. `map()`, фабрики, `sort_by`/`filter_by`, сравнение `lambda` и именованной функции.
3. Цепочка `filter → sort → apply` с выводом на каждом шаге.
4. Замена стратегии без изменения кода коллекции (`TopUpTo`, `SendToServiceIfWorn`, `lambda`).
5. Callable-объект как стратегия: `TestDrive`, `CostEstimator` через `map()`.

**Сценарий 1.** Три стратегии сортировки и два фильтра (задание на 3)

![Сценарий 1](../../image/lab05/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-10-04%20133531.png)

**Сценарий 2.** `map()`, фабрики функций, `sort_by`/`filter_by`, `lambda` (задание на 4)

![Сценарий 2](../../image/lab05/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-10-04%20133557.png)

**Сценарий 3.** Цепочка `filter` → `sort` → `apply` (задание на 5)

![Сценарий 3](../../image/lab05/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-10-04%20133601.png)

**Сценарий 4.** Замена стратегии без изменения кода коллекции

![Сценарий 4](../../image/lab05/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-10-04%20133608.png)

**Сценарий 5.** Callable-объект как стратегия

![Сценарий 5](../../image/lab05/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202026-10-04%20133610.png)

## 4. Вывод
Изучены функции высшего порядка, `lambda`, `map`/`filter`/`sorted`, замыкания и фабрики
функций, паттерн «Стратегия» на callable-объектах и цепочки операций.
