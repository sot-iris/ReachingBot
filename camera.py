#!/usr/bin/env python3
from uuid import getnode as get_mac
import time
import datetime
import cv2
import numpy as np
import subprocess as sp
import atexit
import os

params = cv2.SimpleBlobDetector_Params()
params.filterByArea = True
params.minArea = 100
params.minThreshold = 50
params.maxThreshold = 255
detector = cv2.SimpleBlobDetector(params)

class Frame:
    def __init__(self, frame, time):
        self.frame = frame
        self.time = time

class Camera:
    def __init__(self, width=480, height=640, FPS=250, rotation=90):
        self.w = width
        self.h = height
        self.rot = rotation
        self.fps = FPS
        self.bytesPerFrame = self.w * self.h
        self.videoCmd = """raspividyuv -md 7 -rot {} -w {} -h {} --output - --timeout 0
        --framerate {} --luma --nopreview""".format(self.rot, self.w, self.h, self.fps)
        self.videoCmd = self.videoCmd.split()
        self.cameraProcess = sp.Popen(self.videoCmd, stdout=sp.PIPE)
        atexit.register(self.cameraProcess.terminate)
        print("Camera started -- w={}, h={}, maxFPS={}, rotation={}".format(self.w, self.h, self.fps, self.rot))
        time.sleep(0.1)
        self.cameraProcess.stdout.read(self.bytesPerFrame)

    def FrameGenerator(self):
        self.cameraProcess.stdout.flush()
        frame = np.fromfile(self.cameraProcess.stdout, count=self.bytesPerFrame, dtype=np.uint8)
        if frame.size != self.bytesPerFrame:
            print("Error: Camera stream closed unexpectedly")
        frame.shape = (self.h, self.w)  # set the correct dimensions for the numpy array
        return Frame(frame, time.time())

def BlobDetection(frameToDetect):
    frame = frameToDetect
    small = cv2.resize(frame, (0, 0), fx=0.4, fy=0.4)
    inverted = 255 - small  # inverts image
    keypoints = detector.detect(inverted)
    if keypoints:
        for key in keypoints:
            coordx = key.pt[0]
            coordy = key.pt[1]
            size = key.size
            return coordx, coordy, size, time.time()
    else:
        return None

if __name__ == "__main__":
    Cam = Camera()
    while True:
        frameclass = Cam.FrameGenerator()
        frame = frameclass.frame
        cv2.imshow("LiveStream", frame)#[0:320, 0:480])
        cv2.waitKey(1)
