from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap, QCursor, QMouseEvent
from PyQt5.QtWidgets import QWidget, QApplication
from PIL import ImageGrab, ImageEnhance
from app.utils.image import pilImageToQImage


class CaptureCursorSelectedPortion(QWidget):

    def __init__(self):
        super().__init__()
        original_image = ImageGrab.grab()
        bg_image = ImageEnhance.Brightness(original_image).enhance(1)
        self.bg_image = bg_image
        self.original_image = original_image
        self.selected_region = None
        self.selection_start = QPoint()
        self.selection_end = QPoint()
        self.selection_active = False
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTitleHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(QCursor(Qt.CrossCursor))

    def paintEvent(self, event):
        painter = QPainter(self)
        q_image = pilImageToQImage(self.bg_image)
        bg_pix_map = QPixmap.fromImage(q_image)
        painter.drawPixmap(self.rect(), bg_pix_map)

        if self.selection_active:
            pen = QPen(QColor(255, 255, 255), 2, Qt.SolidLine)
            painter.setPen(pen)
            brush = QColor(255, 255, 255, 50)
            painter.setBrush(brush)
            rect = QRect(self.selection_start, self.selection_end)
            painter.drawRect(rect)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.selection_start = event.pos()
            self.selection_active = True
            self.update()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.selection_active:
            self.selection_end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.selection_active = False
            self.finalizeSelection()

    def finalizeSelection(self):
        scale_x = self.original_image.width / self.width()
        scale_y = self.original_image.height / self.height()
        x1 = int(self.selection_start.x() * scale_x)
        y1 = int(self.selection_start.y() * scale_y)
        x2 = int(self.selection_end.x() * scale_x)
        y2 = int(self.selection_end.y() * scale_y)

        if x1 != x2 and y1 != y2:
            self.selected_region = self.original_image.crop((x1, y1, x2, y2))
        self.close()

    def run(self):
        self.showFullScreen()
        while self.isVisible():
            QApplication.processEvents()
