"""ЛР-3. Сценарии работы с иерархией Car -> Taxi, Truck."""

from base import Car
from collection import Fleet
from models import Taxi, Truck


def header(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def try_it(description, action):
    """Выполнить действие, которое должно упасть, и показать текст ошибки."""
    try:
        action()
        print(f"  {description:<35} -> ошибки нет")
    except (TypeError, ValueError) as error:
        print(f"  {description:<35} -> {type(error).__name__}: {error}")


# ---------------------------------------------------------------------------
header("Сценарий 1. Объекты трёх типов, методы базового и дочерних классов")

camry = Car("А123ВС777", "Toyota", "Camry", 2018, 145300)
taxi = Taxi("Т010ТТ97", "Hyundai", "Solaris", 2019, tariff=25, seats=4, mileage=120500)
truck = Truck("Н500НН50", "KamAZ", "5490", 2020, max_load=20000, mileage=400100)
for car in (camry, taxi, truck):
    print(car)

taxi.drive(15)                                   # метод базового класса
print("\ntaxi.drive(15) — метод Car, пробег:", taxi.mileage)
price = taxi.complete_ride(12, passengers=3)     # собственный метод Taxi
print(f"taxi.complete_ride(12, passengers=3) -> {price:g} руб., пробег {taxi.mileage}")
try_it("taxi.complete_ride(5, passengers=5)", lambda: taxi.complete_ride(5, passengers=5))

truck.load(12000)
print(f"truck.load(12000) -> груз {truck.cargo:g} кг")
try_it("truck.load(9000)", lambda: truck.load(9000))
print(f"truck.unload() -> выгружено {truck.unload():g} кг")

# ---------------------------------------------------------------------------
header("Сценарий 2. super(), isinstance() и переопределённые атрибуты")

print("Car.FUEL_CONSUMPTION =", Car.FUEL_CONSUMPTION,
      "| Taxi:", Taxi.FUEL_CONSUMPTION, "| Truck:", Truck.FUEL_CONSUMPTION)
print("isinstance(taxi, Car):  ", isinstance(taxi, Car))
print("isinstance(taxi, Truck):", isinstance(taxi, Truck))
print("type(taxi) is Car:      ", type(taxi) is Car)
print("issubclass(Truck, Car): ", issubclass(Truck, Car))
print("Taxi.__mro__:", " -> ".join(cls.__name__ for cls in Taxi.__mro__))
print("repr(taxi):", repr(taxi))

created = Car.total_created
try_it("Taxi(..., tariff=-5)", lambda: Taxi("К111КК77", "Kia", "Rio", 2020, tariff=-5))
try_it("Truck(..., max_load='много')", lambda: Truck("К222КК77", "MAN", "TGS", 2015, "много"))
try_it("Taxi с неверным номером", lambda: Taxi("К1", "Kia", "Rio", 2020, tariff=20))
print("Счётчик Car.total_created не изменился:", Car.total_created == created)

# ---------------------------------------------------------------------------
header("Сценарий 3. Полиморфизм: один вызов — разное поведение")

for car in (camry, taxi, truck):        # ни одного if по типу
    print(f"{type(car).__name__:<5} trip_cost(100) = {car.trip_cost(100):7.2f} руб.")
print("\nCar   — расход 8 л/100 км;")
print("Taxi  — метод не переопределён, но свой атрибут FUEL_CONSUMPTION = 10;")
print("Truck — метод переопределён: super().trip_cost() + дорожный сбор.")

# ---------------------------------------------------------------------------
header("Сценарий 4. Одна коллекция — разные типы")

fleet = Fleet([camry, taxi, truck,
               Taxi("В555ВВ77", "Kia", "K5", 2022, tariff=35, seats=3),
               Car("М555ОР50", "Skoda", "Octavia", 2020, 88000)])
fleet.sort(key=lambda car: car.year)
print(fleet)

print("\nget_by_type(Taxi): ", [car.plate for car in fleet.get_by_type(Taxi)])
print("get_by_type(Truck):", [car.plate for car in fleet.get_by_type(Truck)])
print("get_by_type(Car):  ", len(fleet.get_by_type(Car)), "машин — такси и грузовик тоже Car")
print("find_by_plate('Н500НН50'):", repr(fleet.find_by_plate("Н500НН50")))
total = sum(car.trip_cost(100) for car in fleet)
print(f"Топливо и сборы на 100 км для всего парка: {total:.2f} руб.")
