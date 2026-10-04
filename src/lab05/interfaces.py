"""ЛР-5 (из ЛР-4). Интерфейсы (контракты поведения) на базе abc.ABC.

Интерфейс ничего не делает сам. Он говорит: «класс, который меня наследует,
ОБЯЗАН реализовать вот эти методы». Если не реализовал — Python не даст
создать объект такого класса (TypeError при вызове конструктора).

Три контракта для нашей предметной области:

    Printable   умеет показать себя      -> display()
    Comparable  умеет сравнить себя      -> compare_to(other)
    Earnable    умеет зарабатывать       -> earn(distance), earnings
"""

from abc import ABC, abstractmethod


class Printable(ABC):
    """Объект, который можно показать человеку."""

    @abstractmethod
    def display(self):
        """Вернуть подробное текстовое представление (строку)."""


class Comparable(ABC):
    """Объект, который умеет сравнивать себя с другим такого же рода."""

    @abstractmethod
    def compare_to(self, other):
        """Вернуть отрицательное число, 0 или положительное:
        self < other, self == other, self > other соответственно."""

    # Интерфейс может нести и готовое поведение, построенное на абстрактном
    # методе. Классы-наследники получают его бесплатно.
    def is_greater_than(self, other):
        return self.compare_to(other) > 0

    def is_less_than(self, other):
        return self.compare_to(other) < 0


class Earnable(ABC):
    """Объект, который приносит деньги за пройденное расстояние."""

    @abstractmethod
    def earn(self, distance):
        """Выполнить работу на distance км и вернуть заработанную сумму."""

    @property
    @abstractmethod
    def earnings(self):
        """Сколько заработано всего."""
