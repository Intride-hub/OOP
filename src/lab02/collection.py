"""ЛР-2. Контейнер объектов: Fleet (автопарк).

Fleet — это НЕ автомобиль. Это отдельная сущность, которая управляет
группой автомобилей: добавляет, удаляет, ищет, сортирует, фильтрует.
Сам Car ничего не знает о том, что лежит в каком-то парке.
"""

from model import Car
from validate import _validate_plate


class Fleet:
    """Автопарк: упорядоченный набор уникальных (по гос. номеру) автомобилей."""

    def __init__(self, name="Автопарк"):
        self._name = name
        # Изменяемый список создаётся в конструкторе, а не в теле класса:
        # иначе он был бы ОДИН на все автопарки.
        self._items = []

    # ---------- задание на 3: базовое управление ----------

    @property
    def name(self):
        return self._name

    def add(self, car):
        """Добавить машину. Только Car, только без дубликата по номеру."""
        if not isinstance(car, Car):
            raise TypeError(f"В автопарк можно добавить только Car, получено {type(car).__name__}")
        # `car in self._items` перебирает список и вызывает Car.__eq__,
        # а он сравнивает по гос. номеру — вот и проверка на дубликат.
        if car in self._items:
            raise ValueError(f"Машина с номером {car.plate} уже есть в автопарке")
        self._items.append(car)

    def remove(self, car):
        """Удалить машину (по равенству, т.е. по гос. номеру)."""
        if car not in self._items:
            raise ValueError(f"Машины с номером {car.plate} нет в автопарке")
        self._items.remove(car)

    def get_all(self):
        """Вернуть КОПИЮ списка машин.

        Именно копию: если отдать self._items, внешний код сможет сделать
        fleet.get_all().append("мусор") в обход всех проверок add().
        """
        return list(self._items)

    # ---------- задание на 4: поиск, len, for, ограничения ----------

    def find_by_plate(self, plate):
        """Найти машину по гос. номеру. Вернёт Car или None."""
        plate = _validate_plate(plate)  # та же нормализация, что и в Car
        for car in self._items:
            if car.plate == plate:
                return car
        return None

    def find_by_brand(self, brand):
        """Все машины указанной марки (регистр не важен). Вернёт список."""
        brand = brand.strip().lower()
        return [car for car in self._items if car.brand.lower() == brand]

    def __len__(self):
        """len(fleet)"""
        return len(self._items)

    def __iter__(self):
        """for car in fleet: ...  — отдаём итератор по копии-снимку."""
        return iter(list(self._items))

    def __contains__(self, car):
        """car in fleet"""
        return car in self._items

    # ---------- задание на 5: индексация, удаление по индексу, сортировка, выборки ----------

    def __getitem__(self, index):
        """fleet[0], fleet[-1], fleet[1:3] — делегируем списку."""
        return self._items[index]

    def remove_at(self, index):
        """Удалить машину по индексу и вернуть её."""
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError("Индекс должен быть целым числом")
        if not (-len(self._items) <= index < len(self._items)):
            raise IndexError(f"Индекс {index} вне диапазона 0..{len(self._items) - 1}")
        return self._items.pop(index)

    def sort(self, key=None, reverse=False):
        """Отсортировать НА МЕСТЕ. По умолчанию — по гос. номеру."""
        if key is None:
            key = lambda car: car.plate
        self._items.sort(key=key, reverse=reverse)

    def sort_by_year(self, newest_first=False):
        self.sort(key=lambda car: car.year, reverse=newest_first)

    def sort_by_mileage(self, descending=False):
        self.sort(key=lambda car: car.mileage, reverse=descending)

    def _subset(self, predicate, suffix):
        """Общая заготовка для выборок: новый Fleet из машин, прошедших условие."""
        result = Fleet(f"{self._name}: {suffix}")
        for car in self._items:
            if predicate(car):
                result.add(car)
        return result

    def get_available(self):
        """Новый автопарк из машин, которые стоят в гараже."""
        return self._subset(lambda car: car.is_available, "свободные")

    def get_in_service(self):
        return self._subset(lambda car: car.status == Car.STATUS_SERVICE, "в ремонте")

    def get_low_fuel(self, percent=25):
        """Машины, у которых бак заполнен меньше чем на percent %."""
        return self._subset(lambda car: car.fuel_percent < percent, f"бак < {percent} %")

    # ---------- сводные показатели ----------

    @property
    def total_mileage(self):
        return sum(car.mileage for car in self._items)

    # ---------- магические методы ----------

    def __str__(self):
        if not self._items:
            return f"{self._name}: пусто"
        lines = [f"{self._name} ({len(self._items)} шт.):"]
        for number, car in enumerate(self._items, start=1):
            lines.append(f"  {number}. {car}")
        return "\n".join(lines)

    def __repr__(self):
        return f"Fleet(name={self._name!r}, items={len(self._items)})"
