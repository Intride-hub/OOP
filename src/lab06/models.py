"""ЛР-6. Иерархия Car / Taxi / Truck из ЛР-4 с полными аннотациями типов.

Что изменилось по сравнению с ЛР-4:
  * у каждого параметра, атрибута и метода указан тип;
  * добавлены два метода — score() и to_dict() — под протоколы
    Scorable и Serializable из container.py (классы от протоколов
    НЕ наследуются: достаточно, что методы есть).

Аннотации ничего не проверяют во время выполнения. Их читают IDE
и статические анализаторы (mypy, pyright) — и человек.

Прежнее описание:
Иерархия Car / Taxi / Truck с формальными контрактами.

    Car(Printable, Comparable)          обычная машина
     ├── Taxi(Car, Earnable)            зарабатывает на пассажирах
     └── Truck(Car, Earnable)           зарабатывает на грузе

Printable и Comparable «прикручены» к базовому классу, поэтому их получают
все потомки. Earnable добавлен только к коммерческим машинам — обычная
легковушка денег не приносит, и заставлять её реализовывать earn() было бы
ложью в архитектуре.
"""

from __future__ import annotations

from typing import Any

from interfaces import Comparable, Earnable, Printable
from validate import (
    _validate_distance,
    _validate_fuel_level,
    _validate_liters,
    _validate_mileage,
    _validate_plate,
    _validate_positive_number,
    _validate_tank_capacity,
    _validate_text,
    _validate_year,
)


