import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

class SimpleMainWindow(QMainWindow):
    def __init__(self, config:dict):
        super().__init__()

        # Set Transparency for PySide6 Window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint) #Qt.WindowType.WindowStaysOnTopHint
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setWindowTitle(config.get("title", "JARVIS Test"))
        self.resize(*config.get("window_size", (1200, 800)))

        self.central_widget = config.get("central_widget", QWidget())
        self.setCentralWidget(self.central_widget)
        #self.main_layout = QVBoxLayout(self.central_widget) # Maybe?


class SimpleApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
    
    def launch(self, config:dict):
        self.window = SimpleMainWindow(config)
        self.window.show()

        sys.exit(self.app.exec())
