"""ЛР-7. Слой интерфейса: меню, ввод, вывод. Никакой бизнес-логики.

Всё, что делает этот файл: спрашивает пользователя, вызывает FleetApp
и красиво печатает результат. Он не знает, как устроен Fleet, и не
импортирует collection.py.
"""

from __future__ import annotations

from typing import Callable, Optional

from app import FleetApp
from exceptions import FleetError
from models import Car, Taxi, Truck


class FleetCLI:
    """Консольное меню поверх FleetApp."""

    def __init__(self, app: FleetApp) -> None:
        self._app: FleetApp = app
        # Пункты меню: номер -> (подпись, обработчик). Порядок = порядок вывода.
        self._menu: dict[int, tuple[str, Callable[[], None]]] = {
            1: ("Показать все машины", self.show_all),
            2: ("Добавить машину", self.add_car),
            3: ("Найти машину по номеру", self.find_by_plate),
            4: ("Фильтровать", self.filter_cars),
            5: ("Сортировать", self.sort_cars),
            6: ("Операции с машиной (заправка, поездка, ремонт)", self.car_operations),
            7: ("Удалить машину", self.remove_car),
            8: ("Статистика автопарка", self.show_stats),
            0: ("Выход (с сохранением)", self.exit),
        }
        self._running: bool = True

    # ======================================================================
    # Главный цикл
    # ======================================================================

    def run(self) -> None:
        """Загрузить данные, крутить меню, при выходе сохранить."""
        try:
            loaded = self._app.load()
            print(f"Загружено машин из {self._app.storage_path}: {loaded}")
        except FleetError as error:
            print(f"Внимание: {error}. Начинаем с пустого автопарка.")

        while self._running:
            self.print_menu()
            choice = self.ask_int("Выберите пункт: ")
            if choice is None:
                continue
            handler = self._menu.get(choice)
            if handler is None:
                print(f"Нет такого пункта: {choice}")
                continue
            try:
                handler[1]()
            except FleetError as error:
                # Ожидаемая ошибка предметной области — показываем и живём дальше.
                print(f"Ошибка: {error}")

    def print_menu(self) -> None:
        """Напечатать меню."""
        print("\n" + "=" * 44)
        print(f"  АВТОПАРК  ({self._app.count()} машин)")
        print("=" * 44)
        for number, (title, _) in self._menu.items():
            print(f"  {number}. {title}")
        print("-" * 44)

    def exit(self) -> None:
        """Сохранить данные и остановить цикл."""
        saved = self._app.save()
        print(f"Сохранено машин: {saved}. До свидания!")
        self._running = False

    # ======================================================================
    # Вспомогательные функции ввода
    # ======================================================================

    def ask_str(self, prompt: str) -> str:
        """Непустая строка."""
        while True:
            value = input(prompt).strip()
            if value:
                return value
            print("  Пустой ввод. Попробуйте ещё раз.")

    def ask_int(self, prompt: str, default: Optional[int] = None) -> Optional[int]:
        """Целое число. При ошибке — сообщение и None (вызывающий решает, что делать)."""
        raw = input(prompt).strip()
        if raw == "" and default is not None:
            return default
        try:
            return int(raw)
        except ValueError:
            print(f"  Ошибка: введите целое число, а не «{raw}»")
            return None

    def ask_float(self, prompt: str, default: Optional[float] = None) -> Optional[float]:
        """Число с точкой (запятая тоже принимается)."""
        raw = input(prompt).strip().replace(",", ".")
        if raw == "" and default is not None:
            return default
        try:
            return float(raw)
        except ValueError:
            print(f"  Ошибка: введите число, а не «{raw}»")
            return None

    def confirm(self, question: str) -> bool:
        """Подтверждение опасной операции: только 'y' означает «да»."""
        answer = input(f"{question} (y/n): ").strip().lower()
        return answer in ("y", "yes", "д", "да")

    # ======================================================================
    # Вывод
    # ======================================================================

    @staticmethod
    def print_table(cars: list[Car], title: str = "") -> None:
        """Табличный вывод списка машин."""
        if title:
            print(f"\n{title}")
        if not cars:
            print("  (пусто)")
            return
        header = f"  {'№':>2} {'Тип':6} {'Номер':10} {'Марка':9} {'Модель':9} {'Год':>4} {'Пробег, км':>11} {'Бак':>6} {'Статус':10}"
        print(header)
        print("  " + "-" * (len(header) - 2))
        for number, car in enumerate(cars, start=1):
            print(f"  {number:>2} {type(car).__name__:6} {car.plate:10} {car.brand[:9]:9} {car.model[:9]:9} "
                  f"{car.year:>4} {car.mileage:>11,} {car.fuel_percent:>5.0f}% {car.status:10}".replace(",", " "))

    @staticmethod
    def print_card(car: Car) -> None:
        """Подробная карточка одной машины (через полиморфный display())."""
        print()
        print(car.display())
        print(f"    оценка состояния: {car.score():.1f} / 100")

    # ======================================================================
    # Обработчики пунктов меню
    # ======================================================================

    def show_all(self) -> None:
        """1. Показать все машины."""
        self.print_table(self._app.list_cars(), "Все машины:")

    def add_car(self) -> None:
        """2. Добавить машину: спросить тип и поля, передать в app."""
        print("Тип машины: 1 — обычная, 2 — такси, 3 — грузовик")
        kind_choice = self.ask_int("Тип: ")
        kinds = {1: "car", 2: "taxi", 3: "truck"}
        if kind_choice not in kinds:
            print("  Неизвестный тип")
            return
        kind = kinds[kind_choice]

        fields: dict = {}
        fields["plate"] = self.ask_str("Гос. номер: ")
        fields["brand"] = self.ask_str("Марка: ")
        fields["model"] = self.ask_str("Модель: ")
        year = self.ask_int("Год выпуска: ")
        if year is None:
            return
        fields["year"] = year
        mileage = self.ask_int("Пробег, км [0]: ", default=0)
        if mileage is None:
            return
        fields["mileage"] = mileage
        tank = self.ask_float("Объём бака, л [50]: ", default=50.0 if kind != "truck" else 300.0)
        if tank is None:
            return
        fields["tank_capacity"] = tank
        fuel = self.ask_float("Топлива сейчас, л [0]: ", default=0.0)
        if fuel is None:
            return
        fields["fuel_level"] = fuel

        if kind == "taxi":
            tariff = self.ask_float("Тариф, руб/км: ")
            if tariff is None:
                return
            fields["tariff"] = tariff
        elif kind == "truck":
            max_load = self.ask_float("Грузоподъёмность, кг: ")
            if max_load is None:
                return
            fields["max_load"] = max_load

        car = self._app.add_car(kind, fields)
        print(f"Добавлено: {car}")

    def find_by_plate(self) -> None:
        """3. Поиск по номеру (и заодно по марке)."""
        print("Искать: 1 — по гос. номеру, 2 — по марке")
        mode = self.ask_int("Режим: ")
        if mode == 1:
            plate = self.ask_str("Гос. номер: ")
            self.print_card(self._app.get_car(plate))
        elif mode == 2:
            brand = self.ask_str("Марка: ")
            self.print_table(self._app.find_by_brand(brand), f"Машины марки {brand}:")
        else:
            print("  Неизвестный режим")

    def filter_cars(self) -> None:
        """4. Фильтрация: именованные фильтры + фильтры с параметром."""
        options = list(self._app.FILTERS.items())
        print("Фильтр:")
        for number, (_, (title, _)) in enumerate(options, start=1):
            print(f"  {number}. {title}")
        print(f"  {len(options) + 1}. не старше года...")
        print(f"  {len(options) + 2}. по статусу...")
        choice = self.ask_int("Выбор: ")
        if choice is None:
            return
        if 1 <= choice <= len(options):
            name, (title, _) = options[choice - 1]
            self.print_table(self._app.filter_cars(name), f"Фильтр «{title}»:")
        elif choice == len(options) + 1:
            year = self.ask_int("Минимальный год: ")
            if year is not None:
                self.print_table(self._app.filter_by_min_year(year), f"Не старше {year} г.:")
        elif choice == len(options) + 2:
            statuses = (Car.STATUS_GARAGE, Car.STATUS_TRIP, Car.STATUS_SERVICE)
            for number, status in enumerate(statuses, start=1):
                print(f"  {number}. {status}")
            status_choice = self.ask_int("Статус: ")
            if status_choice is not None and 1 <= status_choice <= 3:
                status = statuses[status_choice - 1]
                self.print_table(self._app.filter_by_status(status), f"Статус «{status}»:")
            else:
                print("  Неизвестный статус")
        else:
            print("  Нет такого фильтра")

    def sort_cars(self) -> None:
        """5. Сортировка с выбором стратегии (ЛР-5)."""
        options = list(self._app.SORT_STRATEGIES.items())
        print("Сортировать:")
        for number, (_, (title, _)) in enumerate(options, start=1):
            print(f"  {number}. {title}")
        choice = self.ask_int("Стратегия: ")
        if choice is None or not (1 <= choice <= len(options)):
            print("  Нет такой стратегии")
            return
        name, (title, _) = options[choice - 1]
        descending = self.confirm("По убыванию?")
        self.print_table(self._app.sort_cars(name, descending), f"Сортировка {title}:")

    def car_operations(self) -> None:
        """6. Заправка, поездка, ремонт — состояния из ЛР-1."""
        plate = self.ask_str("Гос. номер: ")
        car = self._app.get_car(plate)
        print(f"  {car}")
        print("  1. Заправить  2. Начать поездку  3. Проехать  4. Завершить поездку")
        print("  5. В ремонт   6. Из ремонта")
        choice = self.ask_int("Операция: ")
        if choice == 1:
            liters = self.ask_float("Литров: ")
            if liters is not None:
                level = self._app.refuel(plate, liters)
                print(f"  Заправлено. В баке {level:.1f} л")
        elif choice == 2:
            self._app.start_trip(plate)
            print("  Поездка начата")
        elif choice == 3:
            distance = self.ask_int("Километров: ")
            if distance is not None:
                used = self._app.drive(plate, distance)
                print(f"  Проехали {distance} км, ушло {used:.1f} л")
        elif choice == 4:
            self._app.finish_trip(plate)
            print("  Поездка завершена, машина в гараже")
        elif choice == 5:
            self._app.send_to_service(plate)
            print("  Машина отправлена в ремонт")
        elif choice == 6:
            self._app.finish_service(plate)
            print("  Ремонт завершён, машина в гараже")
        else:
            print("  Неизвестная операция")

    def remove_car(self) -> None:
        """7. Удаление с подтверждением."""
        plate = self.ask_str("Гос. номер: ")
        car = self._app.get_car(plate)      # CarNotFoundError, если нет
        if not self.confirm(f"Удалить «{car.brand} {car.model} ({car.plate})»?"):
            print("  Отменено")
            return
        self._app.remove_car(plate)
        print(f"  Удалено: {car.plate}")

    def show_stats(self) -> None:
        """8. Сводка по автопарку."""
        s = self._app.stats()
        print("\nСтатистика автопарка:")
        print(f"  всего машин:          {s['total']}")
        print(f"  свободны / в ремонте: {s['available']} / {s['in_service']}")
        print(f"  такси / грузовиков:   {s['taxis']} / {s['trucks']}")
        print(f"  суммарный пробег:     {s['total_mileage']:,} км".replace(",", " "))
        print(f"  выручка коммерческих: {s['total_earnings']:,.0f} руб".replace(",", " "))
        print(f"  выезд всех на 100 км: {s['trip_cost_100']:,.0f} руб".replace(",", " "))
        print(f"  средняя оценка:       {s['avg_score']:.1f} / 100")
