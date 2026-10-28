"""ЛР-4. Сценарии работы с интерфейсами Printable и Earnable."""

from collection import Fleet
from interfaces import Earnable, Printable
from models import Car, Taxi, Truck
from services import print_all, total_income


def header(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


class Driver(Printable):
    """Водитель — не машина, но тоже выполняет контракт Printable."""

    def __init__(self, name, experience):
        self.name = name
        self.experience = experience

    def display(self):
        return f"Водитель {self.name}, стаж {self.experience} лет"


camry = Car("А123ВС777", "Toyota", "Camry", 2018, 145300)
taxi = Taxi("Т010ТТ97", "Hyundai", "Solaris", 2019, tariff=25, seats=4, mileage=120500)
truck = Truck("Н500НН50", "KamAZ", "5490", 2020, max_load=20000, mileage=400100)
truck.load(12000)

# ---------------------------------------------------------------------------
header("Сценарий 1. Контракт: абстрактные методы обязательны")

try:
    Printable()
except TypeError as error:
    print("Printable() ->", error)


class HalfDone(Earnable):    # забыли реализовать income()
    pass


try:
    HalfDone()
except TypeError as error:
    print("HalfDone() ->", error)

print("\ndisplay() — у каждого класса своя реализация:")
for car in (camry, taxi, truck):
    print(f"  {type(car).__name__:<5}: {car.display()}")
print("\nincome(100) — разная реализация у Taxi и Truck:")
print(f"  Taxi : {taxi.income(100):g} руб. (посадка + тариф x км)")
print(f"  Truck: {truck.income(100):g} руб. (ставка x тонны x км)")

# ---------------------------------------------------------------------------
header("Сценарий 2. Интерфейс как тип, isinstance, несколько интерфейсов")

driver = Driver("Иванов И. И.", 12)
print("print_all() принимает любые Printable — машины и водителя:")
print_all([camry, taxi, truck, driver])

print("\n            Printable  Earnable  Car")
for obj in (camry, taxi, truck, driver):
    print(f"  {type(obj).__name__:<8}  {isinstance(obj, Printable)!s:<9}  "
          f"{isinstance(obj, Earnable)!s:<8}  {isinstance(obj, Car)}")
print("\nTaxi.__mro__:", " -> ".join(cls.__name__ for cls in Taxi.__mro__))
print(f"total_income([taxi, truck], 100) = {total_income([taxi, truck], 100):g} руб.")

# ---------------------------------------------------------------------------
header("Сценарий 3. Коллекция работает через интерфейсы")

fleet = Fleet([camry, taxi, truck,
               Taxi("В555ВВ77", "Kia", "K5", 2022, tariff=35, seats=3),
               Car("М555ОР50", "Skoda", "Octavia", 2020, 88000)])
print(fleet)   # Fleet.__str__ печатает каждую машину через display()

earners = fleet.get_by_type(Earnable)
print("\nget_by_type(Earnable):", [car.plate for car in earners])
print("get_by_type(Printable):", len(fleet.get_by_type(Printable)), "из", len(fleet))

print("\nПрибыль рейса на 100 км (доход - расходы), без if по типу:")
for car in earners:
    profit = car.income(100) - car.trip_cost(100)
    print(f"  {car.plate}: {car.income(100):7.0f} - {car.trip_cost(100):6.0f} = {profit:7.0f} руб.")
print(f"Доход всех, кто зарабатывает: {total_income(earners, 100):g} руб.")
