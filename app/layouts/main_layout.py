from PyQt6.QtWidgets import QHBoxLayout, QStackedWidget, QVBoxLayout
from app.core.router import AppRoutes, router
from app.layouts.sidebar import Sidebar
from app.layouts.footer import Footer

class MainLayout(QVBoxLayout):
    def __init__(self, parent):
        super().__init__(parent)

        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)

        self.body_layout = QHBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.footer = Footer()
        self.content = QStackedWidget()

        for _, view in router.get_all_routes().items():
            self.content.addWidget(view)

        self.body_layout.addWidget(self.sidebar)
        self.body_layout.addWidget(self.content, 1)

        self.addLayout(self.body_layout, 1)
        self.addWidget(self.footer)

        initial_route = router.get_initial_route()
        if initial_route is not None:
            self.show_page(initial_route.value)

    def show_page(self, route_value: str) -> None:
        route = AppRoutes.from_value(route_value)
        if route is None:
            return
        self.content.setCurrentWidget(router.get_route(route))