class Car(Printable, Comparable):
    """Конкретный автомобиль, стоящий на учёте под своим гос. номером.

    Это не «модель Toyota Camry» как товарная позиция, а именно та машина,
    у которой есть пробег, остаток топлива и текущий статус. Отсюда следуют
    два решения: пробег и топливо — изменяемые поля, а равенство двух
    объектов определяется государственным номером.
    """

    # ---------- атрибуты КЛАССА: одни на все машины ----------

    MIN_YEAR: int = 1886            # год первого автомобиля Бенца
    MAX_YEAR: int = 2026            # текущий год
    FUEL_CONSUMPTION: float = 8.0   # средний расход, л на 100 км
    FUEL_PRICE: float = 65.0        # цена литра, руб (одна на все машины)
    CATEGORY: str = "легковой"      # категория транспортного средства

    # Допустимые статусы вынесены в константы: опечатка в имени константы
    # даст AttributeError сразу, а опечатка в строке молча сломает сравнение.
    STATUS_GARAGE: str = "в гараже"
    STATUS_TRIP: str = "в поездке"
    STATUS_SERVICE: str = "в ремонте"

    total_created: int = 0          # счётчик созданных объектов (меняется)

    # ---------- конструктор ----------

    def __init__(self, plate: str, brand: str, model: str, year: int,
                 mileage: int = 0, tank_capacity: float = 50.0,
                 fuel_level: float = 0.0) -> None:
        self._plate: str = _validate_plate(plate)
        self._brand: str = _validate_text(brand, "Марка")
        self._model: str = _validate_text(model, "Модель")
        self._year: int = _validate_year(year, self.MIN_YEAR, self.MAX_YEAR)
        self._mileage: int = _validate_mileage(mileage)
        # Порядок важен: уровень топлива проверяется относительно
        # УЖЕ проверенного объёма бака.
        self._tank_capacity: float = _validate_tank_capacity(tank_capacity)
        self._fuel_level: float = _validate_fuel_level(fuel_level, self._tank_capacity)
        # Статус не передаётся снаружи: новая машина всегда начинает в гараже.
        self._status: str = Car.STATUS_GARAGE

        # Последней строкой — чтобы объект, упавший на валидации, не считался.
        Car.total_created += 1

    # ---------- свойства только для чтения ----------

    @property
    def plate(self) -> str:
        """Гос. номер — идентификатор машины, менять его нельзя."""
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
    def tank_capacity(self) -> float:
        return self._tank_capacity

    @property
    def fuel_level(self) -> float:
        """Остаток топлива. Меняется только через drive() и refuel()."""
        return self._fuel_level

    @property
    def status(self) -> str:
        """Текущее состояние. Меняется только методами перехода."""
        return self._status

    # ---------- свойство с сеттером ----------

    @property
    def mileage(self) -> int:
        return self._mileage

    @mileage.setter
    def mileage(self, value: int) -> None:
        """Пробег можно только увеличить (скрутить одометр нельзя)."""
        value = _validate_mileage(value)
        if value < self._mileage:
            raise ValueError(
                f"Пробег нельзя уменьшить: было {self._mileage} км, передано {value} км"
            )
        self._mileage = value

    # ---------- вычисляемые свойства (не хранятся, считаются на лету) ----------

    @property
    def age(self) -> int:
        """Возраст машины в годах."""
        return Car.MAX_YEAR - self._year

    @property
    def fuel_percent(self) -> float:
        """Заполненность бака в процентах."""
        return self._fuel_level / self._tank_capacity * 100

    @property
    def range_km(self) -> float:
        """Сколько километров можно проехать на остатке топлива."""
        return self._fuel_level / self.fuel_needed(100) * 100

    @property
    def is_available(self) -> bool:
        """Машина свободна: стоит в гараже и готова к выезду."""
        return self._status == Car.STATUS_GARAGE

    # ---------- вспомогательный расчёт ----------

    def fuel_needed(self, distance: int) -> float:
        """Сколько литров уйдёт на поездку заданной длины."""
        return distance / 100 * self.FUEL_CONSUMPTION

    # ---------- методы изменения состояния (только меняют статус) ----------

    def start_trip(self) -> None:
        """Гараж -> поездка. Нужен хоть какой-то бензин в баке."""
        if self._status != Car.STATUS_GARAGE:
            raise ValueError(f"Нельзя начать поездку: машина {self._status}")
        if self._fuel_level <= 0:
            raise ValueError("Нельзя начать поездку: бак пуст")
        self._status = Car.STATUS_TRIP

    def finish_trip(self) -> None:
        """Поездка -> гараж."""
        if self._status != Car.STATUS_TRIP:
            raise ValueError(f"Нельзя завершить поездку: машина {self._status}")
        self._status = Car.STATUS_GARAGE

    def send_to_service(self) -> None:
        """Гараж -> ремонт. Из поездки в ремонт не отправить — сначала вернись."""
        if self._status != Car.STATUS_GARAGE:
            raise ValueError(f"Нельзя отправить в ремонт: машина {self._status}")
        self._status = Car.STATUS_SERVICE

    def finish_service(self) -> None:
        """Ремонт -> гараж."""
        if self._status != Car.STATUS_SERVICE:
            raise ValueError(f"Нельзя завершить ремонт: машина {self._status}")
        self._status = Car.STATUS_GARAGE

    # ---------- бизнес-методы (меняют данные, проходят через «ворота» статуса) ----------

    def drive(self, distance: int) -> float:
        """Проехать distance км. Возвращает, сколько литров ушло.

        Все проверки — ДО первого присваивания. Если что-то не так,
        объект остаётся ровно в том состоянии, в каком был.
        """
        distance = _validate_distance(distance)
        if self._status != Car.STATUS_TRIP:
            raise ValueError(f"Нельзя ехать: машина {self._status}, сначала start_trip()")
        needed = self.fuel_needed(distance)
        if needed > self._fuel_level:
            raise ValueError(
                f"Не хватит топлива: нужно {needed:.1f} л, в баке {self._fuel_level:.1f} л"
            )
        # round гасит накопление ошибки двоичной арифметики (0.1 + 0.2 != 0.3)
        self._fuel_level = round(self._fuel_level - needed, 2)
        self._mileage += distance
        return needed

    def refuel(self, liters: float) -> float:
        """Залить liters литров. Возвращает новый уровень топлива."""
        liters = _validate_liters(liters)
        if self._status == Car.STATUS_SERVICE:
            raise ValueError("Нельзя заправлять машину в ремонте")
        free = self._tank_capacity - self._fuel_level
        if liters > free:
            raise ValueError(f"В бак влезет ещё {free:.1f} л, а не {liters} л")
        self._fuel_level = round(self._fuel_level + liters, 2)
        return self._fuel_level

    # ---------- общий интерфейс поведения (потомки переопределяют) ----------

    def display(self) -> str:
        """Подробная карточка машины. Потомки дополняют её своими полями."""
        mileage = f"{self._mileage:,}".replace(",", " ")
        return (f"[{self.CATEGORY}] {self._brand} {self._model}, {self._year} г.\n"
                f"    номер {self._plate}, пробег {mileage} км, статус: {self._status}\n"
                f"    топливо {self._fuel_level:.1f} / {self._tank_capacity:.0f} л "
                f"({self.fuel_percent:.0f} %), запас хода {self.range_km:.0f} км")

    def trip_cost(self, distance: int) -> float:
        """Во что обойдётся поездка на distance км.

        Для обычной машины это только топливо. Такси и грузовик считают иначе,
        но вызывающий код об этом не знает — он просто зовёт trip_cost().
        """
        distance = _validate_distance(distance)
        return self.fuel_needed(distance) * self.FUEL_PRICE

    # ---------- ЛР-6: методы под протоколы (без наследования от них) ----------

    def score(self) -> float:
        """Оценка состояния машины от 0 до 100: чем моложе и меньше пробег, тем выше.

        Формула нарочно простая: 100 минус по 5 баллов за каждый год возраста
        и по 10 баллов за каждые 100 000 км пробега, но не ниже нуля.
        """
        penalty = self.age * 5 + self._mileage / 100_000 * 10
        return max(0.0, round(100 - penalty, 1))

    def to_dict(self) -> dict[str, Any]:
        """Плоский словарь со всеми полями — для сохранения в JSON (ЛР-7).

        Ключ "type" нужен, чтобы при загрузке восстановить правильный класс.
        """
        return {
            "type": type(self).__name__,
            "plate": self._plate,
            "brand": self._brand,
            "model": self._model,
            "year": self._year,
            "mileage": self._mileage,
            "tank_capacity": self._tank_capacity,
            "fuel_level": self._fuel_level,
            "status": self._status,
        }

    def compare_to(self, other: object) -> int:
        """Контракт Comparable: сравниваем по пробегу.

        Критерий ОДИН на всю иерархию — иначе сортировка смешанного списка
        стала бы противоречивой (такси по выручке, грузовик по грузу...).
        """
        if not isinstance(other, Car):
            raise TypeError(f"Сравнивать можно только с Car, получено {type(other).__name__}")
        return self._mileage - other._mileage

    # ---------- магические методы ----------

    def __str__(self) -> str:
        """Строка для человека: print(car)."""
        mileage = f"{self._mileage:,}".replace(",", " ")
        return (f"{self._brand} {self._model} ({self._plate}), {self._year} г., "
                f"пробег {mileage} км, бак {self.fuel_percent:.0f} %, {self._status}")

    def __repr__(self) -> str:
        """Строка для разработчика: по ней объект можно воссоздать."""
        return (f"{type(self).__name__}(plate={self._plate!r}, brand={self._brand!r}, "
                f"model={self._model!r}, year={self._year!r}, "
                f"mileage={self._mileage!r}, tank_capacity={self._tank_capacity!r}, "
                f"fuel_level={self._fuel_level!r})")

    def __eq__(self, other: object) -> bool:
        """Две машины равны, если совпал гос. номер.

        Пробег, топливо и статус не участвуют: та же машина после поездки
        остаётся той же машиной.
        """
        if not isinstance(other, Car):
            return NotImplemented
        return self._plate == other._plate

    def __hash__(self) -> int:
        # Определив __eq__, мы обнулили __hash__ по умолчанию. Возвращаем
        # его, иначе объект нельзя положить в set — а это понадобится в ЛР-2.
        return hash(self._plate)


