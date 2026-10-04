"""ЛР-4. Сценарии: интерфейсы, контракты, полиморфизм через интерфейс, коллекция."""

from collection import Fleet
from interfaces import Comparable, Earnable, Printable
from models import Car, Taxi, Truck
from services import find_max, implemented_interfaces, print_all, total_earnings, work_day


def header(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def expect_error(action, *args, **kwargs):
    try:
        action(*args, **kwargs)
        print("  !!! ошибки не было, а должна была быть")
    except (TypeError, ValueError) as error:
        print(f"  {type(error).__name__}: {error}")


# ---------------------------------------------------------------------------
header("Сценарий 1. Контракт заставляет реализовать методы (задание на 3)")

print("Интерфейс сам по себе создать нельзя:")
expect_error(Printable)

print("Класс, который унаследовал Printable, но не написал display():")


class BrokenVehicle(Printable):
    pass


expect_error(BrokenVehicle)

print("Класс, не имеющий отношения к машинам, но выполняющий контракт:")


class Bicycle(Printable):
    def __init__(self, owner):
        self._owner = owner

    def display(self):
        return f"[велосипед] владелец {self._owner}, топлива не требует"


print("  " + Bicycle("Иван").display())

camry = Car("А123ВС777", "Toyota", "Camry", 2018, 145300, 62, 40)
taxi = Taxi("Т001ТТ77", "Skoda", "Octavia", 2022, tariff=35, mileage=90000, fuel_level=45)
truck = Truck("Н500НН50", "KamAZ", "5490", 2020, max_load=20000, mileage=400000, tank_capacity=400, fuel_level=300)

print("\nОдин метод контракта — разная реализация:")
for obj in (camry, taxi, truck):
    print(obj.display())
    print()

# ---------------------------------------------------------------------------
header("Сценарий 2. Интерфейс как тип, универсальные функции, isinstance (задание на 4)")

print("print_all() принимает list[Printable] — ему всё равно, машины это или велосипеды:")
print_all([camry, Bicycle("Мария"), taxi])

print("Какие контракты выполняет каждый объект (isinstance по интерфейсу):")
for obj in (camry, taxi, truck, Bicycle("Пётр")):
    print(f"  {type(obj).__name__:8} -> {implemented_interfaces(obj)}")

print("\nМножественная реализация: Taxi — это и Car, и Printable, и Comparable, и Earnable:")
print("  Taxi.__mro__ =", [cls.__name__ for cls in Taxi.__mro__])

print("\nЗарабатывают только Earnable. Обычной машине earn() не положен:")
try:
    camry.earn(10)
except AttributeError as error:
    print(f"  AttributeError: {error}")

truck.load(8000)
for vehicle in (taxi, truck):
    vehicle.start_trip()
day_income = f"{work_day([taxi, truck], 50):,.0f}".replace(",", " ")
print(f"work_day([taxi, truck], 50) -> выручка за день {day_income} руб")
print(f"  такси: {taxi.earnings:.0f} руб за {taxi.rides} поездку; грузовик: {truck.earnings:.0f} руб за {truck.deliveries} рейс")
for vehicle in (taxi, truck):
    vehicle.finish_trip()

# ---------------------------------------------------------------------------
header("Сценарий 3. Comparable: сравнение и поиск максимума без ключей сортировки")

print(f"camry.compare_to(taxi) = {camry.compare_to(taxi)}  (пробег {camry.mileage} против {taxi.mileage})")
print(f"camry.is_greater_than(taxi) = {camry.is_greater_than(taxi)}  <- метод из интерфейса, писать не пришлось")
print("Сравнение с чужим типом запрещено контрактом:")
expect_error(camry.compare_to, "строка")
best = find_max([camry, taxi, truck])
print(f"find_max() через Comparable -> {type(best).__name__} {best.plate}, пробег {best.mileage}")

# ---------------------------------------------------------------------------
header("Сценарий 4. Коллекция работает через интерфейсы (задание на 5)")

fleet = Fleet("Автопарк «Стрела»")
for vehicle in (camry, taxi, truck,
                Taxi("Т002ТТ77", "Kia", "Rio", 2021, tariff=28, mileage=12000, fuel_level=20),
                Car("В777АА199", "Lada", "Vesta", 2021, 30000, 55, 55)):
    fleet.add(vehicle)

print("Фильтрация по интерфейсу возвращает новый Fleet:")
print(fleet.get_earnable())
print()
print(f"get_printable(): {len(fleet.get_printable())} из {len(fleet)} — все, т.к. Printable у базового класса")
print("Фильтр по не-интерфейсу:")
expect_error(fleet.get_by_interface, Fleet)

print("\nСортировка через Comparable (коллекция не знает критерия — его знает объект):")
fleet.sort_comparable(descending=True)
for car in fleet:
    print(f"  {car.mileage:>8} км  {type(car).__name__:5} {car.plate}")

print("\nВывод через Printable — display_all():")
print(fleet.display_all())

print(f"\nСуммарная выручка парка: {fleet.total_earnings():,.0f} руб".replace(",", " "))
print(f"То же через универсальную функцию: {total_earnings(fleet.get_earnable()):,.0f} руб".replace(",", " "))
