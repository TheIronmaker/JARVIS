from PySide6.QtWidgets import QWidget, QSlider, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

class DisplaySlider(QWidget):
    def __init__(self, label: str, value: float, min_val: float=0, max_val:float=100, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout()
        self.label = QLabel(label)
        layout.addWidget(self.label)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(min_val))
        self.slider.setMaximum(int(max_val))
        self.slider.setValue(int(value))
        self.slider.setEnabled(False)
        layout.addWidget(self.slider)

        self.value_label = QLabel(str(value))
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
    
    def set_value(self, value:float, rounding=2):
        self.slider.setValue(int(value))
        self.value_label.setText(str(round(value, rounding)))
    
class ButtonStack:
    def __init__(self, buttons:dict, button_cls=QPushButton, layout=QHBoxLayout, alignment=Qt.AlignHCenter):
        self.button_cls = button_cls
        self.layout = layout()
        self.alignment = alignment

        self.objects = {}
        self.create_buttons(buttons)

        # Maybe
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)

    def create_buttons(self, layout:dict, add_widgets=True):
        for name, function in layout.items():
            btn = self.button_cls(name)
            btn.clicked.connect(function)
            if name not in self.objects:
                self.objects[name] = btn

        if add_widgets:
            self.add_widgets()

    def add_widgets(self, widgets=None):
        source = widgets or self.objects.values()
        for object in source:
            self.layout.addWidget(object, alignment=self.alignment)