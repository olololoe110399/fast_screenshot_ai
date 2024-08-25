from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QProgressDialog)
from PyQt5.QtCore import Qt

class BaseUI(QMainWindow):
    def __init__(self):
        super().__init__()

    def showError(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.exec_()

    def showInfo(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Information")
        msg.exec_()

    def showWarning(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(message)
        msg.setWindowTitle("Warning")
        msg.exec_()

    def showLoading(self, message="Loading..."):
        if not hasattr(self, "dialog"):
            self.dialog = QProgressDialog()
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.setCancelButton(None)
        self.dialog.setRange(0, 0)
        self.dialog.setLabelText(message)
        self.dialog.show()

    def closeLoading(self):
        if not hasattr(self, "dialog"):
            return
        self.dialog.close()