import numpy as np
from numpy.typing import NDArray
import cv2
import math

from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtCore import Qt


def round_pixmap(pixmap, radius):
    if not radius or radius <= 0: return pixmap

    rounded = QPixmap(pixmap.size())
    rounded.fill(Qt.transparent)

    with QPainter(rounded) as painter:
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)

    return rounded

def draw_text_list(data: list[str], size, pos=(0, 0), color=(255, 255, 255), font_height=40, font_scale=1, thickness=2) -> NDArray:
    overlay = np.zeros((size[0], size[1], 3), dtype=np.uint8)
    for i, text in enumerate(data):
        cv2.putText(overlay, text, (pos[0], int(pos[1]+i*font_height*font_scale)), cv2.FONT_HERSHEY_DUPLEX, font_scale, color, thickness, cv2.LINE_AA)
    return overlay

def xyz_to_euler(rotation_matrix):
    """ Clamps xyz to [-1, 1] and returns Euler angles - Maybe replace with scipy library"""
    return [math.asin(-rotation_matrix[2][0].clip(-1, 1)),
            math.atan2(rotation_matrix[2][1], rotation_matrix[2][2]),
            math.atan2(rotation_matrix[1][0], rotation_matrix[0][0])]

def render_gizmo(R: np.ndarray, size, thickness=6, scale=0.2):
    overlay = np.zeros((size[0], size[1], 3), dtype=np.uint8)
    sw, sh = size[1] // 2, size[0] // 2

    for i, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
        axis = R[i]

        f = 0.5 * size[1]  # focal length
        dx = int(scale * axis[0] * f / (1 + axis[2]))
        dy = int(scale * axis[1]*1000)

        cv2.line(overlay, (sw, sh), (sw - dx, sh - dy), color, thickness)

    return overlay