"""ЛР-7. Собственные исключения предметной области «Автопарк».

Зачем свои классы, если есть ValueError? Чтобы верхний слой (CLI) мог
отличить «ошибка автопарка, покажи пользователю сообщение» от настоящей
ошибки программиста (KeyError, AttributeError…), которую скрывать нельзя.

Все исключения наследуются от FleetError, поэтому в CLI достаточно одного
`except FleetError` для всех ожидаемых ситуаций.
"""


class FleetError(Exception):
    """Базовое исключение автопарка. Ловим его — ловим все остальные."""


class CarNotFoundError(FleetError):
    """Машина с таким гос. номером не найдена."""

    def __init__(self, plate: str) -> None:
        super().__init__(f"Машина с номером {plate} не найдена")
        self.plate = plate


class DuplicateCarError(FleetError):
    """Машина с таким гос. номером уже есть в автопарке."""

    def __init__(self, plate: str) -> None:
        super().__init__(f"Машина с номером {plate} уже есть в автопарке")
        self.plate = plate


class InvalidCarDataError(FleetError):
    """Данные машины не прошли валидацию (тип или диапазон)."""


class CarStateError(FleetError):
    """Операция недопустима в текущем состоянии машины (в ремонте, в поездке…)."""


class UnknownStrategyError(FleetError):
    """Запрошена сортировка/фильтр, которых нет."""


class StorageError(FleetError):
    """Не удалось прочитать или записать файл с данными."""
