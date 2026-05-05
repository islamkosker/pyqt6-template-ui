from enum import Enum


class AppConstant(Enum):
    APP_NAME = "Test Application"
    APP_VERSION = "1.0.0"
    LOGO_PATH = "app/assets/icons/logo.png"
    LOGO_ICO_PATH = "app/assets/icons/logo.ico"
    FOOTER_TEXT = "© Test Application - IKFlow"
    APP_FONT_SIZE = 9
    APP_STYLES_ROOT_PATH = "app/style"
    APP_ICONS_ROOT_PATH = "app/assets/icons"

class AppRoutes(Enum):
    HOME = "home"

    @classmethod
    def from_value(cls, value: str):
        for route in cls:
            if route.value == value:
                return route
        return None
