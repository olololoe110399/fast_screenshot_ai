from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QEvent, QTimer, QObject, QCoreApplication
from PyQt5.QtGui import QCloseEvent, QMouseEvent, QResizeEvent
from app.utils.image import grabScreenRegion


class CaptureSelectedPortion(QMainWindow):

    def __init__(self):
        super().__init__()
        self.widget_style = """
            QWidget#central_widget {
                border: 4px dashed rgba(255, 0, 0, 255);
                background-color: rgba(255, 255, 255, 2);
                border-radius: 4px;
            }
        """
        self.initUI()
        self.initVariables()
        self.setupConnections()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTitleHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.central_widget = self.createCentralWidget()
        self.setCentralWidget(self.central_widget)
        self.button_window = ButtonWindow()

    def initVariables(self):
        self.mouse_mode = 0
        self.mouse_relative_position = (0, 0)
        self.screen_region = (0, 0, 0, 0)
        self.screen_shoot_path = ""
        self.timer = QTimer(self)
        self.capture_success = False
        self.button_window_height = 50
        screen = QApplication.primaryScreen().size()
        self.screen_width, self.screen_height = screen.width(), screen.height()

        self.setMinimumSize(300, 100)
        self.setGeometry(int(self.screen_width / 2) - 200, int(self.screen_height / 2) - 150, 400, 300)
        self.result = None

    def setupConnections(self):
        self.button_window.button_close.clicked.connect(self.close)
        self.button_window.button_save.clicked.connect(self.saveScreenRegion)

    def createCentralWidget(self):
        central_widget = QWidget(self)
        central_widget.setObjectName("central_widget")
        central_widget.setStyleSheet(self.widget_style)
        central_widget.setMouseTracking(True)
        central_widget.installEventFilter(self)
        return central_widget

    def saveScreenRegion(self):
        self.captureScreenRegion()
        self.hideUI()
        self.timer.singleShot(100, self.saveCapturedRegion)

    def captureScreenRegion(self):
        self.screen_region = (self.x(), self.y(), self.width(), self.height())

    def saveCapturedRegion(self):
        cropped_image = grabScreenRegion(*self.screen_region)
        self.result = cropped_image
        self.capture_success = True

    def hideUI(self):
        self.hide()
        self.button_window.hide()

    def showUI(self):
        self.show()
        self.button_window.show()
        self.button_window.activateWindow()
        self.button_window.raise_()

    def closeEvent(self, event: QCloseEvent):
        self.button_window.close()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_relative_position = (event.pos().x(), event.pos().y())
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mouse_mode = 0
            event.accept()
        else:
            event.ignore()

    def resizeEvent(self, event: QResizeEvent):
        self.button_window.setGeometry(self.x(), self.y() + self.height(), self.width(), self.button_window_height)
        super().resizeEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.MouseMove:
            self.handleMouseMove(event)
        elif event.type() == QEvent.Show:
            self.updateButtonWindowPosition()
        return super().eventFilter(watched, event)

    def handleMouseMove(self, event: QMouseEvent):
        pos = event.pos()
        self.button_window.show()
        self.button_window.activateWindow()
        self.button_window.raise_()

        if event.buttons() == Qt.NoButton:
            self.updateCursorBasedOnPosition(pos)
        elif event.buttons() & Qt.LeftButton:
            self.resizeOrMoveWindow(pos, event.globalPos())

        QCoreApplication.processEvents()

    def updateButtonWindowPosition(self):
        self.button_window.setGeometry(self.x(), self.y() + self.height(), self.width(), self.button_window_height)

    def updateCursorBasedOnPosition(self, pos):
        if pos.x() > self.width() - 5 and pos.y() > self.height() - 5:
            QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
        elif pos.x() < 5 and pos.y() < 5:
            QApplication.setOverrideCursor(Qt.SizeFDiagCursor)
        elif pos.x() > self.width() - 5 and pos.y() < 5:
            QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
        elif pos.x() < 5 and pos.y() > self.height() - 5:
            QApplication.setOverrideCursor(Qt.SizeBDiagCursor)
        elif pos.x() > self.width() - 5 or pos.x() < 5:
            QApplication.setOverrideCursor(Qt.SizeHorCursor)
        elif pos.y() > self.height() - 5 or pos.y() < 5:
            QApplication.setOverrideCursor(Qt.SizeVerCursor)
        else:
            QApplication.setOverrideCursor(Qt.ArrowCursor)

    def resizeOrMoveWindow(self, pos, global_pos):
        if self.isResizeMode(pos):
            self.resizeWindow(pos)
        else:
            self.moveWindow(global_pos)

    def isResizeMode(self, pos):
        return any(
            [
                pos.x() > self.width() - 10 and pos.y() > self.height() - 10,
                pos.x() < 10 and pos.y() < 10,
                pos.x() > self.width() - 10 and pos.y() < 10,
                pos.x() < 10 and pos.y() > self.height() - 10,
            ]
        )

    def resizeWindow(self, pos):
        if pos.x() > self.width() - 10 and pos.y() > self.height() - 10:
            self.setGeometry(self.x(), self.y(), pos.x(), pos.y())
        elif pos.x() < 10 and pos.y() < 10:
            self.setGeometry(self.x() + pos.x(), self.y() + pos.y(), self.width() - pos.x(), self.height() - pos.y())

    def moveWindow(self, global_pos):
        self.move(global_pos.x() - self.mouse_relative_position[0], global_pos.y() - self.mouse_relative_position[1])
        self.updateButtonWindowPosition()

    def isCaptured(self):
        return self.capture_success

    def run(self):
        self.show()
        while not self.isCaptured():
            QApplication.processEvents()


# Button Window
class ButtonWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.button_save = self.createButton("Capture")
        self.button_close = self.createButton("Close")

        layout = self.createLayout()
        self.setLayout(layout)

    def createButton(self, label):
        button = QPushButton(label)
        button.setFixedSize(100, 30)
        button.setMouseTracking(True)
        button.installEventFilter(self)
        return button

    def createLayout(self):
        h_layout = QHBoxLayout()
        h_layout.addStretch(1)
        h_layout.addWidget(self.button_save)
        h_layout.addStretch(1)
        h_layout.addWidget(self.button_close)
        h_layout.addStretch(1)

        v_layout = QVBoxLayout()
        v_layout.addStretch(1)
        v_layout.addLayout(h_layout)
        v_layout.addStretch(1)

        return v_layout

    def eventFilter(self, watched: QObject, event: QEvent):
        if event.type() == QEvent.MouseMove:
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            return True
        return super().eventFilter(watched, event)
