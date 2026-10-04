"""ЛР-2. Сценарии работы с коллекцией Fleet."""

from collection import Fleet
from model import Car


def header(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def expect_error(action, *args, **kwargs):
    try:
        action(*args, **kwargs)
        print("  !!! ошибки не было, а должна была быть")
    except (TypeError, ValueError, IndexError) as error:
        print(f"  {type(error).__name__}: {error}")


# ---------------------------------------------------------------------------
header("Сценарий 1. Добавление, вывод, удаление (задание на 3)")

fleet = Fleet("Автопарк «Стрела»")
camry = Car("А123ВС777", "Toyota", "Camry", 2018, 145300, 62, 38.5)
vesta = Car("В777АА199", "Lada", "Vesta", 2021, 30000, 55, 55)
rio = Car("Е111ЕЕ11", "Kia", "Rio", 2020, 80000, 45, 5)
solaris = Car("К555КК77", "Hyundai", "Solaris", 2019, 60000, 50, 20)
granta = Car("М222ММ22", "Lada", "Granta", 2016, 210000, 50, 30)

for car in (camry, vesta, rio, solaris, granta):
    fleet.add(car)

print(fleet)
print("\nУдаляем Kia Rio...")
fleet.remove(rio)
print(fleet)
print("\nget_all() возвращает обычный список:", type(fleet.get_all()).__name__, len(fleet.get_all()))

# ---------------------------------------------------------------------------
header("Сценарий 2. Проверки при добавлении")

print("Добавляем строку вместо Car:")
expect_error(fleet.add, "Toyota Camry")
print("Добавляем число:")
expect_error(fleet.add, 42)
print("Добавляем дубликат (другой объект, тот же номер, набранный строчными):")
expect_error(fleet.add, Car("а123вс777", "Toyota", "Camry", 2018))
print("Удаляем машину, которой нет:")
expect_error(fleet.remove, rio)
print("В парке по-прежнему", len(fleet), "машины")

# ---------------------------------------------------------------------------
header("Сценарий 3. Поиск, len(), for (задание на 4)")

print("len(fleet) =", len(fleet))
print("find_by_plate('в777аа199') ->", fleet.find_by_plate("в777аа199"))
print("find_by_plate('Х000ХХ00') ->", fleet.find_by_plate("Х000ХХ00"))
print("find_by_brand('lada') ->")
for car in fleet.find_by_brand("lada"):
    print("   ", car)
print("Перебор через for:")
for car in fleet:
    print(f"    {car.plate}: {car.brand} {car.model}, {car.year}")
print("camry in fleet:", camry in fleet, "| rio in fleet:", rio in fleet)

# ---------------------------------------------------------------------------
header("Сценарий 4. Индексация и удаление по индексу (задание на 5)")

print("fleet[0]  ->", fleet[0])
print("fleet[-1] ->", fleet[-1])
print("fleet[1:3] ->", [car.plate for car in fleet[1:3]])
print("Индекс за пределами:")
expect_error(fleet.remove_at, 10)
removed = fleet.remove_at(1)
print("remove_at(1) удалил:", removed.plate)
print(fleet)

# ---------------------------------------------------------------------------
header("Сценарий 5. Сортировка")

fleet.add(vesta)
fleet.add(rio)
print("По умолчанию — по номеру:")
fleet.sort()
print(fleet)
print("\nПо году, новые первыми:")
fleet.sort_by_year(newest_first=True)
print(fleet)
print("\nПо пробегу через универсальный sort(key=...):")
fleet.sort(key=lambda car: car.mileage)
for car in fleet:
    print(f"    {car.mileage:>7} км  {car.brand} {car.model}")

# ---------------------------------------------------------------------------
header("Сценарий 6. Логические выборки возвращают НОВЫЙ автопарк")

camry.start_trip()          # Camry уехала
granta.send_to_service()    # Granta в ремонте
print("Исходный парк:", repr(fleet))
available = fleet.get_available()
print(available)
print()
print(fleet.get_in_service())
print()
print(fleet.get_low_fuel(30))
print("\nИсходный парк не изменился:", len(fleet), "машин, тип выборки:", type(available).__name__)
print("Суммарный пробег парка:", f"{fleet.total_mileage:,}".replace(",", " "), "км")
