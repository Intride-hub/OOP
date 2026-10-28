"""ЛР-7. Сохранение и загрузка автопарка в JSON."""

import json
from pathlib import Path
from typing import Any

from collection import Fleet
from exceptions import StorageError
from models import Car, Taxi, Truck

# Класс выбираем по ключу "type" из файла — без цепочки if/elif.
CAR_TYPES: dict[str, type[Car]] = {"Car": Car, "Taxi": Taxi, "Truck": Truck}


def save(fleet: Fleet, path: str) -> None:
    """Сохранить автопарк в JSON-файл."""
    data = [car.to_dict() for car in fleet]
    try:
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as error:
        raise StorageError(f"не удалось сохранить {path}: {error}") from error


def load(path: str) -> list[Car]:
    """Загрузить машины из JSON-файла. Если файла нет — пустой список."""
    file = Path(path)
    if not file.exists():
        return []
    try:
        raw: list[dict[str, Any]] = json.loads(file.read_text(encoding="utf-8"))
        return [CAR_TYPES[item["type"]].from_dict(item) for item in raw]
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        raise StorageError(f"файл {path} повреждён: {error!r}") from error
