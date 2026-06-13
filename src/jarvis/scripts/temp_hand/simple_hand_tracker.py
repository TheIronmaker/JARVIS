import cv2
import mediapipe as mp
import subprocess
import time
import pyautogui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

SENSITIVITY = 6.0  
CLICK_VELOCITY_THRESHOLD = 90.0  
TAP_TIMEOUT = 0.25  

prev_palm_x = None
prev_palm_y = None
prev_index_y = None
prev_time = None
last_move_time = 0
COOLDOWN = 0.01  

# Tap tracking variables
dip_detected = False
dip_time = 0

base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1,
    running_mode=vision.RunningMode.IMAGE
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def move_front_window_relative(dx, dy):
    apple_script = f'''
    tell application "System Events"
        tell first application process whose frontmost is true
            try
                set targetWindow to window 1
                set {{currentX, currentY}} to position of targetWindow
                set position of targetWindow to {{currentX + {dx}, currentY + {dy}}}
            end try
        end tell
    end tell
    '''
    subprocess.Popen(['osascript', '-e', apple_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

while cap.isOpened():
    success, frame = cap.read()
    if not success: continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    detection_result = detector.detect(mp_image)

    if detection_result.hand_landmarks:
        hand_landmarks = detection_result.hand_landmarks[0]
        
        index_pip = hand_landmarks[6]
        index_tip = hand_landmarks[8]
        palm_node = hand_landmarks[9]       
        middle_pip = hand_landmarks[10]
        middle_tip = hand_landmarks[12]
        
        px, py = int(palm_node.x * w), int(palm_node.y * h)
        iy = int(index_tip.y * h)
        current_time = time.time()
        
        is_index_up = index_tip.y < index_pip.y
        is_middle_up = middle_tip.y < middle_pip.y

        # Down-and-Up Tap Detection Logic
        if prev_index_y is not None and prev_time is not None:
            dt = current_time - prev_time
            if dt > 0:
                vel_y = (iy - prev_index_y) / dt
                
                # Phase 1: Fast downward movement detected
                if vel_y > CLICK_VELOCITY_THRESHOLD and not dip_detected:
                    dip_detected = True
                    dip_time = current_time
                
                # Phase 2: Fast upward movement detected shortly after down movement
                if dip_detected:
                    if current_time - dip_time > TAP_TIMEOUT:
                        dip_detected = False  # Timeout expired
                    elif vel_y < -CLICK_VELOCITY_THRESHOLD:
                        pyautogui.click()
                        dip_detected = False  # Reset after successful trigger

        dx, dy = 0, 0
        if prev_palm_x is not None and prev_palm_y is not None:
            dx = int((px - prev_palm_x) * SENSITIVITY)
            dy = int((py - prev_palm_y) * SENSITIVITY)

        if not is_middle_up:
            if dx != 0 or dy != 0:
                if current_time - last_move_time > COOLDOWN:
                    move_front_window_relative(dx, dy)
                    last_move_time = current_time
            prev_palm_x, prev_palm_y = px, py

        elif not is_index_up:
            if dx != 0 or dy != 0:
                pyautogui.moveRel(dx, dy)
            prev_palm_x, prev_palm_y = px, py
                    
        else:
            prev_palm_x, prev_palm_y = None, None

        prev_index_y = iy
        prev_time = current_time
    else:
        prev_palm_x, prev_palm_y = None, None
        prev_index_y = None
        prev_time = None
        dip_detected = False

    cv2.imshow('Palm Space Manager', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
detector.close()