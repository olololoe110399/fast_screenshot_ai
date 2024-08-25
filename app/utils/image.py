from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication
from PIL.Image import Image
from PIL import ImageGrab
from io import BytesIO
import pyperclip

def pilImageToQImage(image: Image) -> QImage:
    image = image.convert("RGBA")
    data = image.tobytes("raw", "RGBA")
    q_image = QImage(data, image.width, image.height, QImage.Format_RGBA8888)
    return q_image

def copyImageToClipboard(image:Image) -> None:
    output = BytesIO()
    image.convert("RGB").save(output, "PNG")
    pyperclip.copy(output.getvalue().hex())


def grabScreenRegion(x, y, width, height):
    screen_image = ImageGrab.grab()
    screen_width = QApplication.primaryScreen().size().width()
    screen_height = QApplication.primaryScreen().size().height()

    scale_w = screen_image.size[0] / screen_width
    scale_h = screen_image.size[1] / screen_height

    cropped_image = screen_image.crop((int(x * scale_w), int(y * scale_h), int((x + width) * scale_w), int((y + height) * scale_h)))
    return cropped_image
