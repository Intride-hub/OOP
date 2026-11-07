"""ЛР-4. Интерфейсы — контракты поведения на основе abc.ABC.

Интерфейс только перечисляет обязательные методы. Если класс наследует
интерфейс и не реализует хотя бы один @abstractmethod, объект такого класса
создать нельзя: Python бросит TypeError.
"""

from abc import ABC, abstractmethod


class Printable(ABC):

    @abstractmethod
    def display(self):
        """Вернуть описание объекта одной строкой."""


class Earnable(ABC):

    @abstractmethod
    def income(self, distance):
        """Сколько рублей приносит рейс длиной distance км."""
