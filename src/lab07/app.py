"""ЛР-7. Слой бизнес-логики: FleetApp.

Единственное место, где живёт коллекция. CLI не трогает Fleet напрямую —
только через методы этого класса. Здесь же ошибки модели (TypeError,
ValueError) переводятся в исключения предметной области из exceptions.py,
чтобы CLI показывал пользователю понятные сообщения.

В этом файле нет ни print(), ни input(): всё, что нужно показать,
возвращается как значения.
"""

from __future__ import annotations

from typing import Any, Callable

import storage
from collection import Fleet
from exceptions import (
    CarNotFoundError, CarStateError, DuplicateCarError,
    InvalidCarDataError, UnknownStrategyError,
)
from models import Car, Taxi, Truck
from strategie import (
    by_brand_then_year, by_mileage, by_plate, by_year,
    is_available, is_low_fuel, is_taxi, is_truck,
    make_brand_filter, make_min_year_filter, make_status_filter,
)


class FleetApp:
    """Операции над автопарком. Ничего не печатает, всё возвращает."""

    # Стратегии сортировки (ЛР-5): имя для меню -> (подпись, функция-ключ).
    SORT_STRATEGIES: dict[str, tuple[str, Callable[[Car], Any]]] = {
        "plate": ("по гос. номеру", by_plate),
        "year": ("по году выпуска", by_year),
        "mileage": ("по пробегу", by_mileage),
        "brand": ("по марке, затем по году", by_brand_then_year),
    }

    # Фильтры без параметра (ЛР-5): имя -> (подпись, предикат).
    FILTERS: dict[str, tuple[str, Callable[[Car], bool]]] = {
        "available": ("свободные (в гараже)", is_available),
        "low_fuel": ("мало топлива (< 25 %)", is_low_fuel),
        "taxi": ("только такси", is_taxi),
        "truck": ("только грузовики", is_truck),
    }

    def __init__(self, storage_path: str) -> None:
        self._storage_path: str = storage_path
        self._fleet: Fleet = Fleet("Автопарк")

    # ---------- сохранение и загрузка ----------

    def load(self) -> int:
        """Загрузить машины из файла. Возвращает количество загруженных."""
        self._fleet = Fleet("Автопарк")
        for car in storage.load(self._storage_path):
            try:
                self._fleet.add(car)
            except ValueError:
                pass            # дубликат в файле — оставляем первую запись
        return len(self._fleet)

    def save(self) -> int:
        """Сохранить автопарк в файл. Возвращает количество сохранённых."""
        storage.save(self._fleet, self._storage_path)
        return len(self._fleet)

    @property
    def storage_path(self) -> str:
        return self._storage_path

    # ---------- чтение ----------

    def list_cars(self) -> list[Car]:
        """Все машины в текущем порядке."""
        return self._fleet.get_all()

    def count(self) -> int:
        return len(self._fleet)

    def get_car(self, plate: str) -> Car:
        """Найти машину по номеру или бросить CarNotFoundError."""
        try:
            car = self._fleet.find_by_plate(plate)
        except (TypeError, ValueError) as error:
            raise InvalidCarDataError(str(error)) from error
        if car is None:
            raise CarNotFoundError(plate.strip().upper())
        return car

    # ---------- добавление и удаление ----------

    def add_car(self, kind: str, fields: dict[str, Any]) -> Car:
        """Создать машину типа kind ('car' | 'taxi' | 'truck') и добавить в парк.

        Все ошибки валидации модели превращаются в InvalidCarDataError.
        """
        builders: dict[str, Callable[..., Car]] = {"car": Car, "taxi": Taxi, "truck": Truck}
        if kind not in builders:
            raise InvalidCarDataError(f"Неизвестный тип машины: {kind}")
        try:
            car = builders[kind](**fields)
        except (TypeError, ValueError) as error:
            raise InvalidCarDataError(str(error)) from error
        if car in self._fleet:
            raise DuplicateCarError(car.plate)
        self._fleet.add(car)
        return car

    def remove_car(self, plate: str) -> Car:
        """Удалить машину по номеру и вернуть её."""
        car = self.get_car(plate)
        self._fleet.remove(car)
        return car

    # ---------- поиск и фильтрация (ЛР-5) ----------

    def find_by_brand(self, brand: str) -> list[Car]:
        """Все машины указанной марки."""
        return self._fleet.filter_by(make_brand_filter(brand)).get_all()

    def filter_cars(self, filter_name: str) -> list[Car]:
        """Применить один из именованных фильтров FILTERS."""
        if filter_name not in self.FILTERS:
            raise UnknownStrategyError(f"Неизвестный фильтр: {filter_name}")
        _, predicate = self.FILTERS[filter_name]
        return self._fleet.filter_by(predicate).get_all()

    def filter_by_min_year(self, min_year: int) -> list[Car]:
        """Машины не старше указанного года (фабрика функций из ЛР-5)."""
        if not isinstance(min_year, int) or isinstance(min_year, bool):
            raise InvalidCarDataError("Год должен быть целым числом")
        if not (Car.MIN_YEAR <= min_year <= Car.MAX_YEAR):
            raise InvalidCarDataError(f"Год должен быть от {Car.MIN_YEAR} до {Car.MAX_YEAR}")
        return self._fleet.filter_by(make_min_year_filter(min_year)).get_all()

    def filter_by_status(self, status: str) -> list[Car]:
        """Машины с указанным статусом."""
        allowed = (Car.STATUS_GARAGE, Car.STATUS_TRIP, Car.STATUS_SERVICE)
        if status not in allowed:
            raise InvalidCarDataError(f"Статус должен быть одним из: {', '.join(allowed)}")
        return self._fleet.filter_by(make_status_filter(status)).get_all()

    # ---------- сортировка (ЛР-5) ----------

    def sort_cars(self, strategy_name: str, descending: bool = False) -> list[Car]:
        """Отсортировать парк выбранной стратегией. Порядок сохраняется в парке."""
        if strategy_name not in self.SORT_STRATEGIES:
            raise UnknownStrategyError(f"Неизвестная стратегия сортировки: {strategy_name}")
        _, key = self.SORT_STRATEGIES[strategy_name]
        self._fleet.sort(key=key, reverse=descending)
        return self._fleet.get_all()

    # ---------- операции с машиной (состояния из ЛР-1) ----------

    def _do(self, plate: str, action: Callable[[Car], Any]) -> Any:
        """Общий шаблон: найти машину, выполнить действие, перевести ошибки."""
        car = self.get_car(plate)
        try:
            return action(car)
        except TypeError as error:
            raise InvalidCarDataError(str(error)) from error
        except ValueError as error:
            raise CarStateError(str(error)) from error

    def refuel(self, plate: str, liters: float) -> float:
        """Заправить машину; вернуть новый уровень топлива."""
        return self._do(plate, lambda car: car.refuel(liters))

    def start_trip(self, plate: str) -> None:
        self._do(plate, lambda car: car.start_trip())

    def drive(self, plate: str, distance: int) -> float:
        """Проехать; вернуть, сколько литров ушло."""
        return self._do(plate, lambda car: car.drive(distance))

    def finish_trip(self, plate: str) -> None:
        self._do(plate, lambda car: car.finish_trip())

    def send_to_service(self, plate: str) -> None:
        self._do(plate, lambda car: car.send_to_service())

    def finish_service(self, plate: str) -> None:
        self._do(plate, lambda car: car.finish_service())

    # ---------- сводка ----------

    def stats(self) -> dict[str, Any]:
        """Сводные показатели автопарка одним словарём."""
        cars = self._fleet.get_all()
        return {
            "total": len(cars),
            "available": len(self._fleet.get_available()),
            "in_service": len(self._fleet.get_in_service()),
            "taxis": len(self._fleet.get_only_taxis()),
            "trucks": len(self._fleet.get_only_trucks()),
            "total_mileage": self._fleet.total_mileage,
            "total_earnings": self._fleet.total_earnings(),
            "trip_cost_100": self._fleet.total_trip_cost(100) if cars else 0.0,
            "avg_score": sum(car.score() for car in cars) / len(cars) if cars else 0.0,
        }
