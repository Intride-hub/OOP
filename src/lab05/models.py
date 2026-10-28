"""ЛР-5. Иерархия из ЛР-3 без изменений: Car -> Taxi, Truck (в одном файле)."""

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

    # --- атрибуты класса: одни на все машины ---
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
        self._status = Car.STATUS_GARAGE   # новая машина всегда стоит в гараже
        # Счётчик увеличиваем последним: машина, не прошедшая проверки, не считается.
        Car.total_created += 1

    # --- свойства только для чтения ---

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

    # --- свойство с сеттером ---

    @property
    def mileage(self):
        return self._mileage

    @mileage.setter
    def mileage(self, value):
        """Пробег можно только увеличить: скручивать одометр нельзя."""
        value = _validate_mileage(value)
        if value < self._mileage:
            raise ValueError(f"Пробег нельзя уменьшить: было {self._mileage} км, передано {value} км")
        self._mileage = value

    # --- бизнес-методы ---

    def drive(self, distance):
        """Проехать distance км. Машине в ремонте ездить нельзя."""
        distance = _validate_distance(distance)
        if self._status == Car.STATUS_SERVICE:
            raise ValueError(f"Машина {self._plate} в ремонте, ехать нельзя")
        self._mileage += distance

    def trip_cost(self, distance):
        """Стоимость топлива на поездку длиной distance км, руб."""
        distance = _validate_distance(distance)
        # Расход и цену берём через self: у Taxi и Truck свои FUEL_CONSUMPTION.
        return distance / 100 * self.FUEL_CONSUMPTION * self.FUEL_PRICE

    # --- смена состояния ---

    def send_to_service(self):
        """Гараж -> ремонт."""
        if self._status == Car.STATUS_SERVICE:
            raise ValueError(f"Машина {self._plate} уже в ремонте")
        self._status = Car.STATUS_SERVICE

    def finish_service(self):
        """Ремонт -> гараж."""
        if self._status != Car.STATUS_SERVICE:
            raise ValueError(f"Машина {self._plate} не в ремонте")
        self._status = Car.STATUS_GARAGE

    # --- общий метод вывода: потомки его переопределяют ---

    def display(self):
        """Описание машины одной строкой. Потомки дополняют его своими полями."""
        mileage = f"{self._mileage:,}".replace(",", " ")   # 145300 -> "145 300"
        return (f"{self._brand} {self._model} ({self._plate}), {self._year} г., "
                f"пробег {mileage} км, {self._status}")

    # --- магические методы ---

    def __str__(self):
        # self может быть Taxi или Truck: тогда вызовется их display().
        return self.display()

    def __repr__(self):
        return (f"Car(plate={self._plate!r}, brand={self._brand!r}, model={self._model!r}, "
                f"year={self._year}, mileage={self._mileage})")

    def __eq__(self, other):
        """Машины равны, если совпадает гос. номер. Пробег и статус не важны."""
        if not isinstance(other, Car):
            return NotImplemented
        return self._plate == other._plate

    def __hash__(self):
        # Определив __eq__, мы теряем __hash__ по умолчанию. Возвращаем его,
        # чтобы машину можно было положить в set или сделать ключом словаря.
        return hash(self._plate)


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
