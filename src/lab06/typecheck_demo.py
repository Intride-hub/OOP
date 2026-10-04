"""ЛР-6. Файл с НАМЕРЕННЫМИ ошибками типов — для запуска mypy typecheck_demo.py.
Программа даже не запускается по-настоящему: смысл в том, что mypy находит
все четыре ошибки до запуска. Вывод mypy — в images/lab06/mypy_output.txt."""

from container import TypedCollection, Scorable
from models import Car

cars: TypedCollection[Car] = TypedCollection(Car)
cars.add("Toyota Camry")                      # (1) не Car
plates: list[str] = cars.map(lambda car: car.year)   # (2) map даёт list[int], а не list[str]
first = cars.find(lambda car: car.year > 2020)
print(first.plate)                            # (3) first может быть None

class Rock:
    pass

scorables: TypedCollection[Scorable] = TypedCollection(Scorable)
scorables.add(Rock())                         # (4) у Rock нет score()
