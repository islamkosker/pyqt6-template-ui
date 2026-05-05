from PyQt6.QtWidgets import QMainWindow, QWidget
from app.layouts.main_layout import MainLayout
from app.core.constant.app_constant import AppConstant
from PyQt6.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(AppConstant.APP_NAME.value)
        self.setWindowIcon(QIcon(AppConstant.LOGO_ICO_PATH.value))
        self.resize(1200, 700)
        self.setMinimumSize(1200, 700)

        central = QWidget()
        self.setCentralWidget(central)

        self.layout = MainLayout(central)
        self.layout.sidebar.navigationRequested.connect(self.on_navigation)

    def on_navigation(self, page: str):
        self.layout.show_page(page)
