"""ЛР-6. TypedCollection — Generic-версия коллекции из ЛР-2, и два Protocol.

Fleet из ЛР-2 не тронут. TypedCollection повторяет его методы, но знает тип
своих элементов. Методы, которые зависели от машин (find_by_plate,
get_available), заменены общими find() и filter() с функцией-условием.
"""

from collections.abc import Callable, Iterator
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")      # тип элементов коллекции
R = TypeVar("R")      # тип результата map(): может отличаться от T


class TypedCollection(Generic[T]):
    """Коллекция элементов одного типа T.

    Аннотации проверяет mypy до запуска. Во время работы программы они ничего
    не запрещают, поэтому тип элемента ещё и проверяется в add() через isinstance.
    """

    def __init__(self, item_type: type) -> None:
        self._item_type: type = item_type
        self._items: list[T] = []

    # --- методы коллекции из ЛР-2 ---

    def add(self, item: T) -> None:
        """Добавить элемент: только нужного типа и без дубликатов."""
        if not isinstance(item, self._item_type):
            raise TypeError(f"Ожидался {self._item_type.__name__}, получено {type(item).__name__}")
        if item in self._items:
            raise ValueError(f"Такой элемент уже есть: {item!r}")
        self._items.append(item)

    def remove(self, item: T) -> None:
        """Удалить элемент. Если его нет — ValueError."""
        if item not in self._items:
            raise ValueError("Такого элемента нет в коллекции")
        self._items.remove(item)

    def get_all(self) -> list[T]:
        """Копия списка элементов."""
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def remove_at(self, index: int) -> T:
        """Удалить элемент по индексу и вернуть его."""
        if not -len(self._items) <= index < len(self._items):
            raise IndexError(f"Нет элемента с индексом {index}")
        return self._items.pop(index)

    def sort(self, key: Callable[[T], Any], reverse: bool = False) -> None:
        """Отсортировать на месте по функции-ключу."""
        self._items.sort(key=key, reverse=reverse)

    # --- задание на 4: find, filter, map ---

    def find(self, predicate: Callable[[T], bool]) -> T | None:
        """Первый элемент, для которого predicate истинно, или None."""
        for item in self._items:
            if predicate(item):
                return item
        return None

    def filter(self, predicate: Callable[[T], bool]) -> list[T]:
        """Все элементы, для которых predicate истинно."""
        return [item for item in self._items if predicate(item)]

    def map(self, transform: Callable[[T], R]) -> list[R]:
        """Применить transform к каждому элементу. Тип результата R может отличаться от T."""
        return [transform(item) for item in self._items]


# --- задание на 5: протоколы и TypeVar с ограничением ---

@runtime_checkable
class Displayable(Protocol):
    """Всё, что умеет описать себя: есть метод display() -> str."""

    def display(self) -> str: ...


@runtime_checkable
class Priced(Protocol):
    """Всё, у чего есть стоимость поездки: метод trip_cost(distance) -> float."""

    def trip_cost(self, distance: int) -> float: ...


D = TypeVar("D", bound=Displayable)   # только объекты с display()
P = TypeVar("P", bound=Priced)        # только объекты с trip_cost()


def show_all(items: TypedCollection[D]) -> None:
    """Вывести каждый элемент через display(). mypy знает, что display() есть у всех."""
    for item in items:
        print("  " + item.display())


def cheapest(items: TypedCollection[P], distance: int) -> P | None:
    """Элемент с самой дешёвой поездкой на distance км или None, если коллекция пуста.

    Возвращает тот же тип, что лежит в коллекции: для TypedCollection[Taxi] — Taxi.
    """
    return min(items, key=lambda item: item.trip_cost(distance), default=None)