class Taxi(Car, Earnable):
    """Такси: обычная машина, которая берёт деньги за километры."""

    CATEGORY: str = "такси"          # переопределяем атрибут класса
    BOARDING_FEE: float = 150.0      # плата за посадку, руб

    def __init__(self, plate: str, brand: str, model: str, year: int, tariff: float,
                 mileage: int = 0, tank_capacity: float = 50.0,
                 fuel_level: float = 0.0) -> None:
        # Сначала — базовая часть объекта (гос. номер, марка, бак...).
        super().__init__(plate, brand, model, year, mileage, tank_capacity, fuel_level)
        # Потом — то, что есть только у такси. Два новых атрибута:
        self._tariff: float = _validate_positive_number(tariff, "Тариф")   # руб за км
        self._earnings: float = 0.0                                          # заработано всего
        self._rides: int = 0                                                 # количество поездок

    @property
    def tariff(self) -> float:
        return self._tariff

    @tariff.setter
    def tariff(self, value: float) -> None:
        """Тариф можно менять, но только на положительное число."""
        self._tariff = _validate_positive_number(value, "Тариф")

    @property
    def earnings(self) -> float:
        return self._earnings

    @property
    def rides(self) -> int:
        return self._rides

    # --- переопределение базового поведения ---

    def trip_cost(self, distance: int) -> float:
        """Для такси стоимость поездки — это то, что платит пассажир."""
        return self.BOARDING_FEE + self._tariff * distance

    # --- новый метод, которого у Car нет ---

    def complete_ride(self, distance: int) -> float:
        """Выполнить заказ: проехать distance км и записать выручку.

        drive() унаследован от Car и сам проверит статус и топливо;
        если он упадёт — выручка не начислится (строка ниже не выполнится).
        """
        self.drive(distance)
        fare = self.trip_cost(distance)
        self._earnings += fare
        self._rides += 1
        return fare

    def earn(self, distance: int) -> float:
        """Контракт Earnable: для такси «заработать» = выполнить заказ."""
        return self.complete_ride(distance)

    def score(self) -> float:
        """Для такси состояние машины важнее выручки, но выручка добавляет очков."""
        return round(super().score() + self._earnings / 10_000, 1)

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data.update({"tariff": self._tariff, "earnings": self._earnings, "rides": self._rides})
        return data

    # --- представление ---

    def display(self) -> str:
        """Карточка Car + строка про тариф и выручку."""
        earnings = f"{self._earnings:,.0f}".replace(",", " ")
        return (super().display() +
                f"\n    тариф {self._tariff:.0f} руб/км, поездок {self._rides}, "
                f"заработано {earnings} руб")

    def __str__(self) -> str:
        return super().__str__() + f", тариф {self._tariff:.0f} руб/км"

    def __repr__(self) -> str:
        return (f"Taxi(plate={self._plate!r}, brand={self._brand!r}, model={self._model!r}, "
                f"year={self._year!r}, tariff={self._tariff!r}, mileage={self._mileage!r}, "
                f"tank_capacity={self._tank_capacity!r}, fuel_level={self._fuel_level!r})")


