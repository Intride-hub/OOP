"""ЛР-5. Стратегии и функции-обработчики для коллекции Fleet.

Здесь четыре вида «кирпичиков», и все они — просто вызываемые объекты
(callable), которые коллекция получает как аргумент и вызывает сама:

1. Ключи сортировки      car -> значение,  для sorted(..., key=...)
2. Фильтры (предикаты)   car -> bool,      для filter(...)
3. Фабрики функций       параметр -> новая функция-фильтр (замыкание)
4. Стратегии-объекты     класс с __call__, взаимозаменяем с функцией

Коллекция не знает, что именно ей передали, — она просто вызывает.
Это и есть паттерн «Стратегия»: поведение подставляется снаружи.
"""

from interfaces import Earnable
from models import Car, Taxi, Truck


# ===========================================================================
# 1. Ключи сортировки: принимают машину, возвращают то, ПО ЧЕМУ сортировать
# ===========================================================================

def by_plate(car):
    """Сортировка по гос. номеру (алфавитно)."""
    return car.plate


def by_year(car):
    """Сортировка по году выпуска (старые первыми)."""
    return car.year


def by_mileage(car):
    """Сортировка по пробегу (малый пробег первым)."""
    return car.mileage


def by_fuel_percent(car):
    """Сортировка по заполненности бака."""
    return car.fuel_percent


def by_brand_then_year(car):
    """Сортировка по двум атрибутам: сначала марка (без учёта регистра), внутри марки — год.

    Кортеж сравнивается поэлементно: сначала первый элемент, при равенстве — второй.
    """
    return (car.brand.lower(), car.year)


# ===========================================================================
# 2. Фильтры: принимают машину, возвращают True (оставить) или False (выкинуть)
# ===========================================================================

def is_available(car):
    """Машина стоит в гараже и готова к выезду."""
    return car.is_available


def is_low_fuel(car):
    """Бак заполнен меньше чем на четверть — пора на заправку."""
    return car.fuel_percent < 25


def is_commercial(car):
    """Машина приносит деньги (выполняет контракт Earnable из ЛР-4)."""
    return isinstance(car, Earnable)


def is_taxi(car):
    """Фильтр по типу объекта."""
    return isinstance(car, Taxi)


def is_truck(car):
    """Фильтр по типу объекта."""
    return isinstance(car, Truck)


# ===========================================================================
# 3. Фабрики функций: принимают параметр, возвращают НОВУЮ функцию-фильтр
# ===========================================================================

def make_min_year_filter(min_year):
    """Создать фильтр «не старше min_year».

    Внутренняя функция «запоминает» min_year — это называется замыканием.
    Каждый вызов фабрики даёт независимый фильтр со своим порогом.
    """
    def filter_fn(car):
        return car.year >= min_year
    return filter_fn


def make_max_mileage_filter(max_mileage):
    """Создать фильтр «пробег не больше max_mileage»."""
    def filter_fn(car):
        return car.mileage <= max_mileage
    return filter_fn


def make_brand_filter(brand):
    """Создать фильтр по марке (без учёта регистра)."""
    brand = brand.strip().lower()

    def filter_fn(car):
        return car.brand.lower() == brand
    return filter_fn


def make_status_filter(status):
    """Создать фильтр по статусу (в гараже / в поездке / в ремонте)."""
    def filter_fn(car):
        return car.status == status
    return filter_fn


# ===========================================================================
# 4. Преобразования для map(): машина -> что-то другое
# ===========================================================================

def to_short_string(car):
    """Car -> короткая строка «Марка Модель (номер)»."""
    return f"{car.brand} {car.model} ({car.plate})"


def to_plate(car):
    """Car -> гос. номер."""
    return car.plate


def to_summary_dict(car):
    """Car -> словарь с основными полями (пригодится для сохранения в файл в ЛР-7)."""
    return {
        "type": type(car).__name__,
        "plate": car.plate,
        "brand": car.brand,
        "model": car.model,
        "year": car.year,
        "mileage": car.mileage,
        "status": car.status,
    }


# ===========================================================================
# 5. Стратегии-объекты: классы с __call__ — ведут себя как функции,
#    но могут хранить параметры и состояние
# ===========================================================================

class FullRefuel:
    """Стратегия «заправить под горлышко». Пропускает машины в ремонте."""

    def __init__(self):
        self.refueled = 0   # состояние: сколько машин заправили

    def __call__(self, car):
        free = round(car.tank_capacity - car.fuel_level, 2)
        if car.status != Car.STATUS_SERVICE and free > 0:
            car.refuel(free)
            self.refueled += 1


class TopUpTo:
    """Стратегия «долить до N процентов». Параметр задаётся при создании."""

    def __init__(self, percent):
        self.percent = percent

    def __call__(self, car):
        target = car.tank_capacity * self.percent / 100
        liters = round(target - car.fuel_level, 2)
        if car.status != Car.STATUS_SERVICE and liters > 0:
            car.refuel(liters)


class TestDrive:
    """Стратегия «прогнать каждую свободную машину на distance км»."""

    def __init__(self, distance):
        self.distance = distance
        self.total_km = 0

    def __call__(self, car):
        if not car.is_available:
            return
        car.start_trip()
        try:
            car.drive(self.distance)
            self.total_km += self.distance
        except ValueError:
            pass            # не хватило топлива — просто пропускаем
        finally:
            car.finish_trip()


class SendToServiceIfWorn:
    """Стратегия «отправить в ремонт машины с пробегом больше порога»."""

    def __init__(self, max_mileage):
        self.max_mileage = max_mileage

    def __call__(self, car):
        if car.mileage > self.max_mileage and car.is_available:
            car.send_to_service()


class CostEstimator:
    """Стратегия-преобразование для map(): машина -> стоимость поездки на distance км."""

    def __init__(self, distance):
        self.distance = distance

    def __call__(self, car):
        return car.trip_cost(self.distance)
