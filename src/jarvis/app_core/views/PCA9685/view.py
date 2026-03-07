from PySide6.QtWidgets import QWidget, QSizePolicy
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt, QRectF

class PCA9685View(QWidget):
    def __init__(self, name, parent, settings={}):
        super().__init__(parent)
        self.name = name
        self.parent = parent
        self.settings = settings
        self.bus_global = parent.bus
        self.bus = parent.bus.namespaced(name)

        self.container = None

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Data Handling
        self.channel_count = settings.get("num_channels")
        self.corner_radius = settings.get("corner_radius") # Maybe
        self.values = [0] * self.channel_count

        # Gui elements
        self.font = QFont()
    
    def add_link(self, link:str, placement=0):
        if link and isinstance(link, str):
            self.settings["links"].insert(placement, link)
    
    def clear_links(self):
        self.settings["links"] = []
    
    def get_link(self):
        links = self.settings.get("links")
        return links[0] if links else False

    def poll(self):
        link = self.get_link()
        if link:
            self.values = self.bus_global.get(link[0]+".PWM") or self.values

    def paint(self, event=None, painter:QPainter=None):
        p = painter
        p.setRenderHint(QPainter.Antialiasing)

        p.setBrush(QColor(209, 180, 56))
        p.setPen(Qt.NoPen)
        #print(self.geometry().getCoords()[:2])
        if self.container:
            rect_box = QRectF(*self.container.geometry().getCoords()[:2], *self.geometry().getCoords()[2:4])
            rect_box.adjust(0, 0, 0, 0)
        else:
            rect_box = QRectF(*self.geometry().getCoords()[:2], *self.geometry().getCoords()[2:4])
        p.drawRoundedRect(rect_box, 0, 0)

        # Math + Data
        config = self.settings.get("grid_config")
        left_margin = config.get("left_margin")
        cols = config.get("cols")
        rows = config.get("rows")
        cell_w = (self.width() - left_margin) / cols
        cell_h = self.height() / rows
        r = min(cell_w, cell_h) * 0.25

        # Draw Text Cells
        if cell_h > config.get("text_min") and cell_h < config.get("text_max"):
            self.font.setPointSizeF()
            p.setFont(self.font)
        
        font_size = max(config.get("text_min"), min(cell_h * 0.28, config.get("text_max")))
        self.font.setPointSizeF(font_size)

        for i in range(self.channel_count):
            row = i // cols
            col = i % cols

            x = left_margin + col * cell_w + self.x()
            y = row * cell_h + self.y()

            color = QColor(60, 200, 90) if self.values[i] > 0 else QColor(50, 50, 50)
            rect = QRectF(x+4, y+4, cell_w-8, cell_h-8)

            p.setPen(Qt.NoPen)
            p.setBrush(color)
            p.drawRoundedRect(rect, r, r)

            p.setPen(Qt.white)
            p.drawText(rect, Qt.AlignCenter, f"{i}")

        # group labels
        p.setPen(Qt.white)
        for g in range(4):
            y = g * cell_h + cell_h * 0.65
            p.drawText(6, int(y), f"G{g+1}")



    def NEWpaint(self, painter: QPainter):
        p = painter

        # Math and Data
        config = self.settings.get("grid_config")
        cols = config["cols"]
        rows = config["rows"]
        aspect_ratio = int(cols // rows)

        for i in range(self.channel_count):
            rect = QRectF()
            p.drawRoundedRect()