class Truck(Car, Earnable):
    """Грузовик: расход растёт с грузом, за трассу платит «Платону»."""

    CATEGORY: str = "грузовой"
    FUEL_CONSUMPTION: float = 25.0             # порожний расход, л/100 км
    EXTRA_CONSUMPTION_PER_TONNE: float = 2.0   # добавка к расходу на каждую тонну груза
    PLATON_RATE: float = 3.0                   # сбор за проезд по трассам, руб/км
    RATE_PER_TONNE_KM: float = 12.0            # выручка за перевозку 1 т на 1 км, руб

    def __init__(self, plate: str, brand: str, model: str, year: int, max_load: float,
                 mileage: int = 0, tank_capacity: float = 300.0,
                 fuel_level: float = 0.0) -> None:
        super().__init__(plate, brand, model, year, mileage, tank_capacity, fuel_level)
        self._max_load: float = _validate_positive_number(max_load, "Грузоподъёмность")  # кг
        self._current_load: float = 0.0                                                    # кг
        self._earnings: float = 0.0
        self._deliveries: int = 0

    @property
    def max_load(self) -> float:
        return self._max_load

    @property
    def current_load(self) -> float:
        return self._current_load

    @property
    def load_percent(self) -> float:
        return self._current_load / self._max_load * 100

    @property
    def earnings(self) -> float:
        return self._earnings

    @property
    def deliveries(self) -> int:
        return self._deliveries

    # --- новые методы ---

    def load(self, kg: float) -> float:
        """Погрузить kg килограммов. Только в гараже и только в пределах грузоподъёмности."""
        kg = _validate_positive_number(kg, "Масса груза")
        if self._status != Car.STATUS_GARAGE:
            raise ValueError(f"Грузить можно только в гараже, а машина {self._status}")
        if self._current_load + kg > self._max_load:
            free = self._max_load - self._current_load
            raise ValueError(f"Перегруз: свободно {free:.0f} кг, а грузят {kg:.0f} кг")
        self._current_load += kg
        return self._current_load

    def unload(self) -> float:
        """Разгрузить полностью. Возвращает, сколько выгрузили."""
        if self._status != Car.STATUS_GARAGE:
            raise ValueError(f"Разгружать можно только в гараже, а машина {self._status}")
        unloaded = self._current_load
        self._current_load = 0.0
        return unloaded

    def deliver(self, distance: int) -> float:
        """Перевезти текущий груз на distance км и получить оплату."""
        if self._current_load <= 0:
            raise ValueError("Нечего везти: кузов пуст")
        self.drive(distance)
        income = self._current_load / 1000 * self.RATE_PER_TONNE_KM * distance
        self._earnings += income
        self._deliveries += 1
        return income

    def earn(self, distance: int) -> float:
        """Контракт Earnable: для грузовика «заработать» = выполнить рейс."""
        return self.deliver(distance)

    def score(self) -> float:
        """Грузовик оценивается мягче: пробег 400 000 км для него норма."""
        penalty = self.age * 3 + self._mileage / 200_000 * 10
        return max(0.0, round(100 - penalty, 1))

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data.update({"max_load": self._max_load, "current_load": self._current_load,
                     "earnings": self._earnings, "deliveries": self._deliveries})
        return data

    # --- переопределение базового поведения ---

    def fuel_needed(self, distance: int) -> float:
        """Расход = порожний + добавка за груз.

        Этот метод вызывает унаследованный drive(): в Car написано
        `self.fuel_needed(distance)`, и для Truck Python найдёт ЭТУ версию.
        Так один и тот же drive() ведёт себя по-разному для разных классов.
        """
        base = super().fuel_needed(distance)
        extra = distance / 100 * self.EXTRA_CONSUMPTION_PER_TONNE * (self._current_load / 1000)
        return base + extra

    def trip_cost(self, distance: int) -> float:
        """Топливо (с учётом груза, через fuel_needed) + дорожный сбор."""
        return super().trip_cost(distance) + self.PLATON_RATE * distance

    # --- представление ---

    def display(self) -> str:
        earnings = f"{self._earnings:,.0f}".replace(",", " ")
        return (super().display() +
                f"\n    груз {self._current_load:.0f} / {self._max_load:.0f} кг "
                f"({self.load_percent:.0f} %), расход сейчас {self.fuel_needed(100):.1f} л/100 км"
                f"\n    рейсов {self._deliveries}, заработано {earnings} руб")

    def __str__(self) -> str:
        return super().__str__() + f", груз {self._current_load:.0f}/{self._max_load:.0f} кг"

    def __repr__(self) -> str:
        return (f"Truck(plate={self._plate!r}, brand={self._brand!r}, model={self._model!r}, "
                f"year={self._year!r}, max_load={self._max_load!r}, mileage={self._mileage!r}, "
                f"tank_capacity={self._tank_capacity!r}, fuel_level={self._fuel_level!r})")
