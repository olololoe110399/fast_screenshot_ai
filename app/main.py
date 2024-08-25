import sys

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QKeySequence
from PIL import ImageFilter, Image
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QStatusBar,
    QTabWidget,
    QFileDialog,
    QShortcut,
)
from app.components.base import BaseUI
from app.components.capture_cursor_selected_portion import CaptureCursorSelectedPortion
from app.components.capture_selected_portion import CaptureSelectedPortion
from app.threads.text_extraction import TextExtractionThread
from app.threads.ask_ollama import AskOllamaThread
from app.utils.image import pilImageToQImage


class MainApp(BaseUI):
    def __init__(self):
        super().__init__()
        self.img_frame_style = """
            border: 1px solid #dfe6e9; 
            background-color: #f5f6fa; 
            border-radius: 8px; 
            padding: 5px; 
        """
        self.button_style = """
            QPushButton {
                background-color: #4a69bd;
                color: white;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #1e3799;
            }
            QPushButton:pressed {
                background-color: #3b3b98;
            }
        """
        self.text_edit_style = """
            QTextEdit {
                font-size: 13px;
                padding: 8px;
                border: 1px solid #ced6e0;
                border-radius: 5px;
                background-color: #f1f2f6;
                color: #2f3542;
            }
        """
        self.timer = QTimer()
        self.initUI()

    def initUI(self):
        # WindowStaysOnTopHint
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Fast Screenshots AI")
        self.resize(500, 300)
        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.tabs = QTabWidget(self)
        self.view_image_tab, view_image_tab_name = self.viewImageTab()
        self.ask_question_tab, ask_question_tab_name = self.generateTab()
        self.tabs.addTab(self.view_image_tab, view_image_tab_name)
        self.tabs.addTab(self.ask_question_tab, ask_question_tab_name)
        self.setCentralWidget(self.tabs)
        self.tabs.setCurrentIndex(0)

    def viewImageTab(self):
        # Label to display image
        self.img_label = QLabel(self)
        self.img_label.setFixedSize(500, 300)  # Reduced size
        self.img_label.setStyleSheet(self.img_frame_style)
        self.img_label.setAlignment(Qt.AlignCenter)
        self.img_label.setText("No image selected")

        # Button to import image
        import_button = QPushButton("Import Image", self)
        import_button.setStyleSheet(self.button_style)
        import_button.clicked.connect(self.import_image)

        # Button to select area
        capture_cursor_selected_portion_button = QPushButton("Screen Capture", self)
        capture_cursor_selected_portion_button.setStyleSheet(self.button_style)
        capture_cursor_selected_portion_button.clicked.connect(self.area_selection)
        self.shortcut1 = QShortcut(QKeySequence("Ctrl+Shift+6"), self)
        self.shortcut1.activated.connect(self.area_selection)

        # Button to select area
        capture_selected_portion_button = QPushButton("Custom Screen Capture", self)
        capture_selected_portion_button.setStyleSheet(self.button_style)
        capture_selected_portion_button.clicked.connect(self.custom_area_selection)
        self.shortcut2 = QShortcut(QKeySequence("Ctrl+Shift+7"), self)
        self.shortcut2.activated.connect(self.custom_area_selection)

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(import_button)
        button_layout.addWidget(capture_cursor_selected_portion_button)
        button_layout.addWidget(capture_selected_portion_button)

        # Layout for the page
        image_page_layout = QVBoxLayout()
        image_page_layout.setAlignment(Qt.AlignCenter)  # Center content
        image_page_layout.addWidget(self.img_label)
        image_page_layout.addLayout(button_layout)
        image_page = QWidget()
        image_page.setLayout(image_page_layout)
        return image_page, "View Image"

    def area_selection(self):
        self.hide()
        self.timer.singleShot(100, self.capture_screen)

    def custom_area_selection(self):
        self.hide()
        selection_custom = CaptureSelectedPortion()
        selection_custom.run()
        if selection_custom.isCaptured():
            enhanced_image = selection_custom.result
            self.display_image(enhanced_image)
            self.selected_image = enhanced_image
            self.extract_text()
        self.show()

    def capture_screen(self):
        selection_dialog = CaptureCursorSelectedPortion()
        selection_dialog.run()

        if selection_dialog.selected_region:
            enhanced_image = selection_dialog.selected_region.filter(ImageFilter.SHARPEN)
            self.display_image(enhanced_image)
            self.selected_image = enhanced_image
            self.extract_text()
        else:
            self.statusbar.showMessage("No image selected", 3000)
        self.show()

    def display_image(self, image):
        q_image = pilImageToQImage(image)
        img_pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = img_pixmap.scaled(self.img_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.img_label.setPixmap(scaled_pixmap)

    def extract_text(self):
        if self.selected_image:
            self.showLoading("Extracting text...")
            self.text_extraction_thread = TextExtractionThread(self.selected_image)
            self.text_extraction_thread.text_extracted.connect(self.on_text_extraction_complete)
            self.text_extraction_thread.start()

    def on_text_extraction_complete(self, extracted_text):
        self.text_edit.setText(extracted_text)
        self.tabs.setCurrentIndex(1)
        self.statusbar.showMessage("Text extracted successfully", 3000)
        self.text_extraction_thread = None
        self.closeLoading()

    def import_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Import Image", "", "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if file_name:
            self.selected_image = Image.open(file_name)
            self.display_image(self.selected_image)
            self.statusbar.showMessage("Image imported successfully. Extracting text...", 3000)
            self.extract_text()

    def generateTab(self):
        # Text edit to display extracted text
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlaceholderText("Extracted text will appear here...")
        self.text_edit.setStyleSheet(self.text_edit_style)

        # Button to ask GPT-3.5
        ask_gpt_button = QPushButton("Ask", self)
        ask_gpt_button.setStyleSheet(self.button_style)
        ask_gpt_button.clicked.connect(self.ask_gpt)

        # Text response from GPT-3.5
        self.text_response = QTextEdit(self)
        self.text_response.setPlaceholderText("Response from LLM will appear here...")

        # Layout for the page
        gpt_page_layout = QVBoxLayout()
        gpt_page_layout.setAlignment(Qt.AlignCenter)
        gpt_page_layout.addWidget(self.text_edit)
        gpt_page_layout.addWidget(ask_gpt_button)
        gpt_page_layout.addWidget(self.text_response)
        gpt_page = QWidget()
        gpt_page.setLayout(gpt_page_layout)
        return gpt_page, "Ask Question"

    def ask_gpt(self):
        if self.text_edit.toPlainText():
            self.ask_openai_thread = AskOllamaThread(self.text_edit.toPlainText())
            self.ask_openai_thread.question_answered.connect(self.on_question_answered)
            self.ask_openai_thread.start()
        else:
            self.showWarning("No text to ask question")

    def on_question_answered(self, answer):
        self.ask_openai_thread = None
        self.text_response.setText(answer)
        self.tabs.setCurrentIndex(1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
