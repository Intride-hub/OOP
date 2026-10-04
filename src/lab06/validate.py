"""ЛР-6 (с аннотациями). Проверки корректности данных для класса Car.

Правило для всех функций: сначала проверяем ТИП, потом ЗНАЧЕНИЕ.
Если сделать наоборот, то выражение вроде `"пять" < 0` упадёт с невнятной
ошибкой сравнения строки и числа, и пользователь не поймёт, что не так.

Каждая функция либо возвращает проверенное (и при необходимости
нормализованное) значение, либо бросает исключение:
  * TypeError  — пришёл не тот тип;
  * ValueError — тип верный, но значение бессмысленное.

Функции начинаются с подчёркивания: это внутренний инструмент модели,
а не публичный API.
"""

_PLATE_MIN_LENGTH: int = 6       # минимум символов в гос. номере
_PLATE_MAX_LENGTH: int = 9       # максимум (А123ВС777 — ровно 9)
_TEXT_MAX_LENGTH: int = 50       # марка/модель длиннее — почти наверняка ошибка
_TANK_MAX_CAPACITY: float = 500.0  # литров; больше не бывает даже у грузовиков


# --- общие проверки типа (написаны один раз, используются везде) ---

def _ensure_str(value: object, field_name: str) -> str:
    """Убедиться, что value — непустая строка. Возвращает её без пробелов по краям."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name}: ожидалась строка, получено {type(value).__name__}")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name}: строка не может быть пустой")
    return value


def _ensure_int(value: object, field_name: str) -> int:
    """Убедиться, что value — целое число (bool не считается!)."""
    # bool — подкласс int: isinstance(True, int) == True.
    # Без первой проверки Car(..., year=True) создал бы машину 1-го года выпуска.
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name}: ожидалось целое число, получено {type(value).__name__}")
    return value


def _ensure_number(value: object, field_name: str) -> float:
    """Убедиться, что value — число (int или float, но не bool). Возвращает float."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name}: ожидалось число, получено {type(value).__name__}")
    return float(value)


# --- проверки конкретных полей: поверх типа добавляют правило диапазона ---

def _validate_plate(plate: object) -> str:
    """Гос. номер: непустая строка 6–9 символов. Нормализуется к верхнему регистру без пробелов."""
    plate = _ensure_str(plate, "Гос. номер")
    plate = plate.upper().replace(" ", "")
    if not (_PLATE_MIN_LENGTH <= len(plate) <= _PLATE_MAX_LENGTH):
        raise ValueError(
            f"Гос. номер: ожидалось от {_PLATE_MIN_LENGTH} до {_PLATE_MAX_LENGTH} "
            f"символов, получено {len(plate)} ({plate!r})"
        )
    return plate


def _validate_text(value: object, field_name: str) -> str:
    """Марка, модель и прочий текст: непустая строка разумной длины."""
    value = _ensure_str(value, field_name)
    if len(value) > _TEXT_MAX_LENGTH:
        raise ValueError(f"{field_name}: не длиннее {_TEXT_MAX_LENGTH} символов")
    return value


def _validate_year(year: object, min_year: int, max_year: int) -> int:
    """Год выпуска: целое число в диапазоне [min_year, max_year]."""
    year = _ensure_int(year, "Год выпуска")
    if not (min_year <= year <= max_year):
        raise ValueError(f"Год выпуска: ожидался от {min_year} до {max_year}, получено {year}")
    return year


def _validate_mileage(mileage: object) -> int:
    """Пробег: целое неотрицательное число километров."""
    mileage = _ensure_int(mileage, "Пробег")
    if mileage < 0:
        raise ValueError(f"Пробег не может быть отрицательным, получено {mileage}")
    return mileage


def _validate_tank_capacity(capacity: object) -> float:
    """Объём бака: положительное число литров, не больше разумного максимума."""
    capacity = _ensure_number(capacity, "Объём бака")
    if capacity <= 0:
        raise ValueError(f"Объём бака должен быть больше нуля, получено {capacity}")
    if capacity > _TANK_MAX_CAPACITY:
        raise ValueError(f"Объём бака не больше {_TANK_MAX_CAPACITY} л, получено {capacity}")
    return capacity


def _validate_fuel_level(fuel: object, capacity: float) -> float:
    """Остаток топлива: число от 0 до объёма бака включительно."""
    fuel = _ensure_number(fuel, "Уровень топлива")
    if fuel < 0:
        raise ValueError(f"Уровень топлива не может быть отрицательным, получено {fuel}")
    if fuel > capacity:
        raise ValueError(f"В бак объёмом {capacity} л нельзя залить {fuel} л")
    return fuel


def _validate_distance(distance: object) -> int:
    """Расстояние поездки: целое положительное число километров."""
    distance = _ensure_int(distance, "Расстояние")
    if distance <= 0:
        raise ValueError(f"Расстояние должно быть больше нуля, получено {distance}")
    return distance


def _validate_liters(liters: object) -> float:
    """Объём заправки: положительное число литров."""
    liters = _ensure_number(liters, "Объём заправки")
    if liters <= 0:
        raise ValueError(f"Объём заправки должен быть больше нуля, получено {liters}")
    return liters


def _validate_non_negative_number(value: object, field_name: str) -> float:
    """Неотрицательное число (деньги, тариф, груз). Возвращает float."""
    value = _ensure_number(value, field_name)
    if value < 0:
        raise ValueError(f"{field_name} не может быть отрицательным, получено {value}")
    return value


def _validate_positive_number(value: object, field_name: str) -> float:
    """Строго положительное число (тариф, грузоподъёмность). Возвращает float."""
    value = _ensure_number(value, field_name)
    if value <= 0:
        raise ValueError(f"{field_name} должен быть больше нуля, получено {value}")
    return value
