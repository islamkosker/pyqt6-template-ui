from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QSizePolicy, QWidget


class PillDivider(QWidget):
    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self.setFixedHeight(2)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAutoFillBackground(False)

    def setColor(self, color: QColor) -> None:
        self._color = QColor(color)
        self.update()

    def showEvent(self, event):
        self.update()
        super().showEvent(event)

    def resizeEvent(self, event):
        self.update()
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color)

        rect = QRectF(self.rect()).adjusted(0.3, 0.3, -0.3, -0.3)
        radius = rect.height() / 2
        painter.drawRoundedRect(rect, radius, radius)