"""ЛР-3. Дочерние классы Taxi и Truck.

Порядок в __init__ потомка: проверить свои аргументы -> super().__init__ ->
записать свои атрибуты. Если свои аргументы неверны, объект не создаётся
и счётчик Car.total_created не увеличивается.
"""

from base import Car
from validate import _validate_int, _validate_positive


class Taxi(Car):
    """Такси: возит пассажиров по тарифу за километр."""

    FUEL_CONSUMPTION = 10.0    # в городе расход выше, чем у обычной машины
    BASE_FARE = 100.0          # стоимость посадки, руб.
    MAX_SEATS = 8

    def __init__(self, plate, brand, model, year, tariff, seats=4, mileage=0):
        tariff = _validate_positive(tariff, "Тариф")
        seats = _validate_int(seats, "Мест для пассажиров", 1, Taxi.MAX_SEATS)
        super().__init__(plate, brand, model, year, mileage)
        self._tariff = tariff      # руб. за км
        self._seats = seats

    @property
    def tariff(self):
        return self._tariff

    @property
    def seats(self):
        return self._seats

    def complete_ride(self, distance, passengers=1):
        """Выполнить заказ: проехать distance км и вернуть цену поездки, руб."""
        _validate_int(passengers, "Пассажиров", 1, self._seats)
        self.drive(distance)       # метод Car: проверит расстояние и что машина не в ремонте
        return Taxi.BASE_FARE + self._tariff * distance

    def display(self):
        return f"Такси {super().display()}, тариф {self._tariff:g} руб/км, мест {self._seats}"

    def __repr__(self):
        return (f"Taxi(plate={self.plate!r}, brand={self.brand!r}, model={self.model!r}, "
                f"year={self.year}, tariff={self._tariff}, seats={self._seats}, "
                f"mileage={self.mileage})")


class Truck(Car):
    """Грузовик: возит груз в пределах грузоподъёмности."""

    FUEL_CONSUMPTION = 30.0    # л на 100 км
    TOLL_PER_KM = 3.0          # дорожный сбор для грузовиков, руб. за км

    def __init__(self, plate, brand, model, year, max_load, mileage=0):
        max_load = _validate_positive(max_load, "Грузоподъёмность")
        super().__init__(plate, brand, model, year, mileage)
        self._max_load = max_load  # кг
        self._cargo = 0.0          # сколько груза в кузове сейчас, кг

    @property
    def max_load(self):
        return self._max_load

    @property
    def cargo(self):
        return self._cargo

    def load(self, kg):
        """Погрузить kg кг. Больше грузоподъёмности нельзя."""
        kg = _validate_positive(kg, "Масса груза")
        if self._cargo + kg > self._max_load:
            free = self._max_load - self._cargo
            raise ValueError(f"Перегруз: можно догрузить ещё {free:g} кг, а не {kg:g} кг")
        self._cargo += kg

    def unload(self):
        """Выгрузить всё и вернуть массу выгруженного, кг."""
        unloaded = self._cargo
        self._cargo = 0.0
        return unloaded

    def trip_cost(self, distance):
        """Топливо (считает Car, но с расходом грузовика) + дорожный сбор."""
        return super().trip_cost(distance) + Truck.TOLL_PER_KM * distance

    def display(self):
        return f"Грузовик {super().display()}, груз {self._cargo:g} из {self._max_load:g} кг"

    def __repr__(self):
        return (f"Truck(plate={self.plate!r}, brand={self.brand!r}, model={self.model!r}, "
                f"year={self.year}, max_load={self._max_load}, mileage={self.mileage})")
