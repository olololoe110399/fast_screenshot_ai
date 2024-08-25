from PyQt5.QtCore import QThread, pyqtSignal
import openai

class AskOpenAIThread(QThread):
    question_answered = pyqtSignal(str)

    def __init__(self, prompt: str, parent=None):
        super().__init__(parent)
        self.prompt = "Only answer correct answers. Do not provide any additional information. Question: " + prompt

    def run(self):
        response = openai.chat.completions.create(
            engine="davinci",
            prompt=self.prompt,
            stream=True
        )
        for message in response:
            print(message.choices[0].message["content"], end="", flush=True)
            self.question_answered.emit(message.choices[0].message["content"])
