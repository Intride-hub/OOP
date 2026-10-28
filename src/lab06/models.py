"""ЛР-6. Иерархия Car -> Taxi, Truck из ЛР-3 с аннотациями типов.

Аннотированы параметры конструкторов, атрибуты в __init__ и возвращаемые
значения всех методов. Логика не изменилась.
"""

from validate import (
    _validate_distance,
    _validate_int,
    _validate_mileage,
    _validate_plate,
    _validate_positive,
    _validate_text,
    _validate_year,
)


class Car:
    """Конкретная машина автопарка. Однозначно определяется гос. номером."""

    MIN_YEAR: int = 1886
    MAX_YEAR: int = 2026
    FUEL_CONSUMPTION: float = 8.0     # л на 100 км
    FUEL_PRICE: float = 60.0          # руб. за литр

    STATUS_GARAGE: str = "в гараже"
    STATUS_SERVICE: str = "в ремонте"

    total_created: int = 0

    def __init__(self, plate: str, brand: str, model: str, year: int, mileage: int = 0) -> None:
        self._plate: str = _validate_plate(plate)
        self._brand: str = _validate_text(brand, "Марка")
        self._model: str = _validate_text(model, "Модель")
        self._year: int = _validate_year(year, Car.MIN_YEAR, Car.MAX_YEAR)
        self._mileage: int = _validate_mileage(mileage)
        self._status: str = Car.STATUS_GARAGE
        Car.total_created += 1

    @property
    def plate(self) -> str:
        return self._plate

    @property
    def brand(self) -> str:
        return self._brand

    @property
    def model(self) -> str:
        return self._model

    @property
    def year(self) -> int:
        return self._year

    @property
    def status(self) -> str:
        return self._status

    @property
    def mileage(self) -> int:
        return self._mileage

    @mileage.setter
    def mileage(self, value: int) -> None:
        value = _validate_mileage(value)
        if value < self._mileage:
            raise ValueError(f"Пробег нельзя уменьшить: было {self._mileage} км, передано {value} км")
        self._mileage = value

    def drive(self, distance: int) -> None:
        """Проехать distance км. Машине в ремонте ездить нельзя."""
        distance = _validate_distance(distance)
        if self._status == Car.STATUS_SERVICE:
            raise ValueError(f"Машина {self._plate} в ремонте, ехать нельзя")
        self._mileage += distance

    def trip_cost(self, distance: int) -> float:
        """Стоимость топлива на поездку длиной distance км, руб."""
        distance = _validate_distance(distance)
        return distance / 100 * self.FUEL_CONSUMPTION * self.FUEL_PRICE

    def send_to_service(self) -> None:
        """Гараж -> ремонт."""
        if self._status == Car.STATUS_SERVICE:
            raise ValueError(f"Машина {self._plate} уже в ремонте")
        self._status = Car.STATUS_SERVICE

    def finish_service(self) -> None:
        """Ремонт -> гараж."""
        if self._status != Car.STATUS_SERVICE:
            raise ValueError(f"Машина {self._plate} не в ремонте")
        self._status = Car.STATUS_GARAGE

    def display(self) -> str:
        """Описание машины одной строкой. Потомки дополняют его своими полями."""
        mileage = f"{self._mileage:,}".replace(",", " ")
        return (f"{self._brand} {self._model} ({self._plate}), {self._year} г., "
                f"пробег {mileage} км, {self._status}")

    def __str__(self) -> str:
        return self.display()

    def __repr__(self) -> str:
        return (f"Car(plate={self._plate!r}, brand={self._brand!r}, model={self._model!r}, "
                f"year={self._year}, mileage={self._mileage})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Car):
            return NotImplemented
        return self._plate == other._plate

    def __hash__(self) -> int:
        return hash(self._plate)


class Taxi(Car):
    """Такси: возит пассажиров по тарифу за километр."""

    FUEL_CONSUMPTION: float = 10.0
    BASE_FARE: float = 100.0
    MAX_SEATS: int = 8

    def __init__(self, plate: str, brand: str, model: str, year: int,
                 tariff: float, seats: int = 4, mileage: int = 0) -> None:
        tariff = _validate_positive(tariff, "Тариф")
        seats = _validate_int(seats, "Мест для пассажиров", 1, Taxi.MAX_SEATS)
        super().__init__(plate, brand, model, year, mileage)
        self._tariff: float = tariff
        self._seats: int = seats

    @property
    def tariff(self) -> float:
        return self._tariff

    @property
    def seats(self) -> int:
        return self._seats

    def complete_ride(self, distance: int, passengers: int = 1) -> float:
        """Выполнить заказ: проехать distance км и вернуть цену поездки, руб."""
        _validate_int(passengers, "Пассажиров", 1, self._seats)
        self.drive(distance)
        return Taxi.BASE_FARE + self._tariff * distance

    def display(self) -> str:
        return f"Такси {super().display()}, тариф {self._tariff:g} руб/км, мест {self._seats}"

    def __repr__(self) -> str:
        return (f"Taxi(plate={self.plate!r}, brand={self.brand!r}, model={self.model!r}, "
                f"year={self.year}, tariff={self._tariff}, seats={self._seats}, "
                f"mileage={self.mileage})")


class Truck(Car):
    """Грузовик: возит груз в пределах грузоподъёмности."""

    FUEL_CONSUMPTION: float = 30.0
    TOLL_PER_KM: float = 3.0

    def __init__(self, plate: str, brand: str, model: str, year: int,
                 max_load: float, mileage: int = 0) -> None:
        max_load = _validate_positive(max_load, "Грузоподъёмность")
        super().__init__(plate, brand, model, year, mileage)
        self._max_load: float = max_load
        self._cargo: float = 0.0

    @property
    def max_load(self) -> float:
        return self._max_load

    @property
    def cargo(self) -> float:
        return self._cargo

    def load(self, kg: float) -> None:
        """Погрузить kg кг. Больше грузоподъёмности нельзя."""
        kg = _validate_positive(kg, "Масса груза")
        if self._cargo + kg > self._max_load:
            free = self._max_load - self._cargo
            raise ValueError(f"Перегруз: можно догрузить ещё {free:g} кг, а не {kg:g} кг")
        self._cargo += kg

    def unload(self) -> float:
        """Выгрузить всё и вернуть массу выгруженного, кг."""
        unloaded = self._cargo
        self._cargo = 0.0
        return unloaded

    def trip_cost(self, distance: int) -> float:
        """Топливо (считает Car, но с расходом грузовика) + дорожный сбор."""
        return super().trip_cost(distance) + Truck.TOLL_PER_KM * distance

    def display(self) -> str:
        return f"Грузовик {super().display()}, груз {self._cargo:g} из {self._max_load:g} кг"

    def __repr__(self) -> str:
        return (f"Truck(plate={self.plate!r}, brand={self.brand!r}, model={self.model!r}, "
                f"year={self.year}, max_load={self._max_load}, mileage={self.mileage})")
