import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PySide6.QtCore import Qt

class SimpleMainWindow(QMainWindow):
    def __init__(self, config:dict):
        super().__init__()
        self.config = config

        # Set Transparency for PySide6 Window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint) #Qt.WindowType.WindowStaysOnTopHint
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setWindowTitle(config["title"])
        self.resize(*config["size"].values())
        
        self.central_widget = config["ui_layout"]["central_widget"](self)
        self.setCentralWidget(self.central_widget)
        #self.main_layout = QVBoxLayout(self.central_widget) # Maybe?


class SimpleApp:
    def __init__(self, config):
        self.app = QApplication(sys.argv)
        self.config = config
    
    def launch(self):
        self.window = SimpleMainWindow(self.config.get("main_window", {}))
        self.window.show()

        sys.exit(self.app.exec())
