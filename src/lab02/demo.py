"""ЛР-2. Сценарии работы с коллекцией Fleet."""

from collection import Fleet
from model import Car


def header(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def try_it(description, action):
    """Выполнить действие, которое должно упасть, и показать текст ошибки."""
    try:
        action()
        print(f"  {description:<24} -> ошибки нет")
    except (TypeError, ValueError, IndexError) as error:
        print(f"  {description:<24} -> {type(error).__name__}: {error}")


camry = Car("А123ВС777", "Toyota", "Camry", 2018, 145300)
vesta = Car("В777АА199", "Lada", "Vesta", 2021, 30000)
rio = Car("Е001КХ77", "Kia", "Rio", 2016, 210000)
octavia = Car("М555ОР50", "Skoda", "Octavia", 2020, 88000)
solaris = Car("Т010ТТ97", "Hyundai", "Solaris", 2019, 120500)

# ---------------------------------------------------------------------------
header("Сценарий 1. Добавление, вывод, удаление")

fleet = Fleet()
for car in (camry, vesta, rio, octavia, solaris):
    fleet.add(car)
print(fleet)

fleet.remove(rio)
print("\nПосле remove(rio):")
print(fleet)

# ---------------------------------------------------------------------------
header("Сценарий 2. Проверки коллекции")

try_it("add('Toyota')", lambda: fleet.add("Toyota"))
try_it("add(дубликат номера)", lambda: fleet.add(Car("А123ВС777", "Toyota", "Corolla", 2010)))
try_it("remove(rio) повторно", lambda: fleet.remove(rio))

copy = fleet.get_all()
copy.clear()
print("get_all() отдаёт копию: очистили копию, а в автопарке машин:", len(fleet))

# ---------------------------------------------------------------------------
header("Сценарий 3. Поиск, len(), for, in")

print("find_by_plate('М555ОР50'):", fleet.find_by_plate("М555ОР50"))
print("find_by_plate('Х000ХХ00'):", fleet.find_by_plate("Х000ХХ00"))
print("len(fleet):", len(fleet))
print("Марки через for:", ", ".join(car.brand for car in fleet))
print("camry in fleet:", camry in fleet, "| rio in fleet:", rio in fleet)

# ---------------------------------------------------------------------------
header("Сценарий 4. Индексация и удаление по индексу")

print("fleet[0]: ", fleet[0])
print("fleet[-1]:", fleet[-1])
removed = fleet.remove_at(1)
print("remove_at(1) удалил:", removed.plate)
try_it("remove_at(10)", lambda: fleet.remove_at(10))
fleet.add(vesta)
fleet.add(rio)
print("Вернули vesta и rio для следующего сценария.")
print(fleet)

# ---------------------------------------------------------------------------
header("Сценарий 5. Сортировка и выборки (новый Fleet)")

fleet.sort(key=lambda car: car.year)
print("sort по году:   ", [car.year for car in fleet])
fleet.sort(key=lambda car: car.mileage, reverse=True)
print("sort по пробегу:", [car.mileage for car in fleet], "(по убыванию)")

rio.send_to_service()
camry.send_to_service()
available = fleet.get_available()
in_service = fleet.get_in_service()
print("\nВ гараже:", [car.plate for car in available], "->", type(available).__name__)
print("В ремонте:", [car.plate for car in in_service])
print("Исходный автопарк не изменился, машин:", len(fleet))
