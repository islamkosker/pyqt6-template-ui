from dataclasses import dataclass
from enum import Enum
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.feature.home import HomeView


@dataclass(frozen=True)
class SidebarRoute:
    key: "AppRoutes"
    title: str
    icon: str | None = None


class AppRoutes(Enum):
    HOME = "home"

    @classmethod
    def from_value(cls, value: str):
        for route in cls:
            if route.value == value:
                return route
        return None


class PlaceholderView(QWidget):
    def __init__(self, title: str):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(label)


class Router:
    def __init__(self):
        self._route_factories: dict[AppRoutes, Callable[[], QWidget]] = {
            AppRoutes.HOME: HomeView,
        }
        self._route_instances: dict[AppRoutes, QWidget] = {}
        self.sidebar_routes = [
            SidebarRoute(AppRoutes.HOME, "Home", "home"),

        ]

    def get_route(self, route: AppRoutes):
        if route not in self._route_instances:
            factory = self._route_factories[route]
            self._route_instances[route] = factory()
        return self._route_instances[route]

    def get_all_routes(self):
        return {route: self.get_route(route) for route in self._route_factories}

    def get_sidebar_routes(self):
        return list(self.sidebar_routes)

    def get_initial_route(self):
        return AppRoutes.HOME


router = Router()