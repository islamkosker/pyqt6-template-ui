from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.core.constant.app_constant import AppConstant
from app.core.router import AppRoutes, router
from app.core.theme import Theme, ThemeManager
from app.widgets.button import AppButton
from app.widgets.theme_switch import ThemeSwitch

class Sidebar(QFrame):
    navigationRequested = pyqtSignal(str)

    expanded_width = 240
    compact_width = 82

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.is_compact = False
        self.buttons: dict[AppRoutes, AppButton] = {}
        self.route_titles: dict[AppRoutes, str] = {}
        self.route_icons: dict[AppRoutes, str | None] = {}

        self.setMinimumWidth(self.expanded_width)
        self.setMaximumWidth(self.expanded_width)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(8)

        self.header = QFrame()
        self.header.setObjectName("SidebarHeader")
        self.header.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.header_layout = QVBoxLayout(self.header)
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(6)

        self.btn_toggle = self._build_toggle_button()
        self.header_layout.addWidget(self.btn_toggle)

        self.nav_container = QFrame()
        self.nav_container.setObjectName("SidebarNavContainer")
        self.nav_container.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.nav_container_layout = QVBoxLayout(self.nav_container)
        self.nav_container_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_container_layout.setSpacing(6)

        self.nav_scroll = QScrollArea()
        self.nav_scroll.setObjectName("SidebarNavScroll")
        self.nav_scroll.setWidgetResizable(True)
        self.nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.nav_scroll.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.nav_scroll.setWidget(self.nav_container)

        self._build_navigation_buttons()

        self.footer = QFrame()
        self.footer.setObjectName("SidebarFooter")
        self.footer.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.footer_layout = QVBoxLayout(self.footer)
        self.footer_layout.setContentsMargins(0, 0, 0, 0)
        self.footer_layout.setSpacing(5)

        self.theme_switch = ThemeSwitch()
        self.theme_switch.setToolTip(self._get_theme_tooltip())
        self.logo, self.version = self._build_footer_widgets()

        self.footer_layout.addWidget(self.theme_switch, 0, Qt.AlignmentFlag.AlignHCenter)
        self.footer_layout.addWidget(self.logo)
        self.footer_layout.addWidget(self.version)

        self.layout.addWidget(self.header)
        self.layout.addWidget(self.nav_scroll, 1)
        self.layout.addWidget(self.footer)

        self.btn_toggle.clicked.connect(self.toggle_compact)
        self.theme_switch.toggled.connect(self._on_theme_switch_toggled)
        self.theme_switch.sync_checked(ThemeManager.instance().get_current_theme() == Theme.DARK)
        self._update_compact_ui()

        initial_route = router.get_initial_route()
        if initial_route is not None:
            self._set_active(initial_route)

    def _get_width(self):
        return self.width()

    def _set_width(self, width: int):
        self.setFixedWidth(width)

    sidebarWidth = pyqtProperty(int, _get_width, _set_width)

    def _build_toggle_button(self) -> AppButton:
        button = AppButton(
            AppConstant.APP_NAME.value,
            icon=self._build_icon("hamburger"),
            variant="ghost",
            context="sidebar",
            expand_horizontal=True,
            focus_policy=Qt.FocusPolicy.NoFocus,
        )
        button.setProperty("is_header", True)
        return button

    def _build_navigation_buttons(self) -> None:
        self.buttons.clear()
        self.route_titles.clear()
        self.route_icons.clear()
        for route_config in router.get_sidebar_routes():
            button = AppButton(
                route_config.title,
                icon=self._build_icon(route_config.icon),
                variant="ghost",
                context="sidebar",
                expand_horizontal=True,
                focus_policy=Qt.FocusPolicy.NoFocus,
            )
            button.clicked.connect(
                lambda _, route_key=route_config.key: self._emit_navigation(route_key)
            )
            self.buttons[route_config.key] = button
            self.route_titles[route_config.key] = route_config.title
            self.route_icons[route_config.key] = route_config.icon
            self.nav_container_layout.addWidget(button)
        self.nav_container_layout.addStretch(1)

    def _build_footer_widgets(self) -> tuple[QLabel, QLabel]:
        logo = QLabel()
        logo.setObjectName("SidebarLogo")
        pixmap = QPixmap(AppConstant.LOGO_PATH.value)
        if pixmap.isNull():
            logo.setText(AppConstant.APP_NAME.value)
        else:
            logo.setPixmap(
                pixmap.scaled(
                    140,
                    40,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        version = QLabel(AppConstant.APP_VERSION.value)
        version.setObjectName("SidebarVersion")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return logo, version

    def _build_icon(self, icon_name: str | None) -> QIcon:
        icon = ThemeManager.instance().icon(icon_name)
        return icon if not icon.isNull() else QIcon()

    def _set_active(self, active_page: AppRoutes) -> None:
        for route_key, button in self.buttons.items():
            button.setProperty("active", route_key == active_page)
            self._refresh_widget_style(button)

    def _emit_navigation(self, page: AppRoutes) -> None:
        self._set_active(page)
        self.navigationRequested.emit(page.value)

    def _on_theme_switch_toggled(self, checked: bool) -> None:
        desired_theme = Theme.DARK if checked else Theme.LIGHT
        ThemeManager.instance().apply(desired_theme)

    def toggle_compact(self) -> None:
        start = self.width()
        end = self.compact_width if not self.is_compact else self.expanded_width
        next_compact = not self.is_compact

        self.anim = QPropertyAnimation(self, b"sidebarWidth")
        self.anim.setDuration(220)
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        if next_compact:
            self._update_compact_ui(True)
        self.anim.finished.connect(lambda: self._update_compact_ui(next_compact))
        self.anim.start()

        self.is_compact = next_compact

    def _update_compact_ui(self, compact: bool | None = None) -> None:
        compact = self.is_compact if compact is None else compact

        self.btn_toggle.setText("" if compact else f"    {AppConstant.APP_NAME.value.upper()}")
        self.btn_toggle.setProperty("compact", compact)
        self._refresh_widget_style(self.btn_toggle)

        self.theme_switch.setToolTip(self._get_theme_tooltip())

        for route_key, button in self.buttons.items():
            route_title = self.route_titles.get(route_key, route_key.value.capitalize())
            button.setText("" if compact else f"    {route_title}")
            button.setToolTip(route_title if compact else "")
            button.setToolTipDuration(3000 if compact else 0)
            button.setProperty("compact", compact)
            self._refresh_widget_style(button)

        self.theme_switch.setVisible(True)
        self.version.setVisible(not compact)
        self.logo.setVisible(not compact)

    def _refresh_widget_style(self, widget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def on_theme_changed(self) -> None:
        self.btn_toggle.setIcon(self._build_icon("hamburger"))
        self.theme_switch.sync_checked(ThemeManager.instance().get_current_theme() == Theme.DARK)
        self._update_compact_ui()
        for route_key, button in self.buttons.items():
            button.setIcon(self._build_icon(self.route_icons.get(route_key)))

    def _get_theme_tooltip(self) -> str:
        current_theme = ThemeManager.instance().get_current_theme()
        return "Switch to Dark Mode" if current_theme == Theme.LIGHT else "Switch to Light Mode"