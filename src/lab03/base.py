"""ЛР-3. Базовый класс Car — класс из ЛР-1.

Единственное изменение: добавлен общий метод display(). Потомки переопределяют
display(), а __str__ вызывает self.display()
"""

from validate import (
    _validate_distance,
    _validate_mileage,
    _validate_plate,
    _validate_text,
    _validate_year,
)


class Car:

    MIN_YEAR = 1886            # год первого автомобиля
    MAX_YEAR = 2026            # текущий год
    FUEL_CONSUMPTION = 8.0     # расход топлива, л на 100 км
    FUEL_PRICE = 60.0          # цена топлива, руб. за литр

    STATUS_GARAGE = "в гараже"
    STATUS_SERVICE = "в ремонте"

    total_created = 0          # счётчик созданных машин

    def __init__(self, plate, brand, model, year, mileage=0):
        self._plate = _validate_plate(plate)
        self._brand = _validate_text(brand, "Марка")
        self._model = _validate_text(model, "Модель")
        self._year = _validate_year(year, Car.MIN_YEAR, Car.MAX_YEAR)
        self._mileage = _validate_mileage(mileage)
        self._status = Car.STATUS_GARAGE  
        Car.total_created += 1


    @property
    def plate(self):
        return self._plate

    @property
    def brand(self):
        return self._brand

    @property
    def model(self):
        return self._model

    @property
    def year(self):
        return self._year

    @property
    def status(self):
        """Сеттера нет: статус меняют только send_to_service() и finish_service()."""
        return self._status


    @property
    def mileage(self):
        return self._mileage

    @mileage.setter
    def mileage(self, value):
        value = _validate_mileage(value)
        if value < self._mileage:
            raise ValueError(f"Пробег нельзя уменьшить: было {self._mileage} км, передано {value} км")
        self._mileage = value

    # --- бизнес-методы ---

    def drive(self, distance):
        distance = _validate_distance(distance)
        if self._status == Car.STATUS_SERVICE:
            raise ValueError(f"Машина {self._plate} в ремонте, ехать нельзя")
        self._mileage += distance

    def trip_cost(self, distance):
        distance = _validate_distance(distance)
        return distance / 100 * self.FUEL_CONSUMPTION * self.FUEL_PRICE

    # --- смена состояния ---

    def send_to_service(self):
        if self._status == Car.STATUS_SERVICE:
            raise ValueError(f"Машина {self._plate} уже в ремонте")
        self._status = Car.STATUS_SERVICE

    def finish_service(self):
        if self._status != Car.STATUS_SERVICE:
            raise ValueError(f"Машина {self._plate} не в ремонте")
        self._status = Car.STATUS_GARAGE

    # --- общий метод вывода: потомки его переопределяют ---

    def display(self):
        mileage = f"{self._mileage:,}".replace(",", " ")   # 145300 -> "145 300"
        return (f"{self._brand} {self._model} ({self._plate}), {self._year} г., "
                f"пробег {mileage} км, {self._status}")

    # --- магические методы ---

    def __str__(self):
        return self.display()

    def __repr__(self):
        return (f"Car(plate={self._plate!r}, brand={self._brand!r}, model={self._model!r}, "
                f"year={self._year}, mileage={self._mileage})")

    def __eq__(self, other):
        if not isinstance(other, Car):
            return NotImplemented
        return self._plate == other._plate

    def __hash__(self):
        return hash(self._plate)
