"""ЛР-4. Иерархия Car / Taxi / Truck, теперь с формальными контрактами.

    Car(Printable, Comparable)          обычная машина
     ├── Taxi(Car, Earnable)            зарабатывает на пассажирах
     └── Truck(Car, Earnable)           зарабатывает на грузе

Printable и Comparable «прикручены» к базовому классу, поэтому их получают
все потомки. Earnable добавлен только к коммерческим машинам — обычная
легковушка денег не приносит, и заставлять её реализовывать earn() было бы
ложью в архитектуре.
"""

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

    MIN_YEAR = 1886            # год первого автомобиля Бенца
    MAX_YEAR = 2026            # текущий год
    FUEL_CONSUMPTION = 8.0     # средний расход, л на 100 км
    FUEL_PRICE = 65.0          # цена литра, руб (одна на все машины)
    CATEGORY = "легковой"      # категория транспортного средства

    # Допустимые статусы вынесены в константы: опечатка в имени константы
    # даст AttributeError сразу, а опечатка в строке молча сломает сравнение.
    STATUS_GARAGE = "в гараже"
    STATUS_TRIP = "в поездке"
    STATUS_SERVICE = "в ремонте"

    total_created = 0          # счётчик созданных объектов (меняется)

    # ---------- конструктор ----------

    def __init__(self, plate, brand, model, year,
                 mileage=0, tank_capacity=50.0, fuel_level=0.0):
        self._plate = _validate_plate(plate)
        self._brand = _validate_text(brand, "Марка")
        self._model = _validate_text(model, "Модель")
        self._year = _validate_year(year, self.MIN_YEAR, self.MAX_YEAR)
        self._mileage = _validate_mileage(mileage)
        # Порядок важен: уровень топлива проверяется относительно
        # УЖЕ проверенного объёма бака.
        self._tank_capacity = _validate_tank_capacity(tank_capacity)
        self._fuel_level = _validate_fuel_level(fuel_level, self._tank_capacity)
        # Статус не передаётся снаружи: новая машина всегда начинает в гараже.
        self._status = Car.STATUS_GARAGE

        # Последней строкой — чтобы объект, упавший на валидации, не считался.
        Car.total_created += 1

    # ---------- свойства только для чтения ----------

    @property
    def plate(self):
        """Гос. номер — идентификатор машины, менять его нельзя."""
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
    def tank_capacity(self):
        return self._tank_capacity

    @property
    def fuel_level(self):
        """Остаток топлива. Меняется только через drive() и refuel()."""
        return self._fuel_level

    @property
    def status(self):
        """Текущее состояние. Меняется только методами перехода."""
        return self._status

    # ---------- свойство с сеттером ----------

    @property
    def mileage(self):
        return self._mileage

    @mileage.setter
    def mileage(self, value):
        """Пробег можно только увеличить (скрутить одометр нельзя)."""
        value = _validate_mileage(value)
        if value < self._mileage:
            raise ValueError(
                f"Пробег нельзя уменьшить: было {self._mileage} км, передано {value} км"
            )
        self._mileage = value

    # ---------- вычисляемые свойства (не хранятся, считаются на лету) ----------

    @property
    def age(self):
        """Возраст машины в годах."""
        return Car.MAX_YEAR - self._year

    @property
    def fuel_percent(self):
        """Заполненность бака в процентах."""
        return self._fuel_level / self._tank_capacity * 100

    @property
    def range_km(self):
        """Сколько километров можно проехать на остатке топлива."""
        return self._fuel_level / self.fuel_needed(100) * 100

    @property
    def is_available(self):
        """Машина свободна: стоит в гараже и готова к выезду."""
        return self._status == Car.STATUS_GARAGE

    # ---------- вспомогательный расчёт ----------

    def fuel_needed(self, distance):
        """Сколько литров уйдёт на поездку заданной длины."""
        return distance / 100 * self.FUEL_CONSUMPTION

    # ---------- методы изменения состояния (только меняют статус) ----------

    def start_trip(self):
        """Гараж -> поездка. Нужен хоть какой-то бензин в баке."""
        if self._status != Car.STATUS_GARAGE:
            raise ValueError(f"Нельзя начать поездку: машина {self._status}")
        if self._fuel_level <= 0:
            raise ValueError("Нельзя начать поездку: бак пуст")
        self._status = Car.STATUS_TRIP

    def finish_trip(self):
        """Поездка -> гараж."""
        if self._status != Car.STATUS_TRIP:
            raise ValueError(f"Нельзя завершить поездку: машина {self._status}")
        self._status = Car.STATUS_GARAGE

    def send_to_service(self):
        """Гараж -> ремонт. Из поездки в ремонт не отправить — сначала вернись."""
        if self._status != Car.STATUS_GARAGE:
            raise ValueError(f"Нельзя отправить в ремонт: машина {self._status}")
        self._status = Car.STATUS_SERVICE

    def finish_service(self):
        """Ремонт -> гараж."""
        if self._status != Car.STATUS_SERVICE:
            raise ValueError(f"Нельзя завершить ремонт: машина {self._status}")
        self._status = Car.STATUS_GARAGE

    # ---------- бизнес-методы (меняют данные, проходят через «ворота» статуса) ----------

    def drive(self, distance):
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

    def refuel(self, liters):
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

    def display(self):
        """Подробная карточка машины. Потомки дополняют её своими полями."""
        mileage = f"{self._mileage:,}".replace(",", " ")
        return (f"[{self.CATEGORY}] {self._brand} {self._model}, {self._year} г.\n"
                f"    номер {self._plate}, пробег {mileage} км, статус: {self._status}\n"
                f"    топливо {self._fuel_level:.1f} / {self._tank_capacity:.0f} л "
                f"({self.fuel_percent:.0f} %), запас хода {self.range_km:.0f} км")

    def trip_cost(self, distance):
        """Во что обойдётся поездка на distance км.

        Для обычной машины это только топливо. Такси и грузовик считают иначе,
        но вызывающий код об этом не знает — он просто зовёт trip_cost().
        """
        distance = _validate_distance(distance)
        return self.fuel_needed(distance) * self.FUEL_PRICE

    def compare_to(self, other):
        """Контракт Comparable: сравниваем по пробегу.

        Критерий ОДИН на всю иерархию — иначе сортировка смешанного списка
        стала бы противоречивой (такси по выручке, грузовик по грузу...).
        """
        if not isinstance(other, Car):
            raise TypeError(f"Сравнивать можно только с Car, получено {type(other).__name__}")
        return self._mileage - other._mileage

    # ---------- магические методы ----------

    def __str__(self):
        """Строка для человека: print(car)."""
        mileage = f"{self._mileage:,}".replace(",", " ")
        return (f"{self._brand} {self._model} ({self._plate}), {self._year} г., "
                f"пробег {mileage} км, бак {self.fuel_percent:.0f} %, {self._status}")

    def __repr__(self):
        """Строка для разработчика: по ней объект можно воссоздать."""
        return (f"{type(self).__name__}(plate={self._plate!r}, brand={self._brand!r}, "
                f"model={self._model!r}, year={self._year!r}, "
                f"mileage={self._mileage!r}, tank_capacity={self._tank_capacity!r}, "
                f"fuel_level={self._fuel_level!r})")

    def __eq__(self, other):
        """Две машины равны, если совпал гос. номер.

        Пробег, топливо и статус не участвуют: та же машина после поездки
        остаётся той же машиной.
        """
        if not isinstance(other, Car):
            return NotImplemented
        return self._plate == other._plate

    def __hash__(self):
        # Определив __eq__, мы обнулили __hash__ по умолчанию. Возвращаем
        # его, иначе объект нельзя положить в set — а это понадобится в ЛР-2.
        return hash(self._plate)


