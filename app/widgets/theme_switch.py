from pathlib import Path

from PyQt6.QtCore import QPropertyAnimation, QSize, Qt, pyqtProperty
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton


class ThemeSwitch(QPushButton):
    LIGHT_ICON_PATH = Path("app/assets/icons/light.svg")
    DARK_ICON_PATH = Path("app/assets/icons/dark.svg")

    def __init__(self):
        super().__init__()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(36, 36)
        self.setCheckable(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._base_icon_size = 18
        self._icon_scale = 1.0
        self.setIconSize(QSize(self._base_icon_size, self._base_icon_size))
        self.setObjectName("ThemeToggleButton")
        self._light_icon = QIcon(str(self.LIGHT_ICON_PATH))
        self._dark_icon = QIcon(str(self.DARK_ICON_PATH))

        self._shrink_animation = QPropertyAnimation(self, b"iconScale")
        self._shrink_animation.setDuration(90)
        self._shrink_animation.setStartValue(1.0)
        self._shrink_animation.setEndValue(0.72)

        self._grow_animation = QPropertyAnimation(self, b"iconScale")
        self._grow_animation.setDuration(90)
        self._grow_animation.setStartValue(0.72)
        self._grow_animation.setEndValue(1.0)

        self._pending_checked = self.isChecked()
        self.toggled.connect(self._animate_icon_change)
        self._shrink_animation.finished.connect(self._on_shrink_finished)
        self._update_icon(self.isChecked())

    def _update_icon(self, checked: bool) -> None:
        self.setIcon(self._dark_icon if checked else self._light_icon)

    def sync_checked(self, checked: bool) -> None:
        self._shrink_animation.stop()
        self._grow_animation.stop()
        self.blockSignals(True)
        self.setChecked(checked)
        self.blockSignals(False)
        self.iconScale = 1.0
        self._update_icon(checked)

    def _animate_icon_change(self, checked: bool) -> None:
        self._pending_checked = checked
        self._grow_animation.stop()
        self._shrink_animation.stop()
        self._shrink_animation.start()

    def _on_shrink_finished(self) -> None:
        self._update_icon(self._pending_checked)
        self._grow_animation.start()

    def get_icon_scale(self) -> float:
        return self._icon_scale

    def set_icon_scale(self, value: float) -> None:
        self._icon_scale = value
        icon_size = max(12, int(self._base_icon_size * value))
        self.setIconSize(QSize(icon_size, icon_size))

    iconScale = pyqtProperty(float, fget=get_icon_scale, fset=set_icon_scale)
