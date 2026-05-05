from __future__ import annotations

from enum import StrEnum

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton, QSizePolicy, QWidget

from app.core.theme import Theme, ThemeManager, resolve_icon_path


def _qicon_named(icon_name: str) -> QIcon:
    mgr = ThemeManager.instance()
    if mgr is not None:
        return mgr.icon(icon_name)
    path = resolve_icon_path(icon_name, Theme.LIGHT)
    return QIcon(path) if path else QIcon()


class ButtonVariant(StrEnum):
    """Maps to application QSS (`:flat` + dynamic `appearance` property)."""

    STANDARD = "standard"
    """Outlined / neutral `QPushButton` (global theme)."""

    GHOST = "ghost"
    """Transparent row; uses `QPushButton:flat` rules in theme."""

    PRIMARY = "primary"
    """Filled accent; targets `QPushButton[appearance=\"primary\"]` in theme."""


class ButtonContext(StrEnum):
    """Optional placement hint for QSS: `QPushButton[context=\"…\"]."""

    SIDEBAR = "sidebar"
    TOOLBAR = "toolbar"
    PAGE = "page"
    DIALOG = "dialog"


def _coerce_variant(value: ButtonVariant | str) -> ButtonVariant:
    if isinstance(value, ButtonVariant):
        return value
    return ButtonVariant(value)


def _coerce_context(value: ButtonContext | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, ButtonContext):
        return value.value
    return str(value)


class AppButton(QPushButton):
    """
    Application `QPushButton` that cooperates with global QSS (ThemeManager).

    - **Styling** comes from `app/style` — this class only sets `Qt` properties
      (`context`, `appearance`) and `flat` so selectors can target placements.
    - **Icons**: pass a base name (`\"home\"`) for theme-aware SVG resolution, or
      a ready `QIcon`. String icons refresh on `on_theme_changed` if the app
      notifies children (ThemeManager does this on `apply`).
    """

    def __init__(
        self,
        text: str = "",
        parent: QWidget | None = None,
        *,
        icon: str | QIcon | None = None,
        variant: ButtonVariant | str = ButtonVariant.STANDARD,
        context: ButtonContext | str | None = None,
        icon_size: int | QSize | None = 20,
        expand_horizontal: bool = False,
        focus_policy: Qt.FocusPolicy = Qt.FocusPolicy.StrongFocus,
    ) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(focus_policy)

        h = (
            QSizePolicy.Policy.Expanding if expand_horizontal else QSizePolicy.Policy.Minimum
        )
        self.setSizePolicy(h, QSizePolicy.Policy.Fixed)

        self._icon_name: str | None = None
        self._icon_payload: QIcon | None = None

        if isinstance(icon, QIcon):
            self._icon_payload = icon if not icon.isNull() else None
        elif isinstance(icon, str) and icon:
            self._icon_name = icon
        elif icon:
            raise TypeError("icon must be str | QIcon | None")

        if icon_size is not None:
            s = QSize(icon_size, icon_size) if isinstance(icon_size, int) else icon_size
            self.setIconSize(s)

        ctx = _coerce_context(context)
        if ctx:
            self.setProperty("context", ctx)

        self._variant = _coerce_variant(variant)
        self._apply_variant(self._variant)
        self._apply_icon_payload()
        self._polish()

    @property
    def variant(self) -> ButtonVariant:
        return self._variant

    def set_variant(self, value: ButtonVariant | str) -> None:
        self._variant = _coerce_variant(value)
        self._apply_variant(self._variant)
        self._polish()

    def _apply_variant(self, variant: ButtonVariant) -> None:
        if variant is ButtonVariant.GHOST:
            self.setFlat(True)
            self.setProperty("appearance", "standard")
        elif variant is ButtonVariant.PRIMARY:
            self.setFlat(False)
            self.setProperty("appearance", "primary")
        else:
            self.setFlat(False)
            self.setProperty("appearance", "standard")

    def _apply_icon_payload(self) -> None:
        if self._icon_name is not None:
            super().setIcon(_qicon_named(self._icon_name))
            return
        if self._icon_payload is not None:
            super().setIcon(self._icon_payload)

    def setIcon(self, icon: QIcon | None) -> None:
        """Direct icon: clears theme-managed name lookup."""
        self._icon_name = None
        self._icon_payload = icon if icon and not icon.isNull() else None
        super().setIcon(icon if icon and not icon.isNull() else QIcon())

    def set_icon_name(self, name: str | None) -> None:
        """Use theme-relative icon basename (e.g. `home` → `home.svg`)."""
        self._icon_payload = None
        self._icon_name = name or None
        self._apply_icon_payload()

    def on_theme_changed(self) -> None:
        if self._icon_name:
            super().setIcon(_qicon_named(self._icon_name))

    def _polish(self) -> None:
        sty = self.style()
        sty.unpolish(self)
        sty.polish(self)
