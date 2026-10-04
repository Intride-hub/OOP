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

> ![скриншот](../../images/lab05/demo.png) — *вставить скриншот терминала*

```text

============================================================
Сценарий 1. Три стратегии сортировки и два фильтра (задание на 3)
============================================================
Исходный парк:
    2018   145300 км   64.5 %  Car   Toyota Camry (А123ВС777)
    2021    30000 км  100.0 %  Car   Lada Vesta (В777АА199)
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)
    2020   400000 км   15.0 %  Truck KamAZ 5490 (Н500НН50)
    2016   210000 км   20.0 %  Car   Lada Granta (М222ММ22)

sorted(fleet, key=by_year):
    2016   210000 км   20.0 %  Car   Lada Granta (М222ММ22)
    2018   145300 км   64.5 %  Car   Toyota Camry (А123ВС777)
    2020   400000 км   15.0 %  Truck KamAZ 5490 (Н500НН50)
    2021    30000 км  100.0 %  Car   Lada Vesta (В777АА199)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)

sorted(fleet, key=by_mileage, reverse=True):
    2020   400000 км   15.0 %  Truck KamAZ 5490 (Н500НН50)
    2016   210000 км   20.0 %  Car   Lada Granta (М222ММ22)
    2018   145300 км   64.5 %  Car   Toyota Camry (А123ВС777)
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    30000 км  100.0 %  Car   Lada Vesta (В777АА199)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)

sorted(fleet, key=by_brand_then_year):
    2020   400000 км   15.0 %  Truck KamAZ 5490 (Н500НН50)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)
    2016   210000 км   20.0 %  Car   Lada Granta (М222ММ22)
    2021    30000 км  100.0 %  Car   Lada Vesta (В777АА199)
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2018   145300 км   64.5 %  Car   Toyota Camry (А123ВС777)

list(filter(is_available, fleet)):
    2018   145300 км   64.5 %  Car   Toyota Camry (А123ВС777)
    2021    30000 км  100.0 %  Car   Lada Vesta (В777АА199)
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)
    2020   400000 км   15.0 %  Truck KamAZ 5490 (Н500НН50)
    2016   210000 км   20.0 %  Car   Lada Granta (М222ММ22)
list(filter(is_low_fuel, fleet)):
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)
    2020   400000 км   15.0 %  Truck KamAZ 5490 (Н500НН50)
    2016   210000 км   20.0 %  Car   Lada Granta (М222ММ22)
list(filter(is_taxi, fleet)) — фильтр по типу:
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)

============================================================
Сценарий 2. map(), фабрики функций, sort_by/filter_by, lambda (задание на 4)
============================================================
map(to_short_string, fleet):
    ['Toyota Camry (А123ВС777)', 'Lada Vesta (В777АА199)', 'Skoda Octavia (Т001ТТ77)', 'Kia Rio (Т002ТТ77)', 'KamAZ 5490 (Н500НН50)', 'Lada Granta (М222ММ22)']
map(to_plate, fleet):
    ['А123ВС777', 'В777АА199', 'Т001ТТ77', 'Т002ТТ77', 'Н500НН50', 'М222ММ22']
map(to_summary_dict, fleet)[0]:
    {'type': 'Car', 'plate': 'А123ВС777', 'brand': 'Toyota', 'model': 'Camry', 'year': 2018, 'mileage': 145300, 'status': 'в гараже'}

Фабрика функций: один и тот же код, разные пороги
    make_min_year_filter(2020) -> function, не старше 2020: 4 шт., не старше 2018: 5 шт.
    filter(make_brand_filter('lada')):
    2021    30000 км  100.0 %  Car   Lada Vesta (В777АА199)
    2016   210000 км   20.0 %  Car   Lada Granta (М222ММ22)
    filter(make_max_mileage_filter(100000)):
    2021    30000 км  100.0 %  Car   Lada Vesta (В777АА199)
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)

Методы коллекции принимают функции:
fleet.sort_by(by_plate):
    2018   145300 км   64.5 %  Car   Toyota Camry (А123ВС777)
    2021    30000 км  100.0 %  Car   Lada Vesta (В777АА199)
    2016   210000 км   20.0 %  Car   Lada Granta (М222ММ22)
    2020   400000 км   15.0 %  Truck KamAZ 5490 (Н500НН50)
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)
fleet.filter_by(is_commercial):
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)
    2020   400000 км   15.0 %  Truck KamAZ 5490 (Н500НН50)
Исходный парк не тронут: 6 машин, а filter_by вернул новый Fleet

lambda и именованная функция дают одно и то же:
    key=lambda car: car.mileage -> ['Т002ТТ77', 'В777АА199', 'Т001ТТ77', 'А123ВС777', 'М222ММ22', 'Н500НН50']
    key=by_mileage              -> ['Т002ТТ77', 'В777АА199', 'Т001ТТ77', 'А123ВС777', 'М222ММ22', 'Н500НН50']
    результаты равны: True

============================================================
Сценарий 3. Цепочка filter -> sort -> apply с выводом на каждом шаге (задание на 5)
============================================================
Исходный парк (Vesta в ремонте, Camry в поездке):
    2018   145300 км   64.5 %  Car   Toyota Camry (А123ВС777)
    2021    30000 км  100.0 %  Car   Lada Vesta (В777АА199)
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)
    2020   400000 км   15.0 %  Truck KamAZ 5490 (Н500НН50)
    2016   210000 км   20.0 %  Car   Lada Granta (М222ММ22)

1) filter_by(is_available):
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)
    2020   400000 км   15.0 %  Truck KamAZ 5490 (Н500НН50)
    2016   210000 км   20.0 %  Car   Lada Granta (М222ММ22)

2) .sort_by(by_mileage, reverse=True):
    2020   400000 км   15.0 %  Truck KamAZ 5490 (Н500НН50)
    2016   210000 км   20.0 %  Car   Lada Granta (М222ММ22)
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км   16.0 %  Taxi  Kia Rio (Т002ТТ77)

3) .apply(FullRefuel()) — заправлено 4 машин:
    2020   400000 км  100.0 %  Truck KamAZ 5490 (Н500НН50)
    2016   210000 км  100.0 %  Car   Lada Granta (М222ММ22)
    2022    90000 км  100.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км  100.0 %  Taxi  Kia Rio (Т002ТТ77)

То же самое одной цепочкой:
   result:
    2020   400000 км  100.0 %  Truck KamAZ 5490 (Н500НН50)
    2016   210000 км  100.0 %  Car   Lada Granta (М222ММ22)
    2022    90000 км  100.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км  100.0 %  Taxi  Kia Rio (Т002ТТ77)

============================================================
Сценарий 4. Замена стратегии без изменения кода коллекции
============================================================
Код коллекции один: fleet.apply(<стратегия>). Меняем только то, что передаём.

apply(TopUpTo(50)):
    2018   145300 км   64.5 %  Car   Toyota Camry (А123ВС777)
    2021    30000 км  100.0 %  Car   Lada Vesta (В777АА199)
    2022    90000 км   90.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12000 км   50.0 %  Taxi  Kia Rio (Т002ТТ77)
    2020   400000 км   50.0 %  Truck KamAZ 5490 (Н500НН50)
    2016   210000 км   50.0 %  Car   Lada Granta (М222ММ22)

apply(SendToServiceIfWorn(200000)):
    А123ВС777: в гараже
    В777АА199: в гараже
    Т001ТТ77: в гараже
    Т002ТТ77: в гараже
    Н500НН50: в ремонте
    М222ММ22: в ремонте

apply(lambda ...) — стратегией может быть и лямбда:
    А123ВС777: в гараже
    В777АА199: в гараже
    Т001ТТ77: в гараже
    Т002ТТ77: в ремонте
    Н500НН50: в ремонте
    М222ММ22: в гараже

============================================================
Сценарий 5. Callable-объект как стратегия
============================================================
callable(drive) = True, callable(by_year) = True
apply(TestDrive(50)) — всего наезжено 300 км:
    2018   145350 км   58.1 %  Car   Toyota Camry (А123ВС777)
    2021    30050 км   92.7 %  Car   Lada Vesta (В777АА199)
    2022    90050 км   82.0 %  Taxi  Skoda Octavia (Т001ТТ77)
    2021    12050 км    8.0 %  Taxi  Kia Rio (Т002ТТ77)
    2020   400050 км   11.9 %  Truck KamAZ 5490 (Н500НН50)
    2016   210050 км   12.0 %  Car   Lada Granta (М222ММ22)

CostEstimator(100) через map(): объект-стратегия хранит параметр distance
    Toyota Camry (А123ВС777)     ->      520 руб
    Lada Vesta (В777АА199)       ->      520 руб
    Skoda Octavia (Т001ТТ77)     ->     3650 руб
    Kia Rio (Т002ТТ77)           ->     2950 руб
    KamAZ 5490 (Н500НН50)        ->     1925 руб
    Lada Granta (М222ММ22)       ->      520 руб

Передать не-функцию нельзя:
    TypeError: func должен быть функцией (или объектом с __call__)
```

## 4. Вывод
Изучены функции высшего порядка, `lambda`, `map`/`filter`/`sorted`, замыкания и фабрики
функций, паттерн «Стратегия» на callable-объектах и цепочки операций.
