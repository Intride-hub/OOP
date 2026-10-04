"""ЛР-7. Сохранение и загрузка автопарка в JSON-файл.

Формат файла — список словарей, по одному на машину. Что именно кладётся
в словарь, решает сама модель (to_dict / from_dict) — storage.py лишь
переводит список словарей в текст и обратно. Ключ "type" говорит,
объект какого класса восстанавливать.
"""

from __future__ import annotations

import json
import os
from typing import Any

from collection import Fleet
from exceptions import StorageError
from models import Car, Taxi, Truck

# Реестр «имя класса -> класс». Добавил новый тип машины — добавь строку сюда.
CAR_TYPES: dict[str, type[Car]] = {
    "Car": Car,
    "Taxi": Taxi,
    "Truck": Truck,
}


def save(fleet: Fleet, filepath: str) -> None:
    """Сохранить коллекцию в JSON-файл (перезаписывает файл целиком)."""
    records: list[dict[str, Any]] = [car.to_dict() for car in fleet]
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(records, file, ensure_ascii=False, indent=2)
    except OSError as error:
        raise StorageError(f"Не удалось записать {filepath}: {error}") from error


def load(filepath: str) -> list[Car]:
    """Загрузить объекты из JSON-файла. Нет файла — пустой список (это не ошибка).

    Испорченная запись не роняет всю загрузку: она пропускается,
    а причина попадает в StorageError только если не удалось прочитать
    сам файл или его структура не список.
    """
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, encoding="utf-8") as file:
            records = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise StorageError(f"Не удалось прочитать {filepath}: {error}") from error
    if not isinstance(records, list):
        raise StorageError(f"Файл {filepath} должен содержать список записей")

    cars: list[Car] = []
    for record in records:
        car = _record_to_car(record)
        if car is not None:
            cars.append(car)
    return cars


def _record_to_car(record: Any) -> Car | None:
    """Словарь -> объект нужного класса; None, если запись испорчена."""
    if not isinstance(record, dict):
        return None
    car_class = CAR_TYPES.get(record.get("type", "Car"))
    if car_class is None:
        return None
    try:
        return car_class.from_dict(record)
    except (KeyError, TypeError, ValueError):
        return None
