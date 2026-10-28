"""ЛР-7. Слой бизнес-логики: FleetApp.

Только FleetApp работает с коллекцией Fleet: CLI вызывает методы этого класса
и не трогает коллекцию напрямую. Здесь же ошибки модели (TypeError, ValueError)
превращаются в исключения предметной области из exceptions.py.
В этом файле нет ни print(), ни input(): результат возвращается значениями.
"""

from collections.abc import Callable
from typing import Any

import storage
from collection import Fleet
from exceptions import CarNotFoundError, DuplicateCarError, InvalidCarDataError
from models import Car, Taxi, Truck
from strategies import (
    by_brand_then_year,
    by_mileage,
    by_year,
    is_available,
    is_truck,
    make_mileage_filter,
)
from validate import _validate_plate


class FleetApp:
    """Операции над автопарком: загрузка, поиск, фильтры, сортировка, изменения."""

    CAR_KINDS: dict[str, type[Car]] = {"car": Car, "taxi": Taxi, "truck": Truck}
    SORT_KEYS: dict[str, Callable[[Car], Any]] = {
        "year": by_year,
        "mileage": by_mileage,
        "brand": by_brand_then_year,
    }
    FILTERS: dict[str, Callable[[Car], bool]] = {
        "available": is_available,
        "trucks": is_truck,
    }

    def __init__(self, path: str) -> None:
        self._path: str = path
        self._fleet: Fleet = Fleet()

    # --- файл ---

    def load(self) -> int:
        """Загрузить машины из файла и вернуть их количество."""
        self._fleet = Fleet(storage.load(self._path))
        return len(self._fleet)

    def save(self) -> None:
        """Сохранить машины в файл."""
        storage.save(self._fleet, self._path)

    # --- чтение ---

    def all_cars(self) -> list[Car]:
        """Все машины в текущем порядке."""
        return self._fleet.get_all()

    def find(self, plate: str) -> Car:
        """Найти машину по номеру. Номер можно вводить в любом регистре и с пробелами."""
        try:
            plate = _validate_plate(plate)
        except ValueError as error:
            raise InvalidCarDataError(str(error)) from error
        car = self._fleet.find_by_plate(plate)
        if car is None:
            raise CarNotFoundError(f"машины с номером {plate} нет в автопарке")
        return car

    def filter(self, name: str) -> list[Car]:
        """Машины, прошедшие готовый фильтр: "available" или "trucks"."""
        return self._fleet.filter_by(self.FILTERS[name]).get_all()

    def filter_by_mileage(self, max_mileage: int) -> list[Car]:
        """Машины с пробегом не больше max_mileage (фильтр из фабрики ЛР-5)."""
        if max_mileage < 0:
            raise InvalidCarDataError(f"пробег не может быть отрицательным, получено {max_mileage}")
        return self._fleet.filter_by(make_mileage_filter(max_mileage)).get_all()

    # --- изменение ---

    def add_car(self, kind: str, params: dict[str, Any]) -> Car:
        """Создать машину типа kind ("car", "taxi", "truck") и добавить её в автопарк."""
        try:
            car = self.CAR_KINDS[kind](**params)
        except (TypeError, ValueError) as error:
            raise InvalidCarDataError(str(error)) from error
        if self._fleet.find_by_plate(car.plate) is not None:
            raise DuplicateCarError(f"машина с номером {car.plate} уже есть в автопарке")
        self._fleet.add(car)
        return car

    def sort(self, key_name: str) -> list[Car]:
        """Отсортировать автопарк по стратегии "year", "mileage" или "brand"."""
        self._fleet.sort(key=self.SORT_KEYS[key_name])
        return self.all_cars()

    def toggle_service(self, plate: str) -> Car:
        """Отправить машину в ремонт или вернуть из ремонта."""
        car = self.find(plate)
        if car.status == Car.STATUS_SERVICE:
            car.finish_service()
        else:
            car.send_to_service()
        return car

    def remove(self, plate: str) -> Car:
        """Удалить машину по номеру и вернуть её."""
        car = self.find(plate)
        self._fleet.remove(car)
        return car
