from PyQt5.QtCore import QThread, pyqtSignal
import ollama


class AskOllamaThread(QThread):
    question_answered = pyqtSignal(str)

    def __init__(self, prompt, parent=None):
        super().__init__(parent)
        self.prompt = "Only answer correct answers. Do not provide any additional information. Question: " + prompt
        self.full_text = ""

    def run(self):
        self.full_text = ""
        stream = ollama.chat(
            model="llama3:latest",
            messages=[{"role": "user", "content": self.prompt}],
            stream=True,
        )
        for chunk in stream:
            print(chunk["message"]["content"], end="", flush=True)
            self.full_text += chunk["message"]["content"]
            self.question_answered.emit(self.full_text)
