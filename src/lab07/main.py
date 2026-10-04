"""ЛР-7. Точка входа: python main.py

Собирает слои вместе: файл данных -> FleetApp (логика) -> FleetCLI (интерфейс).
"""

import os

from app import FleetApp
from cli import FleetCLI

# Файл с данными лежит рядом с main.py, откуда бы ни запускали программу.
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fleet.json")


def main() -> None:
    """Создать приложение и запустить консольное меню."""
    app = FleetApp(DATA_FILE)
    cli = FleetCLI(app)
    cli.run()


if __name__ == "__main__":
    main()
