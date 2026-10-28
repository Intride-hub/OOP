"""ЛР-4. Универсальные функции, которые знают только интерфейсы.

Здесь нет импорта Car, Taxi и Truck: функции работают с любым объектом,
который выполняет контракт, — даже не с машиной.
"""

from collections.abc import Iterable

from interfaces import Earnable, Printable


def print_all(items: Iterable[Printable]) -> None:
    """Вывести описание каждого объекта через display()."""
    for item in items:
        print("  " + item.display())


def total_income(items: Iterable[Earnable], distance: int) -> float:
    """Суммарный доход всех объектов за рейс длиной distance км."""
    return sum(item.income(distance) for item in items)
