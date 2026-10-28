"""ЛР-5. Сценарии: функции как аргументы, стратегии, цепочки операций."""

from collection import Fleet
from models import Car, Taxi, Truck
from strategies import (
    CostEstimator,
    SendToServiceIfWorn,
    by_brand_then_year,
    by_mileage,
    by_year,
    is_available,
    is_truck,
    make_mileage_filter,
)


def header(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def show(cars, field):
    """Короткий вывод: марка и значение нужного поля у каждой машины."""
    return ", ".join(f"{car.brand} {getattr(car, field)}" for car in cars)


camry = Car("А123ВС777", "Toyota", "Camry", 2018, 145300)
vesta = Car("В777АА199", "Lada", "Vesta", 2021, 30000)
solaris = Taxi("Т010ТТ97", "Hyundai", "Solaris", 2019, tariff=25, mileage=120500)
sonata = Taxi("В555ВВ77", "Hyundai", "Sonata", 2022, tariff=35, seats=3, mileage=41000)
kamaz = Truck("Н500НН50", "KamAZ", "5490", 2020, max_load=20000, mileage=400100)
gazelle = Truck("Е321КХ50", "GAZ", "Gazelle", 2017, max_load=1500, mileage=260000)
gazelle.send_to_service()

fleet = Fleet([camry, vesta, solaris, sonata, kamaz, gazelle])

# ---------------------------------------------------------------------------
header("Сценарий 1. Три стратегии сортировки и два фильтра")

rows = [
    ("sorted(key=by_year)", show(sorted(fleet, key=by_year), "year")),
    ("sorted(key=by_mileage, reverse=True)", show(sorted(fleet, key=by_mileage, reverse=True), "mileage")),
    ("sorted(key=by_brand_then_year)", show(sorted(fleet, key=by_brand_then_year), "year")),
]
for label, value in rows:
    print(f"{label:<37}: {value}")
fleet.sort(key=lambda car: car.plate)    # сортировка на месте по lambda
print(f"{'fleet.sort(key=lambda car: car.plate)':<37}: {[car.plate for car in fleet]}")

print("\nfilter(is_available):", [car.plate for car in filter(is_available, fleet)])
print("filter(is_truck):    ", [car.plate for car in filter(is_truck, fleet)])

# ---------------------------------------------------------------------------
header("Сценарий 2. map(), фабрика функций, sort_by / filter_by, lambda")

print("map(номер):", list(map(lambda car: car.plate, fleet)))
print("map(возраст):", list(map(lambda car: Car.MAX_YEAR - car.year, fleet)))

up_to_150k = make_mileage_filter(150_000)       # фабрика вернула новую функцию
print("\nup_to_150k = make_mileage_filter(150_000)")
print("up_to_150k(camry):", up_to_150k(camry), "| up_to_150k(kamaz):", up_to_150k(kamaz))
print("fleet.filter_by(up_to_150k):", [car.plate for car in fleet.filter_by(up_to_150k)])
print("fleet.sort_by(by_mileage):  ", show(fleet.sort_by(by_mileage), "mileage"))

named = [car.plate for car in fleet.sort_by(by_year)]
anonymous = [car.plate for car in fleet.sort_by(lambda car: car.year)]
print("\nsort_by(by_year) == sort_by(lambda car: car.year):", named == anonymous)

# ---------------------------------------------------------------------------
header("Сценарий 3. Цепочка filter -> sort -> apply")

step1 = fleet.filter_by(is_available)
print("1) filter_by(is_available):       ", [car.plate for car in step1])
step2 = step1.sort_by(by_mileage, reverse=True)
print("2) sort_by(by_mileage, reverse):  ", show(step2, "mileage"))
step3 = step2.apply(CostEstimator(250))
print("3) apply(CostEstimator(250)), руб.:", step3)

result = (fleet
          .filter_by(is_available)
          .sort_by(by_mileage, reverse=True)
          .apply(CostEstimator(250)))
print("То же одной цепочкой:              ", result)

# ---------------------------------------------------------------------------
header("Сценарий 4. Замена стратегии без изменения кода коллекции")

strategies = [
    ("CostEstimator(100)", CostEstimator(100)),
    ("CostEstimator(500)", CostEstimator(500)),
    ("lambda car: car.year", lambda car: car.year),
    ("SendToServiceIfWorn(200000)", SendToServiceIfWorn(200_000)),
]
for name, strategy in strategies:              # метод apply один и тот же
    print(f"apply({name}):")
    print("   ", fleet.apply(strategy))
print("Свободных машин после SendToServiceIfWorn:", len(fleet.filter_by(is_available)))

# ---------------------------------------------------------------------------
header("Сценарий 5. Callable-объект как стратегия")

estimator = CostEstimator(300)
print("callable(estimator):", callable(estimator))
print("estimator(kamaz):", estimator(kamaz), "руб. — объект вызывается как функция")
estimator.distance = 50
print("estimator.distance = 50 -> estimator(kamaz):", estimator(kamaz), "руб.")
print("Тот же объект как ключ сортировки (дешевле -> дороже):")
print("   ", [car.plate for car in sorted(fleet, key=estimator)])
