"""ЛР-6. Сценарии: TypedCollection, find/filter/map, протоколы Displayable и Priced."""

from container import Displayable, Priced, TypedCollection, cheapest, show_all
from models import Car, Taxi, Truck


def header(title: str) -> None:
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


class Driver:
    """Водитель — не машина и ни от чего не наследуется, но у него есть display()."""

    def __init__(self, name: str, experience: int) -> None:
        self.name = name
        self.experience = experience

    def display(self) -> str:
        return f"Водитель {self.name}, стаж {self.experience} лет"


class Rock:
    """Камень: ни display(), ни trip_cost() у него нет."""


camry = Car("А123ВС777", "Toyota", "Camry", 2018, 145300)
vesta = Car("В777АА199", "Lada", "Vesta", 2021, 30000)
solaris = Taxi("Т010ТТ97", "Hyundai", "Solaris", 2019, tariff=25, mileage=120500)
sonata = Taxi("В555ВВ77", "Hyundai", "Sonata", 2022, tariff=35, seats=3, mileage=41000)
kamaz = Truck("Н500НН50", "KamAZ", "5490", 2020, max_load=20000, mileage=400100)

# ---------------------------------------------------------------------------
header("Сценарий 1. TypedCollection[Car] и проверка типа при добавлении")

cars: TypedCollection[Car] = TypedCollection(Car)
for car in (camry, vesta, solaris, kamaz):     # Taxi и Truck — тоже Car
    cars.add(car)

for bad in ("Toyota Camry", Rock()):
    try:
        cars.add(bad)  # type: ignore[arg-type]   # mypy тоже нашёл бы эту ошибку
    except TypeError as error:
        print("add() ->", error)
try:
    cars.add(Car("А123ВС777", "Toyota", "Corolla", 2010))
except ValueError as error:
    print("add() ->", error)

cars.sort(key=lambda car: car.year)
print(f"\nget_all() после sort по году, элементов: {len(cars)}")
for car in cars.get_all():
    print("  " + str(car))

# ---------------------------------------------------------------------------
header("Сценарий 2. find(), filter(), map()")

print("find(номер == 'Н500НН50'):", repr(cars.find(lambda car: car.plate == "Н500НН50")))
print("find(год > 2025):         ", cars.find(lambda car: car.year > 2025))
print("filter(пробег < 150 000): ", [car.plate for car in cars.filter(lambda car: car.mileage < 150_000)])

plates = cars.map(lambda car: car.plate)                  # list[str]
costs = cars.map(lambda car: car.trip_cost(100))          # list[float]
print("\nmap(номер)         ->", plates, "| тип элемента:", type(plates[0]).__name__)
print("map(trip_cost(100)) ->", costs, "| тип элемента:", type(costs[0]).__name__)
print("Одна коллекция Car, а результат map — list[str] или list[float]: это и есть R.")

# ---------------------------------------------------------------------------
header("Сценарий 3. Protocol Displayable: подходят без наследования")

displayable: TypedCollection[Displayable] = TypedCollection(Displayable)
for obj in (camry, solaris, kamaz, Driver("Иванов И. И.", 12)):
    displayable.add(obj)
show_all(displayable)

print("\nisinstance(kamaz, Displayable):", isinstance(kamaz, Displayable))
print("Displayable в Truck.__mro__:   ", Displayable in Truck.__mro__)
try:
    displayable.add(Rock())  # type: ignore[arg-type]
except TypeError as error:
    print("add(Rock()) ->", error)

# ---------------------------------------------------------------------------
header("Сценарий 4. Protocol Priced: тот же класс, другое ограничение")

priced: TypedCollection[Priced] = TypedCollection(Priced)
for car in (camry, vesta, solaris, sonata, kamaz):
    priced.add(car)
for item in priced:          # mypy знает про item только то, что у него есть trip_cost()
    print(f"  {type(item).__name__:<5} trip_cost(100) = {item.trip_cost(100):7.2f} руб.")
print("cheapest(priced, 100):", repr(cheapest(priced, 100)))

taxis: TypedCollection[Taxi] = TypedCollection(Taxi)
taxis.add(solaris)
taxis.add(sonata)
best = cheapest(taxis, 100)        # mypy знает: best — Taxi | None, а не просто Priced
if best is not None:
    print(f"cheapest(taxis, 100) вернул Taxi, у него есть тариф: {best.tariff:g} руб/км")
print("cheapest(пустая коллекция):", cheapest(TypedCollection[Car](Car), 100))
