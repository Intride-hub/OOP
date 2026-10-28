"""ЛР-7. Коллекция Fleet из ЛР-5 с аннотациями типов (ЛР-6)."""

from collections.abc import Callable, Iterable, Iterator
from typing import Any

from models import Car


class Fleet:
    """Автопарк: машины без повторов гос. номера."""

    def __init__(self, cars: Iterable[Car] = ()) -> None:
        self._items: list[Car] = []
        for car in cars:
            self.add(car)

    def add(self, car: Car) -> None:
        """Добавить машину. Только Car (и потомки) и без дубликатов по номеру."""
        if not isinstance(car, Car):
            raise TypeError(f"В автопарк можно добавить только Car, получено {type(car).__name__}")
        if car in self._items:
            raise ValueError(f"Машина с номером {car.plate} уже есть в автопарке")
        self._items.append(car)

    def remove(self, car: Car) -> None:
        """Удалить машину. Если её нет — ValueError."""
        if car not in self._items:
            raise ValueError("Такой машины нет в автопарке")
        self._items.remove(car)

    def get_all(self) -> list[Car]:
        """Копия списка машин."""
        return list(self._items)

    def find_by_plate(self, plate: str) -> Car | None:
        """Машина с таким номером или None."""
        for car in self._items:
            if car.plate == plate:
                return car
        return None

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Car]:
        return iter(self._items)

    def __getitem__(self, index: int) -> Car:
        return self._items[index]

    def remove_at(self, index: int) -> Car:
        """Удалить машину по индексу и вернуть её."""
        if not -len(self._items) <= index < len(self._items):
            raise IndexError(f"В автопарке нет машины с индексом {index}")
        return self._items.pop(index)

    def sort(self, key: Callable[[Car], Any], reverse: bool = False) -> None:
        """Отсортировать на месте."""
        self._items.sort(key=key, reverse=reverse)

    def sort_by(self, key_func: Callable[[Car], Any], reverse: bool = False) -> "Fleet":
        """Новый автопарк, отсортированный по key_func."""
        return Fleet(sorted(self._items, key=key_func, reverse=reverse))

    def filter_by(self, predicate: Callable[[Car], bool]) -> "Fleet":
        """Новый автопарк из машин, для которых predicate(car) истинно."""
        return Fleet(filter(predicate, self._items))

    def apply(self, func: Callable[[Car], Any]) -> list[Any]:
        """Применить func к каждой машине и вернуть список результатов."""
        return [func(car) for car in self._items]
