"""ЛР-6. Обобщённая (generic) коллекция TypedCollection[T] и протоколы.

Коллекция Fleet из ЛР-2 умела хранить только Car. TypedCollection умеет
хранить «что угодно, но одного типа T», причём этот T указывается при
создании — и проверяется дважды:

  * статически  — IDE/mypy видят TypedCollection[Car] и ругаются на add("строка")
                  ещё до запуска;
  * динамически — в конструктор передаётся класс (TypedCollection(Car)),
                  и add() проверяет isinstance во время выполнения.

Протоколы Scorable и Serializable — это «интерфейсы без наследования»:
объект подходит, если у него ЕСТЬ нужный метод. Наследоваться не нужно.
"""

from __future__ import annotations

from typing import Any, Callable, Generic, Iterator, Optional, Protocol, TypeVar, runtime_checkable

# ===========================================================================
# Протоколы: структурная типизация («утиная типизация» с проверкой)
# ===========================================================================


@runtime_checkable
class Scorable(Protocol):
    """Всё, у чего есть score() -> float. Наследоваться от Scorable не нужно."""

    def score(self) -> float:
        ...


@runtime_checkable
class Serializable(Protocol):
    """Всё, что умеет превращаться в словарь: to_dict() -> dict."""

    def to_dict(self) -> dict[str, Any]:
        ...


# ===========================================================================
# Переменные типа
# ===========================================================================

T = TypeVar("T")                            # любой тип
R = TypeVar("R")                            # тип результата map()
S = TypeVar("S", bound=Scorable)            # только то, у чего есть score()
Z = TypeVar("Z", bound=Serializable)        # только то, у чего есть to_dict()


# ===========================================================================
# Обобщённая коллекция
# ===========================================================================

class TypedCollection(Generic[T]):
    """Коллекция объектов одного типа T. Повторяет интерфейс Fleet из ЛР-2/5."""

    def __init__(self, item_type: type, name: str = "Коллекция") -> None:
        # item_type — класс (или протокол с @runtime_checkable) для проверки в add().
        if not isinstance(item_type, type):
            raise TypeError("item_type должен быть классом")
        self._item_type: type = item_type
        self._name: str = name
        self._items: list[T] = []

    # ---------- ЛР-2 (задание на 3): базовое управление ----------

    @property
    def name(self) -> str:
        return self._name

    @property
    def item_type(self) -> type:
        return self._item_type

    def add(self, item: T) -> None:
        """Добавить объект. Проверка типа — во время выполнения, дубликатов — по ==."""
        if not isinstance(item, self._item_type):
            raise TypeError(
                f"В {self._name} можно добавить только {self._item_type.__name__}, "
                f"получено {type(item).__name__}"
            )
        if item in self._items:
            raise ValueError(f"Объект {item!r} уже есть в коллекции")
        self._items.append(item)

    def remove(self, item: T) -> None:
        if item not in self._items:
            raise ValueError(f"Объекта {item!r} нет в коллекции")
        self._items.remove(item)

    def get_all(self) -> list[T]:
        """Копия списка — как и в Fleet."""
        return list(self._items)

    # ---------- ЛР-2 (задание на 4): len, for, in ----------

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(list(self._items))

    def __contains__(self, item: object) -> bool:
        return item in self._items

    # ---------- ЛР-2 (задание на 5): индексация, удаление, сортировка ----------

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def remove_at(self, index: int) -> T:
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError("Индекс должен быть целым числом")
        if not (-len(self._items) <= index < len(self._items)):
            raise IndexError(f"Индекс {index} вне диапазона")
        return self._items.pop(index)

    def sort(self, key: Callable[[T], Any], reverse: bool = False) -> None:
        """Сортировка на месте по ключу key."""
        self._items.sort(key=key, reverse=reverse)

    # ---------- ЛР-5: стратегии как аргументы ----------

    def sort_by(self, key: Callable[[T], Any], reverse: bool = False) -> TypedCollection[T]:
        """Новая коллекция того же типа, отсортированная по key."""
        result: TypedCollection[T] = TypedCollection(self._item_type, self._name)
        for item in sorted(self._items, key=key, reverse=reverse):
            result.add(item)
        return result

    def filter_by(self, predicate: Callable[[T], bool]) -> TypedCollection[T]:
        """Новая коллекция из элементов, прошедших predicate."""
        result: TypedCollection[T] = TypedCollection(self._item_type, self._name)
        for item in self._items:
            if predicate(item):
                result.add(item)
        return result

    def apply(self, func: Callable[[T], Any]) -> TypedCollection[T]:
        """Применить func к каждому элементу; вернуть self для цепочки."""
        for item in self._items:
            func(item)
        return self

    # ---------- ЛР-6 (задание на 4): find / filter / map ----------

    def find(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Первый элемент, для которого predicate вернул True, иначе None."""
        for item in self._items:
            if predicate(item):
                return item
        return None

    def filter(self, predicate: Callable[[T], bool]) -> list[T]:
        """Список всех подходящих элементов (именно list, как просит ТЗ)."""
        return [item for item in self._items if predicate(item)]

    def map(self, transform: Callable[[T], R]) -> list[R]:
        """Список результатов transform(item). Тип результата R может отличаться от T."""
        return [transform(item) for item in self._items]

    # ---------- представление ----------

    def __str__(self) -> str:
        if not self._items:
            return f"{self._name}[{self._item_type.__name__}]: пусто"
        lines = [f"{self._name}[{self._item_type.__name__}] ({len(self._items)} шт.):"]
        for number, item in enumerate(self._items, start=1):
            lines.append(f"  {number}. {item}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"TypedCollection({self._item_type.__name__}, name={self._name!r}, items={len(self._items)})"


# ===========================================================================
# Функции, использующие ограниченные TypeVar
# ===========================================================================

def best_by_score(items: TypedCollection[S]) -> Optional[S]:
    """Элемент с максимальным score(). Работает с любым S, у которого есть score()."""
    best: Optional[S] = None
    for item in items:
        if best is None or item.score() > best.score():
            best = item
    return best


def average_score(items: TypedCollection[S]) -> float:
    """Средний score() по коллекции (0.0 для пустой)."""
    if len(items) == 0:
        return 0.0
    return sum(item.score() for item in items) / len(items)


def serialize_all(items: TypedCollection[Z]) -> list[dict[str, Any]]:
    """Список словарей — то, что можно отдать json.dump()."""
    return [item.to_dict() for item in items]
