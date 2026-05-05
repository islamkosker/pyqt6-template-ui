from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt

from app.core.constant.app_constant import AppConstant

class Footer(QFrame):
    def __init__(self):
        super().__init__()

        self.setFixedHeight(20)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        self.setObjectName("Footer")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(AppConstant.FOOTER_TEXT.value)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setObjectName("FooterLabel")

        layout.addWidget(label)
