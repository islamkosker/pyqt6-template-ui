from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QFrame, QSizePolicy, QLabel


class TopBar(QFrame):
    def __init__(self, title: str | None):
        super().__init__()
        self.setMinimumHeight(70)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setObjectName("TopBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(24, 0, 24, 0)
        self.layout.setSpacing(12)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        if title:
            self.lbl_title = QLabel(title)
            self.lbl_title.setObjectName("TopBarTitle")

            font = self.lbl_title.font()
            font.setFamilies(["Segoe UI", "Inter", "Roboto", "Arial"])
            self.lbl_title.setFont(font)
            self.layout.addWidget(self.lbl_title)

        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("TopBarStatus")
        self.lbl_status.setVisible(False)
        self.lbl_status.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self._set_status_variant("default")

        self.layout.addStretch()
        self.layout.addWidget(self.lbl_status)

    def set_state(self, text: str, success: bool = False, error: bool = False):
        self.lbl_status.setText(text)
        self.lbl_status.setVisible(True)

        if success:
            self._set_status_variant("success")
        elif error:
            self._set_status_variant("error")
        else:
            self._set_status_variant("default")

    def _set_status_variant(self, variant: str) -> None:
        self.lbl_status.setProperty("variant", variant)
        self.lbl_status.style().unpolish(self.lbl_status)
        self.lbl_status.style().polish(self.lbl_status)
