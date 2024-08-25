import pytesseract
from PyQt5.QtCore import QThread, pyqtSignal

class TextExtractionThread(QThread):
    text_extracted = pyqtSignal(str)

    def __init__(self, image, parent=None):
        super().__init__(parent)
        self.image = image

    def run(self):
        extracted_text = pytesseract.image_to_string(self.image)
        self.text_extracted.emit(extracted_text)
