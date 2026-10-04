"""ЛР-3. Сценарии: наследование, переопределение, полиморфизм, коллекция разных типов."""

from base import Car
from collection import Fleet
from models import Taxi, Truck


def header(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def expect_error(action, *args, **kwargs):
    try:
        action(*args, **kwargs)
        print("  !!! ошибки не было, а должна была быть")
    except (TypeError, ValueError) as error:
        print(f"  {type(error).__name__}: {error}")


# ---------------------------------------------------------------------------
header("Сценарий 1. Создание объектов трёх типов, методы базового и дочернего класса")

camry = Car("А123ВС777", "Toyota", "Camry", 2018, 145300, 62, 40)
taxi = Taxi("Т001ТТ77", "Skoda", "Octavia", 2022, tariff=35, mileage=90000, tank_capacity=50, fuel_level=45)
truck = Truck("Н500НН50", "KamAZ", "5490", 2020, max_load=20000, mileage=400000, tank_capacity=400, fuel_level=300)

for car in (camry, taxi, truck):
    print(car.display())
    print()

print("Унаследованные методы работают у потомков без единой строки кода:")
taxi.start_trip()
print(f"  taxi.start_trip() -> статус {taxi.status}")
print(f"  taxi.drive(10) -> ушло {taxi.drive(10):.1f} л, пробег {taxi.mileage}")
taxi.finish_trip()

print("Собственные методы потомков:")
print(f"  truck.load(5000) -> в кузове {truck.load(5000):.0f} кг")
print(f"  truck.load(8000) -> в кузове {truck.load(8000):.0f} кг ({truck.load_percent:.0f} %)")
print("  перегруз:")
expect_error(truck.load, 10000)
print("  у обычной машины метода load нет:")
try:
    camry.load(100)
except AttributeError as error:
    print(f"  AttributeError: {error}")

print("Атрибут класса переопределён в потомке:")
print(f"  Car.FUEL_CONSUMPTION = {Car.FUEL_CONSUMPTION}, Truck.FUEL_CONSUMPTION = {Truck.FUEL_CONSUMPTION}, "
      f"Taxi.FUEL_CONSUMPTION = {Taxi.FUEL_CONSUMPTION} (унаследован)")
print(f"  CATEGORY: {camry.CATEGORY} / {taxi.CATEGORY} / {truck.CATEGORY}")
print("Счётчик один на всю иерархию: Car.total_created =", Car.total_created)

# ---------------------------------------------------------------------------
header("Сценарий 2. Переопределённый метод и isinstance()")

print("__str__ переопределён в каждом классе (print делает разное):")
for car in (camry, taxi, truck):
    print("  ", car)

print("\nisinstance — потомок «является» базовым классом, но не наоборот:")
print(f"  isinstance(taxi, Taxi)  = {isinstance(taxi, Taxi)}")
print(f"  isinstance(taxi, Car)   = {isinstance(taxi, Car)}   <- такси — это тоже машина")
print(f"  isinstance(camry, Taxi) = {isinstance(camry, Taxi)}  <- а машина — не такси")
print(f"  type(taxi) is Car       = {type(taxi) is Car}  <- type() смотрит на точный класс")
print(f"  issubclass(Truck, Car)  = {issubclass(Truck, Car)}")

print("\nfuel_needed переопределён в Truck, а drive() — нет, но drive() это учитывает:")
print(f"  пустой грузовик: {Truck('Х000ХХ00', 'MAN', 'TGX', 2019, 18000).fuel_needed(100):.1f} л/100 км")
print(f"  с грузом {truck.current_load:.0f} кг: {truck.fuel_needed(100):.1f} л/100 км")
truck.start_trip()
used = truck.drive(100)
print(f"  truck.drive(100) списал {used:.1f} л — версию fuel_needed выбрал Python, не мы")
truck.finish_trip()

# ---------------------------------------------------------------------------
header("Сценарий 3. Полиморфизм: один вызов — разное поведение")

print("trip_cost(100) для каждого объекта:")
for car in (camry, taxi, truck):
    print(f"  {type(car).__name__:5} {car.brand:7} -> {car.trip_cost(100):8.0f} руб")

print("\nАнти-паттерн (так делать НЕ надо):")
print("    if isinstance(car, Taxi): ... elif isinstance(car, Truck): ... else: ...")
print("Правильно: car.trip_cost(100) — объект сам знает свой класс.\n")

print("Такси зарабатывает через собственный метод, который опирается на унаследованный drive():")
taxi.start_trip()
for km in (12, 7, 25):
    fare = taxi.complete_ride(km)
    print(f"  заказ {km:2} км -> {fare:.0f} руб; всего {taxi.earnings:.0f} руб за {taxi.rides} поездки")
print("  Не хватает топлива — выручка не начисляется:")
expect_error(taxi.complete_ride, 900)
print(f"  earnings по-прежнему {taxi.earnings:.0f} руб, rides = {taxi.rides}")
taxi.finish_trip()

# ---------------------------------------------------------------------------
header("Сценарий 4. Одна коллекция — разные типы, фильтрация по типу")

fleet = Fleet("Автопарк «Стрела»")
fleet.add(camry)
fleet.add(taxi)
fleet.add(truck)
fleet.add(Taxi("Т002ТТ77", "Kia", "Rio", 2021, tariff=28, fuel_level=20))
fleet.add(Truck("Н501НН50", "MAN", "TGX", 2019, max_load=18000, tank_capacity=400, fuel_level=100))
fleet.add(Car("В777АА199", "Lada", "Vesta", 2021, 30000, 55, 55))

print(fleet)
print("\nПолиморфный вызов внутри коллекции (никаких проверок типа):")
print(f"  выезд всего парка на 100 км обойдётся в {fleet.total_trip_cost(100):,.0f} руб".replace(",", " "))

print("\nВыборки по типу возвращают новый Fleet:")
print(fleet.get_only_taxis())
print(fleet.get_only_trucks())
print(fleet.get_only_plain_cars())
print(fleet.get_only(Car))       # все, потому что все — потомки Car
print("\nПопытка отфильтровать по не-классу:")
expect_error(fleet.get_only, "Taxi")

print("\nПоиск и сортировка из ЛР-2 работают с потомками как с обычными Car:")
fleet.sort_by_year(newest_first=True)
for car in fleet:
    print(f"  {car.year}  {type(car).__name__:5}  {car.plate}")
found = fleet.find_by_plate("н500нн50")
print(f"  find_by_plate вернул объект класса {type(found).__name__}: {found.display().splitlines()[0]}")