class Taxi(Car, Earnable):
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

    def earn(self, distance):
        """Контракт Earnable: для такси «заработать» = выполнить заказ."""
        return self.complete_ride(distance)

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


class Truck(Car, Earnable):
    """Грузовик: расход растёт с грузом, за трассу платит «Платону»."""

    CATEGORY = "грузовой"
    FUEL_CONSUMPTION = 25.0             # порожний расход, л/100 км
    EXTRA_CONSUMPTION_PER_TONNE = 2.0   # добавка к расходу на каждую тонну груза
    PLATON_RATE = 3.0                   # сбор за проезд по трассам, руб/км
    RATE_PER_TONNE_KM = 12.0            # выручка за перевозку 1 т на 1 км, руб

    def __init__(self, plate, brand, model, year, max_load,
                 mileage=0, tank_capacity=300.0, fuel_level=0.0):
        super().__init__(plate, brand, model, year, mileage, tank_capacity, fuel_level)
        self._max_load = _validate_positive_number(max_load, "Грузоподъёмность")  # кг
        self._current_load = 0.0                                                    # кг
        self._earnings = 0.0
        self._deliveries = 0

    @property
    def max_load(self):
        return self._max_load

    @property
    def current_load(self):
        return self._current_load

    @property
    def load_percent(self):
        return self._current_load / self._max_load * 100

    @property
    def earnings(self):
        return self._earnings

    @property
    def deliveries(self):
        return self._deliveries

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

    def deliver(self, distance):
        """Перевезти текущий груз на distance км и получить оплату."""
        if self._current_load <= 0:
            raise ValueError("Нечего везти: кузов пуст")
        self.drive(distance)
        income = self._current_load / 1000 * self.RATE_PER_TONNE_KM * distance
        self._earnings += income
        self._deliveries += 1
        return income

    def earn(self, distance):
        """Контракт Earnable: для грузовика «заработать» = выполнить рейс."""
        return self.deliver(distance)

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
        earnings = f"{self._earnings:,.0f}".replace(",", " ")
        return (super().display() +
                f"\n    груз {self._current_load:.0f} / {self._max_load:.0f} кг "
                f"({self.load_percent:.0f} %), расход сейчас {self.fuel_needed(100):.1f} л/100 км"
                f"\n    рейсов {self._deliveries}, заработано {earnings} руб")

    def __str__(self):
        return super().__str__() + f", груз {self._current_load:.0f}/{self._max_load:.0f} кг"

    def __repr__(self):
        return (f"Truck(plate={self._plate!r}, brand={self._brand!r}, model={self._model!r}, "
                f"year={self._year!r}, max_load={self._max_load!r}, mileage={self._mileage!r}, "
                f"tank_capacity={self._tank_capacity!r}, fuel_level={self._fuel_level!r})")
