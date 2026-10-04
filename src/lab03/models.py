"""ЛР-3. Производные классы: Taxi и Truck.

Иерархия:

    Car               обычная легковая машина (базовый класс, base.py)
     ├── Taxi         легковая + тариф, зарабатывает на поездках
     └── Truck        грузовая + грузоподъёмность, расход зависит от груза

Оба потомка НЕ копируют код Car: конструктор вызывает super().__init__(),
а всё общее поведение (статусы, drive, refuel, свойства) наследуется.
"""

from base import Car
from validate import _validate_positive_number


class Taxi(Car):
    """Такси: обычная машина, которая берёт деньги за километры."""

    CATEGORY = "такси"          # переопределяем атрибут класса
    BOARDING_FEE = 150.0        # плата за посадку, руб

    def __init__(self, plate, brand, model, year, tariff,
                 mileage=0, tank_capacity=50.0, fuel_level=0.0):
        # Сначала — базовая часть объекта (гос. номер, марка, бак...).
        super().__init__(plate, brand, model, year, mileage, tank_capacity, fuel_level)
        # Потом — то, что есть только у такси. Два новых атрибута:
        self._tariff = _validate_positive_number(tariff, "Тариф")   # руб за км
        self._earnings = 0.0                                          # заработано всего
        self._rides = 0                                               # количество поездок

    @property
    def tariff(self):
        return self._tariff

    @tariff.setter
    def tariff(self, value):
        """Тариф можно менять, но только на положительное число."""
        self._tariff = _validate_positive_number(value, "Тариф")

    @property
    def earnings(self):
        return self._earnings

    @property
    def rides(self):
        return self._rides

    # --- переопределение базового поведения ---

    def trip_cost(self, distance):
        """Для такси стоимость поездки — это то, что платит пассажир."""
        return self.BOARDING_FEE + self._tariff * distance

    # --- новый метод, которого у Car нет ---

    def complete_ride(self, distance):
        """Выполнить заказ: проехать distance км и записать выручку.

        drive() унаследован от Car и сам проверит статус и топливо;
        если он упадёт — выручка не начислится (строка ниже не выполнится).
        """
        self.drive(distance)
        fare = self.trip_cost(distance)
        self._earnings += fare
        self._rides += 1
        return fare

    # --- представление ---

    def display(self):
        """Карточка Car + строка про тариф и выручку."""
        earnings = f"{self._earnings:,.0f}".replace(",", " ")
        return (super().display() +
                f"\n    тариф {self._tariff:.0f} руб/км, поездок {self._rides}, "
                f"заработано {earnings} руб")

    def __str__(self):
        return super().__str__() + f", тариф {self._tariff:.0f} руб/км"

    def __repr__(self):
        return (f"Taxi(plate={self._plate!r}, brand={self._brand!r}, model={self._model!r}, "
                f"year={self._year!r}, tariff={self._tariff!r}, mileage={self._mileage!r}, "
                f"tank_capacity={self._tank_capacity!r}, fuel_level={self._fuel_level!r})")


class Truck(Car):
    """Грузовик: расход растёт с грузом, за трассу платит «Платону»."""

    CATEGORY = "грузовой"
    FUEL_CONSUMPTION = 25.0             # порожний расход, л/100 км
    EXTRA_CONSUMPTION_PER_TONNE = 2.0   # добавка к расходу на каждую тонну груза
    PLATON_RATE = 3.0                   # сбор за проезд по трассам, руб/км

    def __init__(self, plate, brand, model, year, max_load,
                 mileage=0, tank_capacity=300.0, fuel_level=0.0):
        super().__init__(plate, brand, model, year, mileage, tank_capacity, fuel_level)
        self._max_load = _validate_positive_number(max_load, "Грузоподъёмность")  # кг
        self._current_load = 0.0                                                    # кг

    @property
    def max_load(self):
        return self._max_load

    @property
    def current_load(self):
        return self._current_load

    @property
    def load_percent(self):
        return self._current_load / self._max_load * 100

    # --- новые методы ---

    def load(self, kg):
        """Погрузить kg килограммов. Только в гараже и только в пределах грузоподъёмности."""
        kg = _validate_positive_number(kg, "Масса груза")
        if self._status != Car.STATUS_GARAGE:
            raise ValueError(f"Грузить можно только в гараже, а машина {self._status}")
        if self._current_load + kg > self._max_load:
            free = self._max_load - self._current_load
            raise ValueError(f"Перегруз: свободно {free:.0f} кг, а грузят {kg:.0f} кг")
        self._current_load += kg
        return self._current_load

    def unload(self):
        """Разгрузить полностью. Возвращает, сколько выгрузили."""
        if self._status != Car.STATUS_GARAGE:
            raise ValueError(f"Разгружать можно только в гараже, а машина {self._status}")
        unloaded = self._current_load
        self._current_load = 0.0
        return unloaded

    # --- переопределение базового поведения ---

    def fuel_needed(self, distance):
        """Расход = порожний + добавка за груз.

        Этот метод вызывает унаследованный drive(): в Car написано
        `self.fuel_needed(distance)`, и для Truck Python найдёт ЭТУ версию.
        Так один и тот же drive() ведёт себя по-разному для разных классов.
        """
        base = super().fuel_needed(distance)
        extra = distance / 100 * self.EXTRA_CONSUMPTION_PER_TONNE * (self._current_load / 1000)
        return base + extra

    def trip_cost(self, distance):
        """Топливо (с учётом груза, через fuel_needed) + дорожный сбор."""
        return super().trip_cost(distance) + self.PLATON_RATE * distance

    # --- представление ---

    def display(self):
        return (super().display() +
                f"\n    груз {self._current_load:.0f} / {self._max_load:.0f} кг "
                f"({self.load_percent:.0f} %), расход сейчас {self.fuel_needed(100):.1f} л/100 км")

    def __str__(self):
        return super().__str__() + f", груз {self._current_load:.0f}/{self._max_load:.0f} кг"

    def __repr__(self):
        return (f"Truck(plate={self._plate!r}, brand={self._brand!r}, model={self._model!r}, "
                f"year={self._year!r}, max_load={self._max_load!r}, mileage={self._mileage!r}, "
                f"tank_capacity={self._tank_capacity!r}, fuel_level={self._fuel_level!r})")
