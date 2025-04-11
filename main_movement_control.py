import cv2
import numpy as np
import math
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui
from util.utils import CameraCalibrateAndRemoveDist 
from util.communication import UDPClient, create_message
from util.config import UDP_ADDRESS, UDP_PORT
from typing import Tuple
from pathlib import Path
import requests
from mediapipe.framework.formats import landmark_pb2


DIRECTIONS = [
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

def main(src_dir:str,pattern_size:Tuple[int,int],img_size:Tuple[int,int]):
    global DIRECTIONS

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    base_options = python.BaseOptions(model_asset_path=Path("util/gesture_recognizer.task"))
    options = vision.GestureRecognizerOptions(base_options=base_options,
                                              num_hands=2)
    recognizer = vision.GestureRecognizer.create_from_options(options)

    screen_width, screen_height = pyautogui.size()

    cap = cv2.VideoCapture(0)

    CCRD = CameraCalibrateAndRemoveDist(src_dir,pattern_size,img_size)
    CCRD.find_chessboard_corners()
    CCRD.find_calibration_params()

    client = UDPClient()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        frame = CCRD.undistort_image(frame)
        h, w, _ = frame.shape
        # rgb_frame1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        rgb_frame = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # result = hands.process(rgb_frame1)
        recognition_result = recognizer.recognize(rgb_frame)

        direction = "None"
        
        # if result.multi_hand_landmarks:
        if recognition_result.hand_landmarks:
            # for hand_landmarks in result.multi_hand_landmarks:
            index = 0
            for hand_landmarks in recognition_result.hand_landmarks:
                # finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP] 
                # wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                finger_tip = hand_landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP] 
                wrist = hand_landmarks[mp_hands.HandLandmark.WRIST]
                
                x, y = int(finger_tip.x * w), int(finger_tip.y * h)
                
                dx = finger_tip.x - wrist.x
                dy = wrist.y - finger_tip.y
                angle_rad = math.atan2(dy, dx)
                angle_deg = (math.degrees(angle_rad) + 360) % 360
                cv2.putText(frame, f"{int(angle_deg)} st.", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
                direction = "None"
                for (lb, ub), name in DIRECTIONS:
                    if lb <= angle_deg <= ub:
                        direction = name
                
                cv2.putText(frame, f"Sterowanie: {direction}", (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                gesture = recognition_result.gestures[index][0].category_name
                handedness = recognition_result.handedness[index][0].category_name
                if handedness == "Left":
                    cv2.putText(frame, f"Right: {gesture}", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    screen_x = int(finger_tip.x * screen_width)
                    screen_y = int(finger_tip.y * screen_height)
                    pyautogui.moveTo(screen_x, screen_y)

                elif handedness == "Right":
                    cv2.putText(frame, f"Left: {gesture}", (10, 310), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                
                # screen_x = int(finger_tip.x * screen_width)
                # screen_y = int(finger_tip.y * screen_height)
                # # pyautogui.moveTo(screen_x, screen_y)
                
                hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                hand_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
                ])
                
                mp_drawing.draw_landmarks(frame, hand_landmarks_proto, mp_hands.HAND_CONNECTIONS)
                index += 1
        cv2.imshow("Result", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        message = create_message(direction)
        if message is not None:
            client.send(UDP_ADDRESS, UDP_PORT, message)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    src_dir:str = "img" # (calibration directory name)
    pattern_size:Tuple[int,int] = (6,8) # (rows,cols)
    img_size:Tuple[int,int] = (480,640) # (rows,cols)
    if not Path("util/gesture_recognizer.task").exists():
        url = "https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task"
        response = requests.get(url)
        with open(Path("util/gesture_recognizer.task"), "wb") as f:
            f.write(response.content)
    else:
        print("File already exists.")
    main(src_dir,pattern_size,img_size)