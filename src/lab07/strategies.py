"""ЛР-7. Стратегии из ЛР-5, которые использует приложение (с аннотациями типов)."""

from collections.abc import Callable

from models import Car, Truck


def by_year(car: Car) -> int:
    """Ключ сортировки: год выпуска."""
    return car.year


def by_mileage(car: Car) -> int:
    """Ключ сортировки: пробег."""
    return car.mileage


def by_brand_then_year(car: Car) -> tuple[str, int]:
    """Ключ сортировки: марка, при одинаковой марке — год."""
    return (car.brand, car.year)


def is_available(car: Car) -> bool:
    """Фильтр: машина в гараже."""
    return car.status == Car.STATUS_GARAGE


def is_truck(car: Car) -> bool:
    """Фильтр: грузовик."""
    return isinstance(car, Truck)


def make_mileage_filter(max_mileage: int) -> Callable[[Car], bool]:
    """Фабрика: фильтр «пробег не больше max_mileage»."""
    def mileage_filter(car: Car) -> bool:
        """True, если пробег машины не больше max_mileage."""
        return car.mileage <= max_mileage
    return mileage_filter
