"""ЛР-4. Универсальные функции, которые знают ТОЛЬКО про интерфейсы.

Ни одна функция здесь не импортирует Car, Taxi или Truck. Им всё равно,
что за объект пришёл, — лишь бы он выполнял нужный контракт. Поэтому
сюда можно подать и велосипед, и самолёт, если они реализуют Printable.
"""

from interfaces import Comparable, Earnable, Printable


def print_all(items):
    """Показать каждый элемент через контракт Printable."""
    for item in items:
        print(item.display())
        print()


def find_max(items):
    """Найти наибольший элемент через контракт Comparable (без sorted и без ключей)."""
    items = list(items)
    if not items:
        return None
    best = items[0]
    for item in items[1:]:
        if item.is_greater_than(best):
            best = item
    return best


def total_earnings(items):
    """Суммарная выручка всех Earnable-объектов."""
    return sum(item.earnings for item in items)


def work_day(items, distance):
    """Заставить всех Earnable отработать distance км. Вернуть выручку за день."""
    return sum(item.earn(distance) for item in items)


def implemented_interfaces(obj):
    """Список имён контрактов, которые выполняет объект (для демонстрации isinstance)."""
    names = []
    for interface in (Printable, Comparable, Earnable):
        if isinstance(obj, interface):
            names.append(interface.__name__)
    return names
