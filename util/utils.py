import numpy as np
import cv2 as cv
from typing import List, Tuple, Union
from pathlib import Path 
from copy import deepcopy


size_P = Union[List[int],Tuple[int,int]]


class CameraCalibrateAndRemoveDist:
    def __init__(self,src_dir:str, pattern_shape:size_P, img_shape:size_P):
        self.src_dir: Path = Path(src_dir)
        self.imgs_path:List[Path] = []
        self.get_files()
        self.chkr_pattrn:size_P = pattern_shape
        self.img_shape:size_P = img_shape 
        self.MatrixCoefs:np.ndarray = None
        self.DistCoefs:np.ndarray = None
        self.objpoints: List[np.ndarray] = []
        self.imgpoints: List[np.ndarray] = []


    def find_chessboard_corners(self,draw:bool=False) -> None:
        if self.objpoints:
            self.rm_obj_world_points()

        criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((self.chkr_pattrn[0]*self.chkr_pattrn[1],3), np.float32)
        objp[:,:2] = np.mgrid[0:self.chkr_pattrn[0],0:self.chkr_pattrn[1]].T.reshape(-1,2)

        for img_p in self.imgs_path:
            gray = cv.imread(img_p,0)
            if gray.shape != self.img_shape:
                gray = cv.resize(gray,self.img_shape)

            ret, corners = cv.findChessboardCorners(gray,self.chkr_pattrn,None)
            if ret == True:
                self.objpoints.append(objp)
                self.imgpoints.append(cv.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria))
                if draw:
                    img = np.zeros(shape=(self.img_shape[0],self.img_shape[1],3),dtype=np.uint8)
                    img[:,:,0] = gray
                    img[:,:,1] = gray
                    img[:,:,2] = gray
                    cv.drawChessboardCorners(img, (7,6), self.imgpoints[-1], ret)
                    cv.imshow('img', img)
                    cv.waitKey(1500)
        cv.destroyAllWindows()


    def find_calibration_params(self):
        repError, self.MatrixCoefs, self.DistCoefs, rvecs,tvec = cv.calibrateCamera(
            self.objpoints, self.imgpoints, self.img_shape[::-1], None, None
        )

    
    def undistort_image(self, img:np.ndarray):
        HEIGHT, WIDTH = img.shape[:2]
        newcameramtx, roi = cv.getOptimalNewCameraMatrix(self.MatrixCoefs, self.DistCoefs, (WIDTH,HEIGHT), 1, (WIDTH,HEIGHT))
        return cv.undistort(img, self.MatrixCoefs, self.DistCoefs, None, newcameramtx)[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]


    def get_files(self,extensions:List[str]=[".jpg",".jpeg",".png"]) -> None:
        if self.imgs_path:
            self.rm_files()

        for file in self.src_dir.rglob("*.*"):
            if file.is_file() and file.suffix.lower() in [".jpg",".jpeg",".png"]:
                self.imgs_path.append(file)
    

    def rm_files(self) -> None:
        self.imgs_path = []


    def rm_obj_world_points(self) -> None:
        self.objpoints = []
        self.imgpoints = []