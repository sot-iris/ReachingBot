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

def videoProcess(ID, _frames):
 #accepts RFID tag of animal and the list of frames to encode to video
    stamp = str(datetime.datetime.now()).split(" ")[1].split(".")[0].strip(":")
    videoName = "{}_{}.avi".format(ID, remove(":", stamp))
    out = cv2.VideoWriter(videoName, cv2.cv.CV_FOURCC(*"XVID"), 30, (450, 350))
    fps = len(_frames) / (_frames[-1].time - _frames[0].time)
    print("fps: {}".format(fps))
    for n in range(len(_frames)):
        try:
            roi = cv2.cvtColor(_frames[n].frame[0:350, 0:450], cv2.COLOR_GRAY2BGR)
            out.write(roi)
        except:
            print("this was the frame number: {}".format(n))
    out.release()
    data_Send.sendDatatoDB(videoName, ID, stamp, fps, getTarget())

def BlobDetection(frameToDetect, cropping=[0,350,0,450]):
    frame = frameToDetect
    small = cv2.resize(frame, (0, 0), fx=0.4, fy=0.4)
    inverted = 255 - small  # inverts image
    keypoints = detector.detect(inverted)
    if keypoints:
        pelletTrue = True
        for key in keypoints:
            coordx = key.pt[0]
            coordy = key.pt[1]
            size = key.size
            return pelletTrue, coordx, coordy, size, time.time()
    else:
        pelletTrue = False
        return pelletTrue, 1, 1, 1, time.time()

if __name__ == "__main__":
    Cam = Camera()
    while True:
        frameclass = Cam.FrameGenerator()
        frame = frameclass.frame
        fps_counter.append(frameclass.time)
        if len(fps_counter) == 10:
            difference = fps_counter[9] - fps_counter[0]
            fps = 10/difference
            cv2.putText(frame,
                        "FPS of LiveStream: {}".format(str(int(fps))),
                        (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255,255,255),
                        2)
        cv2.imshow("LiveStream", frame)#[0:320, 0:480])
        cv2.waitKey(1)
