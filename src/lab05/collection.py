"""ЛР-5. Fleet из ЛР-2/ЛР-3 + методы, которые принимают функции.

sort_by(key_func), filter_by(predicate), apply(func) — коллекция не знает,
по какому правилу сортировать или отбирать: правило передают ей как аргумент.
Поэтому частные выборки get_available(), get_in_service() и get_by_type()
больше не нужны — их заменяет один filter_by() с фильтром из strategies.py.
"""

from models import Car


class Fleet:
    """Автопарк: машины без повторов гос. номера."""

    def __init__(self, cars=()):
        self._items = []
        for car in cars:          # каждая машина проходит те же проверки, что и в add()
            self.add(car)

    # --- базовые операции (ЛР-2) ---

    def add(self, car):
        """Добавить машину. Только Car (и потомки) и без дубликатов по номеру."""
        if not isinstance(car, Car):
            raise TypeError(f"В автопарк можно добавить только Car, получено {type(car).__name__}")
        if car in self._items:
            raise ValueError(f"Машина с номером {car.plate} уже есть в автопарке")
        self._items.append(car)

    def remove(self, car):
        """Удалить машину. Если её нет — ValueError."""
        if car not in self._items:
            raise ValueError("Такой машины нет в автопарке")
        self._items.remove(car)

    def get_all(self):
        """Копия списка машин."""
        return list(self._items)

    def find_by_plate(self, plate):
        """Машина с таким номером или None."""
        for car in self._items:
            if car.plate == plate:
                return car
        return None

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def remove_at(self, index):
        """Удалить машину по индексу и вернуть её."""
        if not -len(self._items) <= index < len(self._items):
            raise IndexError(f"В автопарке нет машины с индексом {index}")
        return self._items.pop(index)

    def sort(self, key, reverse=False):
        """Отсортировать на месте (действие: меняет этот автопарк)."""
        self._items.sort(key=key, reverse=reverse)

    # --- ЛР-5: функции как аргументы ---

    def sort_by(self, key_func, reverse=False):
        """Новый автопарк, отсортированный по key_func (запрос: исходный не меняется)."""
        return Fleet(sorted(self._items, key=key_func, reverse=reverse))

    def filter_by(self, predicate):
        """Новый автопарк из машин, для которых predicate(car) истинно."""
        return Fleet(filter(predicate, self._items))

    def apply(self, func):
        """Применить func к каждой машине и вернуть список результатов."""
        return [func(car) for car in self._items]

    def __str__(self):
        if not self._items:
            return "Автопарк пуст"
        lines = [f"Автопарк, машин: {len(self._items)}"]
        for index, car in enumerate(self._items):
            lines.append(f"  [{index}] {car}")
        return "\n".join(lines)
