"""ЛР-6. Сценарии: типизированная коллекция, find/filter/map, протоколы без наследования."""

from __future__ import annotations

from typing import Any

from container import (
    Scorable, Serializable, TypedCollection,
    average_score, best_by_score, serialize_all,
)
from models import Car, Taxi, Truck


def header(title: str) -> None:
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def expect_error(action, *args, **kwargs) -> None:
    try:
        action(*args, **kwargs)
        print("  !!! ошибки не было, а должна была быть")
    except (TypeError, ValueError, IndexError) as error:
        print(f"  {type(error).__name__}: {error}")


# ---------------------------------------------------------------------------
header("Сценарий 1. Типизированная коллекция и проверка типов (задание на 3)")

cars: TypedCollection[Car] = TypedCollection(Car, "Автопарк")
cars.add(Car("А123ВС777", "Toyota", "Camry", 2018, 145300, 62, 40))
cars.add(Taxi("Т001ТТ77", "Skoda", "Octavia", 2022, tariff=35, mileage=90000, fuel_level=45))
cars.add(Truck("Н500НН50", "KamAZ", "5490", 2020, max_load=20000, mileage=400000, fuel_level=300))
cars.add(Car("В777АА199", "Lada", "Vesta", 2021, 30000, 55, 55))
print(cars)

print("\nВалидация типа при добавлении:")
expect_error(cars.add, "Toyota Camry")
expect_error(cars.add, 42)
print("Дубликат по гос. номеру:")
expect_error(cars.add, Car("а123вс777", "Toyota", "Camry", 2018))

print("\nКоллекция другого типа — строк — тем же классом:")
plates: TypedCollection[str] = TypedCollection(str, "Номера")
for plate in ("А123ВС777", "Т001ТТ77"):
    plates.add(plate)
print(plates)
expect_error(plates.add, cars[0])

print("\nget_all() и перебор:")
for car in cars.get_all():
    print("   ", car)

# ---------------------------------------------------------------------------
header("Сценарий 2. find(), filter(), map() (задание на 4)")

found = cars.find(lambda car: car.brand == "Lada")
print(f"find(brand == 'Lada')   -> {found}")
missing = cars.find(lambda car: car.year > 2030)
print(f"find(year > 2030)       -> {missing}")

print("filter(mileage > 50000) ->")
for car in cars.filter(lambda car: car.mileage > 50000):
    print("   ", car.plate, car.mileage)

print("\nmap() меняет ТИП результата (для этого нужен второй TypeVar R):")
plates_list: list[str] = cars.map(lambda car: car.plate)
years: list[int] = cars.map(lambda car: car.year)
percents: list[float] = cars.map(lambda car: round(car.fuel_percent, 1))
dicts: list[dict[str, Any]] = cars.map(lambda car: car.to_dict())
print(f"    map(-> plate):        {plates_list}  тип элементов: {type(plates_list[0]).__name__}")
print(f"    map(-> year):         {years}  тип элементов: {type(years[0]).__name__}")
print(f"    map(-> fuel_percent): {percents}  тип элементов: {type(percents[0]).__name__}")
print(f"    map(-> to_dict)[0]:   {dicts[0]}")

print("\nЦепочка из ЛР-5 работает и здесь:")
chain = cars.filter_by(lambda car: car.is_available).sort_by(lambda car: car.year, reverse=True)
print("   ", [f"{car.year} {car.plate}" for car in chain])

# ---------------------------------------------------------------------------
header("Сценарий 3. Protocol Scorable: TypedCollection[S] без наследования (задание на 5)")

print("Классы НЕ наследуются от Scorable, но у них есть score():")
print(f"    Car.__mro__ содержит Scorable? {Scorable in Car.__mro__}")
print(f"    isinstance(Car(...), Scorable) = {isinstance(cars[0], Scorable)}  <- @runtime_checkable смотрит на наличие метода")


class Driver:
    """Совсем не машина, но score() есть — значит, подходит под Scorable."""

    def __init__(self, name: str, experience_years: int) -> None:
        self.name: str = name
        self.experience_years: int = experience_years

    def score(self) -> float:
        return min(100.0, 50.0 + self.experience_years * 5)

    def __str__(self) -> str:
        return f"водитель {self.name}, стаж {self.experience_years} лет"


scorables: TypedCollection[Scorable] = TypedCollection(Scorable, "Оценки")
for thing in (cars[0], cars[1], cars[2], Driver("Иван", 7)):
    scorables.add(thing)
print(scorables)
print("\nВызов метода протокола для каждого типа:")
for item in scorables:
    print(f"    {type(item).__name__:6} -> score() = {item.score():5.1f}")
best = best_by_score(scorables)
print(f"best_by_score()  -> {type(best).__name__}: {best}")
print(f"average_score()  -> {average_score(scorables):.1f}")

print("\nОбъект БЕЗ score() в коллекцию Scorable не пройдёт:")
expect_error(scorables.add, "строка")
expect_error(scorables.add, 3.14)

# ---------------------------------------------------------------------------
header("Сценарий 4. Protocol Serializable: тот же TypedCollection, другое ограничение")

serializables: TypedCollection[Serializable] = TypedCollection(Serializable, "Для JSON")
for car in cars:
    serializables.add(car)
print(f"isinstance(car, Serializable) = {isinstance(cars[0], Serializable)}, "
      f"isinstance(Driver, Serializable) = {isinstance(Driver('Пётр', 1), Serializable)} (нет to_dict)")
expect_error(serializables.add, Driver("Пётр", 1))

print("\nserialize_all() — список словарей, готовых для json.dump():")
import json
print(json.dumps(serialize_all(serializables)[1], ensure_ascii=False, indent=2))
print(f"Всего записей: {len(serialize_all(serializables))}")

print("\nОдин и тот же класс TypedCollection, три разных ограничения:")
for collection in (cars, plates, scorables, serializables):
    print(f"    {repr(collection)}")
