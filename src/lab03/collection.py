"""ЛР-3. Fleet из ЛР-2 + выборка по типу get_by_type().

Хранит Car и любых потомков: add() проверяет isinstance(car, Car),
а Taxi и Truck — тоже Car.

Fleet не наследуется от list, а хранит список внутри (композиция):
так снаружи доступны только наши методы с проверками, а не append/insert.
"""

from base import Car


class Fleet:
    """Автопарк: машины без повторов гос. номера."""

    def __init__(self, cars=()):
        self._items = []
        for car in cars:          # каждая машина проходит те же проверки, что и в add()
            self.add(car)

    # --- из ЛР-2, задание на 3 ---

    def add(self, car):
        """Добавить машину. Только Car и без дубликатов по номеру."""
        if not isinstance(car, Car):
            raise TypeError(f"В автопарк можно добавить только Car, получено {type(car).__name__}")
        if car in self._items:    # `in` сравнивает через Car.__eq__, то есть по номеру
            raise ValueError(f"Машина с номером {car.plate} уже есть в автопарке")
        self._items.append(car)

    def remove(self, car):
        """Удалить машину. Если её нет — ValueError."""
        if car not in self._items:
            raise ValueError("Такой машины нет в автопарке")
        self._items.remove(car)

    def get_all(self):
        """Копия списка: изменить автопарк в обход add() через неё нельзя."""
        return list(self._items)

    # --- из ЛР-2, задание на 4 ---

    def find_by_plate(self, plate):
        """Машина с таким номером или None."""
        for car in self._items:
            if car.plate == plate:
                return car
        return None

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        # Благодаря __iter__ работают и `for car in fleet`, и `car in fleet`.
        return iter(self._items)

    # --- из ЛР-2, задание на 5 ---

    def __getitem__(self, index):
        return self._items[index]

    def remove_at(self, index):
        """Удалить машину по индексу и вернуть её."""
        if not -len(self._items) <= index < len(self._items):
            raise IndexError(f"В автопарке нет машины с индексом {index}")
        return self._items.pop(index)

    def sort(self, key, reverse=False):
        """Отсортировать автопарк на месте по функции-ключу."""
        self._items.sort(key=key, reverse=reverse)

    def get_available(self):
        """Новый автопарк из машин в гараже. Исходный не меняется."""
        return Fleet(car for car in self._items if car.status == Car.STATUS_GARAGE)

    def get_in_service(self):
        """Новый автопарк из машин в ремонте. Исходный не меняется."""
        return Fleet(car for car in self._items if car.status == Car.STATUS_SERVICE)

    # --- ЛР-3: выборка по типу ---

    def get_by_type(self, car_type):
        """Новый автопарк из машин данного типа.

        isinstance учитывает наследование: get_by_type(Car) вернёт и такси, и грузовики.
        """
        return Fleet(car for car in self._items if isinstance(car, car_type))

    def __str__(self):
        if not self._items:
            return "Автопарк пуст"
        lines = [f"Автопарк, машин: {len(self._items)}"]
        for index, car in enumerate(self._items):
            lines.append(f"  [{index}] {car}")
        return "\n".join(lines)
