"""ЛР-7. Собственные исключения предметной области.

Все наследуются от FleetError, поэтому CLI достаточно одного
`except FleetError`, чтобы показать пользователю понятное сообщение.
"""


class FleetError(Exception):
    """Базовая ошибка автопарка."""


class CarNotFoundError(FleetError):
    """Машины с таким номером нет в автопарке."""


class DuplicateCarError(FleetError):
    """Машина с таким номером уже есть в автопарке."""


class InvalidCarDataError(FleetError):
    """Некорректные данные: не тот тип или недопустимое значение."""


class StorageError(FleetError):
    """Не удалось прочитать или записать файл с данными."""
