"""ЛР-1. Сценарии использования класса Car.

Здесь только сценарии: создание объектов, вызовы методов, печать.
Логика класса — в model.py, проверки — в validate.py.
"""

from model import Car


def header(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def expect_error(action, *args, **kwargs):
    """Выполнить действие, которое ДОЛЖНО упасть, и показать текст ошибки."""
    try:
        action(*args, **kwargs)
        print("  !!! ошибки не было, а должна была быть")
    except (TypeError, ValueError) as error:
        print(f"  {type(error).__name__}: {error}")


# ---------------------------------------------------------------------------
header("Сценарий 1. Создание объекта, print, repr, атрибуты класса")

camry = Car("а123вс777", "Toyota", "Camry", 2018, 145300, 62.0, 38.5)
vesta = Car("В777АА199", "Lada", "Vesta", 2021, 30000, 55.0, 55.0)

print("print(camry) ->", camry)
print("repr(camry)  ->", repr(camry))
print("Гос. номер нормализован:", camry.plate)
print(f"Возраст {camry.age} лет, бак {camry.fuel_percent:.1f} %, "
      f"запас хода {camry.range_km:.0f} км, свободна: {camry.is_available}")

print("Атрибут класса через класс:    Car.CATEGORY =", Car.CATEGORY)
print("Атрибут класса через экземпляр: camry.CATEGORY =", camry.CATEGORY)
print("Создано машин (Car.total_created):", Car.total_created)

# ---------------------------------------------------------------------------
header("Сценарий 2. Сравнение объектов")

same_car_later = Car("А123ВС777", "Toyota", "Camry", 2018, 146000, 62.0, 10.0)
print("camry == same_car_later:", camry == same_car_later, "(тот же номер)")
print("camry is same_car_later:", camry is same_car_later, "(но это два разных объекта в памяти)")
print("camry == vesta:", camry == vesta)
print("camry == 'строка':", camry == "строка", "(исключения нет — вернулся NotImplemented -> False)")
print("В множестве из трёх объектов уникальных машин:", len({camry, vesta, same_car_later}))

# ---------------------------------------------------------------------------
header("Сценарий 3. Валидация в конструкторе")

print("Пустой номер:")
expect_error(Car, "", "Toyota", "Camry", 2018)
print("Слишком короткий номер:")
expect_error(Car, "А12", "Toyota", "Camry", 2018)
print("Пустая марка:")
expect_error(Car, "А123ВС777", "   ", "Camry", 2018)
print("Год строкой:")
expect_error(Car, "А123ВС777", "Toyota", "Camry", "2018")
print("Год = True (bool маскируется под int):")
expect_error(Car, "А123ВС777", "Toyota", "Camry", True)
print("Год из будущего:")
expect_error(Car, "А123ВС777", "Toyota", "Camry", 2040)
print("Отрицательный пробег:")
expect_error(Car, "А123ВС777", "Toyota", "Camry", 2018, -5)
print("Топлива больше, чем бак:")
expect_error(Car, "А123ВС777", "Toyota", "Camry", 2018, 0, 50, 60)
print("Счётчик не вырос от неудачных попыток:", Car.total_created)

# ---------------------------------------------------------------------------
header("Сценарий 4. Свойства: сеттер с проверкой и поля только для чтения")

print("Пробег до:", camry.mileage)
camry.mileage = 145800
print("Пробег после camry.mileage = 145800:", camry.mileage)
print("Попытка скрутить одометр:")
expect_error(setattr, camry, "mileage", 100000)
print("Попытка записать пробег строкой:")
expect_error(setattr, camry, "mileage", "много")
print("Попытка сменить гос. номер (свойство без сеттера):")
try:
    camry.plate = "Х000ХХ00"
except AttributeError as error:
    print(f"  AttributeError: {error}")

# ---------------------------------------------------------------------------
header("Сценарий 5. Логическое состояние и поведение, зависящее от него")

print("Статус:", camry.status)
print("Ехать из гаража нельзя:")
expect_error(camry.drive, 100)

camry.start_trip()
print("После start_trip():", camry.status, "| свободна:", camry.is_available)
print("Второй раз выехать нельзя:")
expect_error(camry.start_trip)
print("В ремонт из поездки нельзя:")
expect_error(camry.send_to_service)

used = camry.drive(120)
print(f"Проехали 120 км, ушло {used:.1f} л -> {camry}")
print("Слишком далеко для остатка топлива:")
expect_error(camry.drive, 5000)
print("Заправка 20 л на АЗС по дороге, стало", camry.refuel(20), "л")
print("Переполнить бак нельзя:")
expect_error(camry.refuel, 100)

camry.finish_trip()
camry.send_to_service()
print("После finish_trip() и send_to_service():", camry.status)
print("В ремонте нельзя ни ехать, ни заправляться:")
expect_error(camry.drive, 10)
expect_error(camry.refuel, 5)
camry.finish_service()
print("После finish_service():", camry.status)

print("Пустой бак — выехать нельзя даже из гаража:")
empty = Car("Е111ЕЕ11", "Kia", "Rio", 2020, 0, 45, 0)
expect_error(empty.start_trip)

print("\nИтог:", camry)
