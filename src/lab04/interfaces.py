"""ЛР-4. Интерфейсы — контракты поведения на основе abc.ABC.

Интерфейс только перечисляет обязательные методы. Если класс наследует
интерфейс и не реализует хотя бы один @abstractmethod, объект такого класса
создать нельзя: Python бросит TypeError.
"""

from abc import ABC, abstractmethod


class Printable(ABC):
    """Контракт: объект умеет описать себя строкой."""

    @abstractmethod
    def display(self):
        """Вернуть описание объекта одной строкой."""


class Earnable(ABC):
    """Контракт: объект приносит доход."""

    @abstractmethod
    def income(self, distance):
        """Сколько рублей приносит рейс длиной distance км."""
