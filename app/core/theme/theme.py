from __future__ import annotations

import ctypes
import sys
from enum import Enum, StrEnum
from pathlib import Path
from typing import ClassVar

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QWidget

from app.core.constant.app_constant import AppConstant


class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"


class StyleModule(StrEnum):
    BUTTON = "button"
    SIDEBAR_BUTTON = "sidebar_button"
    SURFACE = "surface"

    def qss_filename(self) -> str:
        return f"{self.value}.qss"


def _parse_theme(raw: str | None) -> Theme:
    try:
        return Theme(raw or Theme.LIGHT.value)
    except ValueError:
        return Theme.LIGHT


def _style_root_path() -> Path:
    return Path(AppConstant.APP_STYLES_ROOT_PATH.value)


def _icons_root_path() -> Path:
    return Path(AppConstant.APP_ICONS_ROOT_PATH.value)


def resolve_icon_path(
    icon_name: str | None,
    theme: Theme | None = None,
    *,
    icons_root: Path | None = None,
) -> str | None:
    """Theme-aware icon lookup (e.g. `name-dark.svg` on dark). Returns absolute path str or None."""
    if not icon_name:
        return None

    root = icons_root if icons_root is not None else _icons_root_path()
    selected = theme or Theme.LIGHT

    icon_path = Path(icon_name)
    stem = icon_path.stem
    suffix = icon_path.suffix.lower()

    candidates: list[str] = []
    if suffix:
        if selected == Theme.DARK and suffix == ".svg":
            candidates.append(f"{stem}-dark.svg")
        candidates.append(icon_name)
        if suffix != ".svg":
            candidates.append(f"{stem}.svg")
        if suffix != ".png":
            candidates.append(f"{stem}.png")
    else:
        if selected == Theme.DARK:
            candidates.append(f"{stem}-dark.svg")
            candidates.append(f"{stem}-dark.png")
        candidates.append(f"{stem}.svg")
        candidates.append(f"{stem}.png")

    for candidate in candidates:
        full = root / candidate
        if full.is_file():
            return str(full.resolve())
    return None


class ThemeManager:
    """
    QSS loading:
    - Default: for each `StyleModule`, `core/<name>.qss` then `<theme>/<name>.qss`.
    - Override: pass `theme_file_lists` like the old `THEME_QSS_FILES` dict for a fixed order.

    Persistence: `QSettings` key `"theme"` (same as your previous project).
    """

    SETTINGS_KEY = "theme"
    _instance: ClassVar[ThemeManager | None] = None

    def __init__(
        self,
        app: QApplication,
        *,
        style_root: Path | str | None = None,
        theme_file_lists: dict[Theme, list[Path]] | None = None,
        persist: bool = True,
        auto_apply: bool = True,
    ) -> None:
        ThemeManager._instance = self
        self._app = app
        self._style_root = Path(style_root) if style_root is not None else _style_root_path()
        self._theme_file_lists = theme_file_lists
        self._persist = persist
        self._current_theme = Theme.LIGHT
        self._stylesheet_cache: dict[Theme, str] = {}

        self._core = self._style_root / "core"
        self._theme_dirs = {
            Theme.LIGHT: self._style_root / Theme.LIGHT.value,
            Theme.DARK: self._style_root / Theme.DARK.value,
        }

        if auto_apply:
            initial = _parse_theme(
                QSettings().value(self.SETTINGS_KEY, Theme.LIGHT.value)
                if persist
                else Theme.LIGHT.value
            )
            self.apply(initial, write_settings=False)

    @classmethod
    def instance(cls) -> ThemeManager | None:
        return cls._instance

    def get_current_theme(self) -> Theme:
        return self._current_theme

    def invalidate_cache(self) -> None:
        self._stylesheet_cache.clear()

    def _discover_paths(self, theme: Theme) -> list[Path]:
        theme_dir = self._theme_dirs[theme]
        paths: list[Path] = []
        for module in StyleModule:
            core_path = self._core / module.qss_filename()
            variant_path = theme_dir / module.qss_filename()
            if core_path.is_file():
                paths.append(core_path)
            if variant_path.is_file():
                paths.append(variant_path)
            elif core_path.is_file():
                raise FileNotFoundError(
                    f"Theme '{theme.value}' missing QSS for {module.name}: {variant_path}"
                )
        return paths

    def get_stylesheet(self, theme: Theme) -> str:
        cached = self._stylesheet_cache.get(theme)
        if cached is not None:
            return cached

        if self._theme_file_lists is not None:
            paths = self._theme_file_lists.get(theme)
            if not paths:
                raise KeyError(f"No QSS path list configured for theme {theme!r}")
        else:
            paths = self._discover_paths(theme)

        parts: list[str] = []
        for path in paths:
            if not path.is_file():
                raise FileNotFoundError(f"QSS file not found: {path}")
            parts.append(path.read_text(encoding="utf-8"))

        qss = "\n".join(parts) + "\n"
        self._stylesheet_cache[theme] = qss
        return qss

    def apply(self, theme: Theme, *, write_settings: bool | None = None) -> None:
        ws = self._persist if write_settings is None else write_settings
        self._current_theme = theme
        if ws:
            QSettings().setValue(self.SETTINGS_KEY, theme.value)

        self._app.setStyleSheet(self.get_stylesheet(theme))

        for widget in self._app.topLevelWidgets():
            self._notify_theme_changed(widget)

        self.set_dark_titlebar(
            self._titlebar_target_window(self._app),
            theme == Theme.DARK,
        )

    def toggle(self) -> Theme:
        nxt = Theme.DARK if self._current_theme == Theme.LIGHT else Theme.LIGHT
        self.apply(nxt)
        return nxt

    def load_core_only(self) -> None:
        """Debug: only `style/core/*.qss` from `StyleModule`, no variant layer."""
        parts: list[str] = []
        for module in StyleModule:
            path = self._core / module.qss_filename()
            if path.is_file():
                parts.append(path.read_text(encoding="utf-8"))
        self._app.setStyleSheet("\n\n".join(parts))

    def resolve_icon(self, icon_name: str | None) -> str | None:
        return resolve_icon_path(icon_name, self._current_theme)

    def icon(self, icon_name: str | None) -> QIcon:
        path = resolve_icon_path(icon_name, self._current_theme)
        return QIcon(path) if path else QIcon()

    @staticmethod
    def set_dark_titlebar(window: QWidget | None, use_dark: bool) -> None:
        if window is None or sys.platform != "win32":
            return
        try:
            wid = window.winId()
            if not wid:
                return
            hwnd = int(wid)
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            value = ctypes.c_int(1 if use_dark else 0)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(value),
                ctypes.sizeof(value),
            )
        except Exception as e:
            print("Dark titlebar (Windows 10/11 only):", e)

    @staticmethod
    def _notify_theme_changed(widget: QWidget) -> None:
        cb = getattr(widget, "on_theme_changed", None)
        if callable(cb):
            cb()
        for child in widget.findChildren(QWidget):
            child_cb = getattr(child, "on_theme_changed", None)
            if callable(child_cb):
                child_cb()

    @staticmethod
    def _titlebar_target_window(app: QApplication) -> QWidget | None:
        active = app.activeWindow()
        if active is not None:
            return active
        for w in app.topLevelWidgets():
            if w.isWindow() and w.isVisible():
                return w
        for w in app.topLevelWidgets():
            if w.isWindow():
                return w
        return None
