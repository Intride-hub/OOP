"""ЛР-5. Стратегии для коллекции Fleet.

Ключи сортировки, фильтры, фабрика фильтров и стратегии-объекты (callable).
Все они передаются в Fleet или во встроенные sorted/filter/map как аргументы:
передаём ссылку на функцию (by_year), а не результат вызова (by_year(car)).
"""

from models import Car, Truck


# --- ключи сортировки: для sorted(key=...), Fleet.sort и Fleet.sort_by ---

def by_year(car):
    """Ключ сортировки: год выпуска."""
    return car.year


def by_mileage(car):
    """Ключ сортировки: пробег."""
    return car.mileage


def by_brand_then_year(car):
    """Ключ сортировки по двум полям: сначала марка, при одинаковой марке — год."""
    return (car.brand, car.year)


# --- фильтры (предикаты): для filter() и Fleet.filter_by ---

def is_available(car):
    """Фильтр по атрибуту: машина в гараже, а не в ремонте."""
    return car.status == Car.STATUS_GARAGE


def is_truck(car):
    """Фильтр по типу объекта."""
    return isinstance(car, Truck)


# --- фабрика функций ---

def make_mileage_filter(max_mileage):
    """Создать фильтр «пробег не больше max_mileage».

    Внутренняя функция запоминает max_mileage — это замыкание.
    """
    def mileage_filter(car):
        """True, если пробег машины не больше max_mileage."""
        return car.mileage <= max_mileage
    return mileage_filter


# --- паттерн «Стратегия»: объекты, которые можно вызвать как функцию ---

class CostEstimator:
    """Стратегия: стоимость поездки на distance км. Хранит distance внутри."""

    def __init__(self, distance):
        self.distance = distance

    def __call__(self, car):
        """Посчитать стоимость поездки для одной машины."""
        return car.trip_cost(self.distance)


class SendToServiceIfWorn:
    """Стратегия: отправить в ремонт свободные машины с пробегом больше max_mileage."""

    def __init__(self, max_mileage):
        self.max_mileage = max_mileage

    def __call__(self, car):
        """Обработать одну машину и вернуть её статус."""
        if car.mileage > self.max_mileage and is_available(car):
            car.send_to_service()
        return car.status
