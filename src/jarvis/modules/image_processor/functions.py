import numpy as np
import cv2

def draw_text_list(data, size, pos=(0, 0), color=(255, 255, 255), font_height=40, font_scale=1, thickness=2):
    overlay = np.zeros((size[0], size[1], 3), dtype=np.uint8)
    for i, text in enumerate(data):
        cv2.putText(overlay, text, (pos[0], int(pos[1]+i*font_height*font_scale)), cv2.FONT_HERSHEY_DUPLEX, font_scale, color, thickness, cv2.LINE_AA)
    return overlay