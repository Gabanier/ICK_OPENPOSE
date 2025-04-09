import numpy as np
import cv2 as cv
from pathlib import Path
from utils import CameraCalibrateAndRemoveDist
from glob import glob
from typing import Tuple
import os


def get_calibration_images(src_dir:str,filename:str="checkerboard"):
    src = Path(src_dir)
    src.mkdir(parents=True, exist_ok=True)
    cap = cv.VideoCapture(0)
    ite = 0
    while cap.isOpened():
        
        ret, img = cap.read()
        key = cv.waitKey(10)

        if key == ord('q'):
            break
        elif key == ord('s'):
            cv.imwrite(src / f"{filename}_{ite}.png", img)
            print(f"Saved {filename}_{ite}.png")
            ite += 1
             
        
        cv.imshow("You :)",img)
    
    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    src_dir = input("Select img direcotry: ")
    get_calibration_images(src_dir)