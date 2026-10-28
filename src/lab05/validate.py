"""ЛР-5 (из ЛР-3 без изменений). Проверки входных данных.

Каждая функция возвращает проверенное значение или бросает исключение:
  TypeError  — пришёл не тот тип;
  ValueError — тип верный, но значение недопустимое.
Сначала проверяем тип, потом значение: иначе сравнение вроде "пять" < 0
упало бы с непонятной ошибкой.
"""


def _validate_text(value, field_name):
    """Непустая строка. Пробелы по краям обрезаются."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name}: ожидалась строка, получено {type(value).__name__}")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name}: пустая строка")
    return value


def _validate_plate(plate):
    """Гос. номер: 6–9 символов, приводится к верхнему регистру без пробелов."""
    plate = _validate_text(plate, "Гос. номер").upper().replace(" ", "")
    if not 6 <= len(plate) <= 9:
        raise ValueError(f"Гос. номер: ожидалось 6–9 символов, получено {len(plate)} ({plate!r})")
    return plate


def _validate_int(value, field_name, min_value, max_value=None):
    """Целое число не меньше min_value и не больше max_value (если он задан)."""
    # bool — подкласс int: без этой проверки год True превратился бы в 1.
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name}: ожидалось целое число, получено {type(value).__name__}")
    if value < min_value:
        raise ValueError(f"{field_name}: ожидалось не меньше {min_value}, получено {value}")
    if max_value is not None and value > max_value:
        raise ValueError(f"{field_name}: ожидалось не больше {max_value}, получено {value}")
    return value


def _validate_year(year, min_year, max_year):
    """Год выпуска в диапазоне [min_year, max_year]."""
    return _validate_int(year, "Год выпуска", min_year, max_year)


def _validate_mileage(mileage):
    """Пробег: целое число километров, не меньше 0."""
    return _validate_int(mileage, "Пробег", 0)


def _validate_distance(distance):
    """Расстояние поездки: целое число километров, не меньше 1."""
    return _validate_int(distance, "Расстояние", 1)


def _validate_positive(value, field_name):
    """Положительное число (int или float). Возвращается как float."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name}: ожидалось число, получено {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{field_name}: ожидалось больше 0, получено {value}")
    return float(value)
