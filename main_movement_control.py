import cv2
import numpy as np
import math
import mediapipe as mp
import pyautogui
from util.utils import CameraCalibrateAndRemoveDist 
from typing import Tuple

directions = [
        ((75, 105), "Gora"),
        ((255, 285), "Dol"),
        ((165, 195), "Lewo"),
        ((345, 360), "Prawo"),
        ((0, 15), "Prawo"),
        ((15, 75), "Gora-Prawo"),
        ((105, 165), "Gora-Lewo"),
        ((195, 255), "Dol-Lewo"),
        ((285, 345), "Dol-Prawo")
    ]


mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

screen_width, screen_height = pyautogui.size()

cap = cv2.VideoCapture(0)

SRC_DIR:str = "img"
pattern_size:Tuple[int,int] = (6,8) # (rows,cols)
img_size:Tuple[int,int] = (480,640)

CCRD = CameraCalibrateAndRemoveDist(SRC_DIR,pattern_size,img_size)
CCRD.find_chessboard_corners()
CCRD.find_calibration_params()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    frame = CCRD.undistort_image(frame)
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP] 
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
            
            x, y = int(finger_tip.x * w), int(finger_tip.y * h)
            
            dx = finger_tip.x - wrist.x
            dy = wrist.y - finger_tip.y
            angle_rad = math.atan2(dy, dx)
            angle_deg = (math.degrees(angle_rad) + 360) % 360
            cv2.putText(frame, f"{int(angle_deg)} st.", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            direction = "None"
            for (lb, ub), name in directions:
                if lb <= angle_deg <= ub:
                    direction = name
            
            cv2.putText(frame, f"Sterowanie: {direction}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            
            screen_x = int(finger_tip.x * screen_width)
            screen_y = int(finger_tip.y * screen_height)
            pyautogui.moveTo(screen_x, screen_y)
            
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    cv2.imshow("Result", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()