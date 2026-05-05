import os
import sys

if getattr(sys, "frozen", False):
    _base = getattr(sys, "_MEIPASS", None) or os.path.dirname(sys.executable)
    os.chdir(_base)

from PyQt6.QtWidgets import QApplication

from app.core.theme import ThemeManager
from app.main_window import MainWindow

def main() -> int:
    app = QApplication(sys.argv)
    # Restores last theme from QSettings ("theme" key); applies QSS + titlebar hook.
    ThemeManager(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
