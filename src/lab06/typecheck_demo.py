"""ЛР-6. Файл с НАМЕРЕННЫМИ ошибками типов — для команды `python -m mypy typecheck_demo.py`.

Запускать сам файл не нужно: смысл в том, что mypy находит ошибки ДО запуска,
только по аннотациям. Вывод mypy приведён в README.
"""

from container import Displayable, TypedCollection, cheapest
from models import Car, Taxi

cars: TypedCollection[Car] = TypedCollection(Car)
cars.add("Toyota Camry")                                  # 1) строка — не Car
years: list[str] = cars.map(lambda car: car.year)         # 2) map вернёт list[int], а не list[str]
found = cars.find(lambda car: car.year > 2020)
print(found.plate)                                        # 3) found может быть None


class Rock:
    pass


things: TypedCollection[Displayable] = TypedCollection(Displayable)
things.add(Rock())                                        # 4) у Rock нет display()

taxis: TypedCollection[Taxi] = TypedCollection(Taxi)
best = cheapest(taxis, 100)
print(best.max_load)                                      # 5) у Taxi нет max_load (и best может быть None)
