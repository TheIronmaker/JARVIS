from PySide6.QtWidgets import QWidget, QSlider, QLabel, QVBoxLayout
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
    
    def set_value(self, value:float, round=2):
        self.slider.setValue(int(value))
        self.value_label.setText(str(round(value, round)))