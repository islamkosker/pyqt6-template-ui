from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QVBoxLayout, QWidget

from app.core.theme import Theme, ThemeManager
from app.layouts.topbar import TopBar
from app.widgets.pill_divider import PillDivider

class ViewLayout(QWidget):

    def __init__(self, title: str | None = None):
        super().__init__()
        self.setObjectName("ViewSurface")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)

        self.top_bar: TopBar | None = None
        if title:
            self.top_bar = TopBar(title)
            self.root.addWidget(self.top_bar)

        self.divider_wrap = QWidget()
        self.divider_wrap.setObjectName("TopBarDividerWrap")
        self.divider_wrap.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        divider_layout = QHBoxLayout(self.divider_wrap)
        divider_layout.setContentsMargins(24, 0, 24, 0)
        divider_layout.setSpacing(0)

        self.divider = PillDivider(self._divider_color())
        self.divider.setObjectName("TopBarDivider")
        divider_layout.addWidget(self.divider)
        self.root.addWidget(self.divider_wrap)

        self.main_content = QWidget()
        self.main_content.setObjectName("ViewMainContent")
        self.main_content.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.main_content.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.main_layout = QVBoxLayout(self.main_content)
        self.main_layout.setContentsMargins(24, 0, 24, 24)
        self.main_layout.setSpacing(20)
        self.root.addWidget(self.main_content, 1)

    def _divider_color(self) -> QColor:
        manager = ThemeManager.instance()
        is_dark = manager is not None and manager.get_current_theme() == Theme.DARK
        return QColor("#30363d" if is_dark else "#e5e7eb")

    def on_theme_changed(self) -> None:
        self.divider.setColor(self._divider_color())
