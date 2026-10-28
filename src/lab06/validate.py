"""ЛР-6. Проверки входных данных из ЛР-3, теперь с аннотациями типов.

На вход проверки принимают object — то есть что угодно: именно поэтому
им и нужно проверять тип. На выходе — уже точный тип (str, int, float).
"""


def _validate_text(value: object, field_name: str) -> str:
    """Непустая строка. Пробелы по краям обрезаются."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name}: ожидалась строка, получено {type(value).__name__}")
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name}: пустая строка")
    return value


def _validate_plate(plate: object) -> str:
    """Гос. номер: 6–9 символов, приводится к верхнему регистру без пробелов."""
    text = _validate_text(plate, "Гос. номер").upper().replace(" ", "")
    if not 6 <= len(text) <= 9:
        raise ValueError(f"Гос. номер: ожидалось 6–9 символов, получено {len(text)} ({text!r})")
    return text


def _validate_int(value: object, field_name: str,
                  min_value: int, max_value: int | None = None) -> int:
    """Целое число не меньше min_value и не больше max_value (если он задан)."""
    # bool — подкласс int: без этой проверки год True превратился бы в 1.
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name}: ожидалось целое число, получено {type(value).__name__}")
    if value < min_value:
        raise ValueError(f"{field_name}: ожидалось не меньше {min_value}, получено {value}")
    if max_value is not None and value > max_value:
        raise ValueError(f"{field_name}: ожидалось не больше {max_value}, получено {value}")
    return value


def _validate_year(year: object, min_year: int, max_year: int) -> int:
    """Год выпуска в диапазоне [min_year, max_year]."""
    return _validate_int(year, "Год выпуска", min_year, max_year)


def _validate_mileage(mileage: object) -> int:
    """Пробег: целое число километров, не меньше 0."""
    return _validate_int(mileage, "Пробег", 0)


def _validate_distance(distance: object) -> int:
    """Расстояние поездки: целое число километров, не меньше 1."""
    return _validate_int(distance, "Расстояние", 1)


def _validate_positive(value: object, field_name: str) -> float:
    """Положительное число (int или float). Возвращается как float."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name}: ожидалось число, получено {type(value).__name__}")
    if value <= 0:
        raise ValueError(f"{field_name}: ожидалось больше 0, получено {value}")
    return float(value)
