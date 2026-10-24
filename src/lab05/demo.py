"""ЛР-5. Сценарии: функции как аргументы, map/filter/sorted, фабрики, паттерн Стратегия, цепочки."""

from collection import Fleet
from models import Car, Taxi, Truck
from strategies import (
    CostEstimator, FullRefuel, SendToServiceIfWorn, TestDrive, TopUpTo,
    by_brand_then_year, by_mileage, by_plate, by_year,
    is_available, is_commercial, is_low_fuel, is_taxi,
    make_brand_filter, make_max_mileage_filter, make_min_year_filter,
    to_plate, to_short_string, to_summary_dict,
)


def header(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def show(title, cars):
    """Напечатать список машин одной строкой на машину."""
    print(f"{title}:")
    for car in cars:
        print(f"    {car.year}  {car.mileage:>7} км  {car.fuel_percent:5.1f} %  {type(car).__name__:5} {car.brand} {car.model} ({car.plate})")


def build_fleet():
    fleet = Fleet("Автопарк «Стрела»")
    for car in (
        Car("А123ВС777", "Toyota", "Camry", 2018, 145300, 62, 40),
        Car("В777АА199", "Lada", "Vesta", 2021, 30000, 55, 55),
        Taxi("Т001ТТ77", "Skoda", "Octavia", 2022, tariff=35, mileage=90000, fuel_level=45),
        Taxi("Т002ТТ77", "Kia", "Rio", 2021, tariff=28, mileage=12000, fuel_level=8),
        Truck("Н500НН50", "KamAZ", "5490", 2020, max_load=20000, mileage=400000, tank_capacity=400, fuel_level=60),
        Car("М222ММ22", "Lada", "Granta", 2016, 210000, 50, 10),
    ):
        fleet.add(car)
    return fleet


# ---------------------------------------------------------------------------
header("Сценарий 1. Три стратегии сортировки и два фильтра (задание на 3)")

fleet = build_fleet()
show("Исходный парк", fleet)

# Передаём ССЫЛКУ на функцию: by_year, а не by_year() — вызывать будет sorted.
show("\nsorted(fleet, key=by_year)", sorted(fleet, key=by_year))
show("\nsorted(fleet, key=by_mileage, reverse=True)", sorted(fleet, key=by_mileage, reverse=True))
show("\nsorted(fleet, key=by_brand_then_year)", sorted(fleet, key=by_brand_then_year))

show("\nlist(filter(is_available, fleet))", list(filter(is_available, fleet)))
show("list(filter(is_low_fuel, fleet))", list(filter(is_low_fuel, fleet)))
show("list(filter(is_taxi, fleet)) — фильтр по типу", list(filter(is_taxi, fleet)))

# ---------------------------------------------------------------------------
header("Сценарий 2. map(), фабрики функций, sort_by/filter_by, lambda (задание на 4)")

print("map(to_short_string, fleet):")
print("   ", list(map(to_short_string, fleet)))
print("map(to_plate, fleet):")
print("   ", list(map(to_plate, fleet)))
print("map(to_summary_dict, fleet)[0]:")
print("   ", list(map(to_summary_dict, fleet))[0])

print("\nФабрика функций: один и тот же код, разные пороги")
not_older_than_2020 = make_min_year_filter(2020)
not_older_than_2018 = make_min_year_filter(2018)
print(f"    make_min_year_filter(2020) -> {type(not_older_than_2020).__name__}, "
      f"не старше 2020: {len(list(filter(not_older_than_2020, fleet)))} шт., "
      f"не старше 2018: {len(list(filter(not_older_than_2018, fleet)))} шт.")
show("    filter(make_brand_filter('lada'))", filter(make_brand_filter("lada"), fleet))
show("    filter(make_max_mileage_filter(100000))", filter(make_max_mileage_filter(100000), fleet))

print("\nМетоды коллекции принимают функции:")
show("fleet.sort_by(by_plate)", fleet.sort_by(by_plate))
show("fleet.filter_by(is_commercial)", fleet.filter_by(is_commercial))
print(f"Исходный парк не тронут: {len(fleet)} машин, "
      f"а filter_by вернул новый {type(fleet.filter_by(is_commercial)).__name__}")

print("\nlambda и именованная функция дают одно и то же:")
via_lambda = [car.plate for car in sorted(fleet, key=lambda car: car.mileage)]
via_named = [car.plate for car in sorted(fleet, key=by_mileage)]
print(f"    key=lambda car: car.mileage -> {via_lambda}")
print(f"    key=by_mileage              -> {via_named}")
print(f"    результаты равны: {via_lambda == via_named}")

# ---------------------------------------------------------------------------
header("Сценарий 3. Цепочка filter -> sort -> apply с выводом на каждом шаге (задание на 5)")

def prepare():
    """Парк, в котором не все свободны: Vesta в ремонте, Camry в поездке."""
    fleet = build_fleet()
    fleet.find_by_plate("В777АА199").send_to_service()
    fleet.find_by_plate("А123ВС777").start_trip()
    return fleet


fleet = prepare()
show("Исходный парк (Vesta в ремонте, Camry в поездке)", fleet)
step1 = fleet.filter_by(is_available)
show("\n1) filter_by(is_available)", step1)
step2 = step1.sort_by(by_mileage, reverse=True)
show("\n2) .sort_by(by_mileage, reverse=True)", step2)
refuel = FullRefuel()
step3 = step2.apply(refuel)
show(f"\n3) .apply(FullRefuel()) — заправлено {refuel.refueled} машин", step3)

print("\nТо же самое одной цепочкой:")
result = (prepare()
          .filter_by(is_available)
          .sort_by(by_mileage, reverse=True)
          .apply(FullRefuel()))
show("   result", result)

# ---------------------------------------------------------------------------
header("Сценарий 4. Замена стратегии без изменения кода коллекции")

print("Код коллекции один: fleet.apply(<стратегия>). Меняем только то, что передаём.\n")
fleet = build_fleet()
fleet.apply(TopUpTo(50))
show("apply(TopUpTo(50))", fleet)

fleet = build_fleet()
fleet.apply(SendToServiceIfWorn(200000))
print("\napply(SendToServiceIfWorn(200000)):")
for car in fleet:
    print(f"    {car.plate}: {car.status}")

fleet = build_fleet()
fleet.apply(lambda car: car.send_to_service() if car.fuel_percent < 20 else None)
print("\napply(lambda ...) — стратегией может быть и лямбда:")
for car in fleet:
    print(f"    {car.plate}: {car.status}")

# ---------------------------------------------------------------------------
header("Сценарий 5. Callable-объект как стратегия")

fleet = build_fleet()
drive = TestDrive(50)
print(f"callable(drive) = {callable(drive)}, callable(by_year) = {callable(by_year)}")
fleet.apply(drive)
show(f"apply(TestDrive(50)) — всего наезжено {drive.total_km} км", fleet)

print("\nCostEstimator(100) через map(): объект-стратегия хранит параметр distance")
for line, cost in zip(fleet.map(to_short_string), fleet.map(CostEstimator(100))):
    print(f"    {line:28} -> {cost:8.0f} руб")

print("\nПередать не-функцию нельзя:")
try:
    fleet.apply("заправить всех")
except TypeError as error:
    print(f"    TypeError: {error}")
