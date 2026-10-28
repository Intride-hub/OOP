"""ЛР-7. Точка входа: python main.py"""

from pathlib import Path

from app import FleetApp
from cli import FleetCLI

# Файл с данными лежит рядом с main.py, из какой бы папки ни запускали программу.
DATA_FILE = Path(__file__).with_name("fleet.json")


def main() -> None:
    """Собрать приложение из слоёв и запустить меню."""
    FleetCLI(FleetApp(str(DATA_FILE))).run()


if __name__ == "__main__":
    main()
