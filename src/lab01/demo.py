"""ЛР-1. Сценарии работы с классом Car.

Только сценарии: создание объектов, вызовы методов, печать.
Логика класса — в model.py, проверки — в validate.py.
"""

from model import Car


def header(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


def try_it(description, action):
    """Выполнить действие, которое должно упасть, и показать текст ошибки."""
    try:
        action()
        print(f"  {description:<27} -> ошибки нет")
    except (TypeError, ValueError, AttributeError) as error:
        print(f"  {description:<27} -> {type(error).__name__}: {error}")


# ---------------------------------------------------------------------------
header("Сценарий 1. Создание объекта, print, repr, атрибуты класса")

camry = Car("а123вс777", "Toyota", "Camry", 2018, 145300)
vesta = Car("В777АА199", "Lada", "Vesta", 2021, 30000)

print("print(camry):", camry)
print("repr(camry): ", repr(camry))
print("Номер приведён к верхнему регистру:", camry.plate)
print("Атрибут класса через класс:     Car.FUEL_PRICE   =", Car.FUEL_PRICE)
print("Атрибут класса через экземпляр: camry.FUEL_PRICE =", camry.FUEL_PRICE)

camry.FUEL_PRICE = 70.0     # присваивание через экземпляр создаёт его СОБСТВЕННЫЙ атрибут
print("После camry.FUEL_PRICE = 70.0:",
      f"camry -> {camry.FUEL_PRICE}, vesta -> {vesta.FUEL_PRICE}, Car -> {Car.FUEL_PRICE}")
del camry.FUEL_PRICE        # убираем атрибут экземпляра, снова виден атрибут класса

print("Создано машин (Car.total_created):", Car.total_created)

# ---------------------------------------------------------------------------
header("Сценарий 2. Сравнение объектов")

same_plate = Car("А123ВС777", "Toyota", "Camry", 2018, 150000)

print("camry == same_plate:", camry == same_plate, "(номер тот же, пробег другой)")
print("camry is same_plate:", camry is same_plate, "(это два разных объекта)")
print("camry == vesta:     ", camry == vesta)
print("camry == 'А123ВС777':", camry == "А123ВС777", "(строка — не машина)")
print("len({camry, same_plate, vesta}) =", len({camry, same_plate, vesta}),
      "(дубликат по номеру в set не попал)")

# ---------------------------------------------------------------------------
header("Сценарий 3. Валидация: конструктор и сеттер")

created_before = Car.total_created
try_it("номер — число", lambda: Car(123, "Toyota", "Camry", 2018))
try_it("номер из 3 символов", lambda: Car("А12", "Toyota", "Camry", 2018))
try_it("пустая марка", lambda: Car("А001АА77", "   ", "Camry", 2018))
try_it("год 1800", lambda: Car("А001АА77", "Lada", "Niva", 1800))
try_it("год True", lambda: Car("А001АА77", "Lada", "Niva", True))
try_it("пробег -5", lambda: Car("А001АА77", "Lada", "Niva", 2020, -5))
print("Неудачные попытки не посчитаны:", Car.total_created == created_before)

camry.mileage = 146000
print("camry.mileage = 146000 ->", camry.mileage)
try_it("camry.mileage = 100", lambda: setattr(camry, "mileage", 100))
try_it("camry.mileage = 'много'", lambda: setattr(camry, "mileage", "много"))
try_it("camry.year = 2025", lambda: setattr(camry, "year", 2025))

# ---------------------------------------------------------------------------
header("Сценарий 4. Состояние объекта и поведение, зависящее от него")

print("Исходно:", vesta)
vesta.drive(120)
print("После drive(120):", vesta.mileage, "км")
print(f"Стоимость топлива на 250 км: {vesta.trip_cost(250):.2f} руб.")

vesta.send_to_service()
print("После send_to_service():", vesta.status)
try_it("drive(10) в ремонте", lambda: vesta.drive(10))
try_it("повторный send_to_service", vesta.send_to_service)

vesta.finish_service()
print("После finish_service():", vesta.status)
vesta.drive(10)
print("Снова можно ехать, пробег:", vesta.mileage, "км")
try_it("finish_service не в ремонте", vesta.finish_service)
try_it("drive(0)", lambda: vesta.drive(0))
