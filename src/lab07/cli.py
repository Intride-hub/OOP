"""ЛР-7. Консольный интерфейс: меню, ввод и вывод.

Бизнес-логики здесь нет, и к коллекции CLI не обращается: он спрашивает
пользователя, вызывает метод FleetApp и печатает результат.
"""

from collections.abc import Callable
from typing import Any

from app import FleetApp
from exceptions import FleetError, InvalidCarDataError
from models import Car

MENU = """
========================= АВТОПАРК =========================
 1. Показать все        2. Добавить            3. Найти по номеру
 4. Фильтровать         5. Сортировать         6. Ремонт: в / из
 7. Удалить             0. Выход с сохранением"""

KINDS = {"1": "car", "2": "taxi", "3": "truck"}
SORT_KEYS = {"1": "year", "2": "mileage", "3": "brand"}


class FleetCLI:
    """Меню в цикле: показать пункты -> выполнить выбранный -> снова меню."""

    def __init__(self, app: FleetApp) -> None:
        self._app = app
        self._actions: dict[int, Callable[[], None]] = {
            1: self.show_all,
            2: self.add_car,
            3: self.find_car,
            4: self.filter_cars,
            5: self.sort_cars,
            6: self.toggle_service,
            7: self.remove_car,
        }

    def run(self) -> None:
        """Загрузить данные, крутить меню до выхода, при выходе сохранить."""
        try:
            print(f"Загружено машин из файла: {self._app.load()}")
        except FleetError as error:
            print(f"Ошибка: {error}. Исправьте или удалите файл и запустите снова.")
            return
        try:
            self._loop()
        except (KeyboardInterrupt, EOFError):    # Ctrl+C или конец ввода — тоже выход
            print()
        try:
            self._app.save()
            print("Данные сохранены. До свидания!")
        except FleetError as error:
            print(f"Ошибка: {error}")

    def _loop(self) -> None:
        """Цикл меню до выбора пункта 0."""
        while True:
            print(MENU)
            try:
                choice = int(input("Выберите пункт: "))
            except ValueError:
                print("Ошибка: введите число")
                continue
            if choice == 0:
                return
            action = self._actions.get(choice)
            if action is None:
                print("Ошибка: нет такого пункта меню")
                continue
            try:
                action()
            except FleetError as error:      # любое наше исключение: показать и продолжить
                print(f"Ошибка ({type(error).__name__}): {error}")

    # --- пункты меню ---

    def show_all(self) -> None:
        """1. Показать все машины таблицей."""
        self._print_table(self._app.all_cars())

    def add_car(self) -> None:
        """2. Спросить тип и данные машины и добавить её."""
        kind = KINDS.get(input("Тип (1 — легковая, 2 — такси, 3 — грузовик): ").strip())
        if kind is None:
            raise InvalidCarDataError("нет такого типа машины")
        params: dict[str, Any] = {
            "plate": input("Гос. номер: "),
            "brand": input("Марка: "),
            "model": input("Модель: "),
            "year": self._ask_int("Год выпуска: "),
            "mileage": self._ask_int("Пробег, км [0]: ", default=0),
        }
        if kind == "taxi":
            params["tariff"] = self._ask_float("Тариф, руб/км: ")
            params["seats"] = self._ask_int("Мест для пассажиров [4]: ", default=4)
        elif kind == "truck":
            params["max_load"] = self._ask_float("Грузоподъёмность, кг: ")
        car = self._app.add_car(kind, params)
        print(f"Добавлено: {car}")

    def find_car(self) -> None:
        """3. Найти машину по номеру и показать подробно."""
        car = self._app.find(input("Гос. номер: "))
        print(car.display())

    def filter_cars(self) -> None:
        """4. Выбрать фильтр и показать подходящие машины."""
        choice = input("Фильтр (1 — в гараже, 2 — грузовики, 3 — пробег не больше N км): ").strip()
        if choice == "1":
            cars = self._app.filter("available")
        elif choice == "2":
            cars = self._app.filter("trucks")
        elif choice == "3":
            cars = self._app.filter_by_mileage(self._ask_int("N, км: "))
        else:
            raise InvalidCarDataError("нет такого фильтра")
        self._print_table(cars)

    def sort_cars(self) -> None:
        """5. Выбрать стратегию сортировки и показать результат."""
        key = SORT_KEYS.get(input("Сортировать (1 — по году, 2 — по пробегу, 3 — по марке и году): ").strip())
        if key is None:
            raise InvalidCarDataError("нет такой сортировки")
        self._print_table(self._app.sort(key))

    def toggle_service(self) -> None:
        """6. Отправить машину в ремонт или вернуть из ремонта."""
        car = self._app.toggle_service(input("Гос. номер: "))
        print(f"{car.plate}: теперь {car.status}")

    def remove_car(self) -> None:
        """7. Удалить машину после подтверждения y/n."""
        car = self._app.find(input("Гос. номер: "))
        answer = input(f'Удалить "{car.brand} {car.model} ({car.plate})"? (y/n): ')
        if answer.strip().lower() == "y":
            self._app.remove(car.plate)
            print("Удалено.")
        else:
            print("Удаление отменено.")

    # --- помощники ввода и вывода ---

    @staticmethod
    def _ask_int(prompt: str, default: int | None = None) -> int:
        """Спросить целое число; пустой ввод -> default, если он задан."""
        text = input(prompt).strip()
        if not text and default is not None:
            return default
        try:
            return int(text)
        except ValueError:
            raise InvalidCarDataError(f"ожидалось целое число, введено {text!r}") from None

    @staticmethod
    def _ask_float(prompt: str) -> float:
        """Спросить число (можно с запятой: 27,5)."""
        text = input(prompt).strip().replace(",", ".")
        try:
            return float(text)
        except ValueError:
            raise InvalidCarDataError(f"ожидалось число, введено {text!r}") from None

    @staticmethod
    def _print_table(cars: list[Car]) -> None:
        """Напечатать машины таблицей."""
        if not cars:
            print("Машин нет.")
            return
        print(f"{'№':>2}  {'Тип':<5}  {'Номер':<9}  {'Марка и модель':<16}  {'Год':>4}  "
              f"{'Пробег, км':>10}  Статус")
        print("-" * 70)
        for number, car in enumerate(cars, start=1):
            name = f"{car.brand} {car.model}"
            mileage = f"{car.mileage:,}".replace(",", " ")
            print(f"{number:>2}  {type(car).__name__:<5}  {car.plate:<9}  {name:<16}  "
                  f"{car.year:>4}  {mileage:>10}  {car.status}")
        print(f"Всего: {len(cars)}")
