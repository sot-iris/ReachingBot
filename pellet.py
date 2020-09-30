from __future__ import division
from motor import *
from collections import deque
from tqdm import tqdm
from camera import *
from reachingLogs import *
import time
import threading
import os
import numpy as np

from uuid import getnode as get_mac

videoSave = input("Do you want to save the videos? y/n").lower()
if videoSave:
    RFID_NAME = input("Please enter the RFID number: ")
    timePoint = input("Please enter the timePoint: ")
    folder = "{}_week{}".format(RFID_NAME, timePoint)
    if not os.path.exists(folder):
        os.makedirs((folder))
else:
    pLog("Not saving videos.")

waitTime = 60
Cam = Camera()
framesforvideo = deque(maxlen=350) #contains the frames that'll get stored to video
cameraStream = deque(maxlen=10) #containts the frames from the live stream
blobs = deque(maxlen=10) #contains instances of the Pellet class
pelletPlaced = False #used to stop and start appending frames to buffer that'll get
trial_number = 1
cameraOn = True
def remove(itemToRemove, wholeString):
    new = ""
    for i in wholeString:
        if i != itemToRemove:
            new += i
    return new

class Pellet:
    def __init__(self, x, y, size, timestamp):
        self.x = x
        self.y = y
        self.size = size
        self.timestamp = timestamp

def videoProcess(_frames=None):
    global trial_number
    finalFrames = _frames
    videoName = "{}/{}_week{}_trial{}.avi".format(folder, RFID_NAME, timePoint, trial_number)
    out = cv2.VideoWriter(videoName, cv2.cv.CV_FOURCC(*"XVID"), 30, (320, 240))
    fps = len(finalFrames) / (finalFrames[-1].time - finalFrames[0].time)
    pLog((fps, "- FPS"))
    for n in tqdm(range(len(finalFrames)), position=1, desc="Progress for video {}".format(1)):
        try:
            roi = cv2.cvtColor(finalFrames[n].frame, cv2.COLOR_GRAY2BGR)
            out.write(roi)
        except:
            pLog("this was the frame number: {}".format(n))
    out.release()
    pLog("{} saved.".format(videoName))
    trial_number += 1

def processFrame(frametoProcess, cropping=[140,240,90,160]):
    y1, y2, x1, x2 = cropping
    _frame_ = frametoProcess[y1:y2, x1:x2]
    processed =  BlobDetection(_frame_)
    if processed:
        x, y, size, time = processed
        return Pellet(x+x1, y+y1, size, time)
    else:
        return None

def blobStream():
    global cameraOn
    while cameraOn:
        if len(cameraStream) > 2:
            pel = processFrame(frametoProcess=cameraStream[-1])
            image = cameraStream[-1]
            if pel:
                blobs.append(pel)
                cv2.circle(image, (int(pel.x), int(pel.y)), int(pel.size), (0, 0, 255), thickness=2, shift=0)
            cv2.imshow("live frame", image)
            cv2.waitKey(1) & 0xFF

def isPellet():
    if len(blobs):
        return True
    else:
        return False

def getPellet():
    goHome()
    if isPellet():
        return True
    else:
        return False

def addFrames():
    global cameraOn
    global pelletPlaced
    while cameraOn:
        frametoProcess = Cam.FrameGenerator()
        cameraStream.append(frametoProcess.frame)
        if pelletPlaced:
            framesforvideo.append(frametoProcess)

def monitorPellet():
    global pelletPlaced
    first = time.time()
    while isPellet():
        blobs.pop()
        if not blobs:
            pelletPlaced = False
            pLog("Pellet no longer present.")
            if videoSave == "y":
                if len(framesforvideo) > 150:
                    pLog("Video now saving...")
                    videoProcess(_frames=framesforvideo)
            break
        time.sleep(0.1)

def activateTrial():
    global pelletPlaced
    pLog("Trial active.")
    if isPellet():
        pelletPlaced = True
        while pelletPlaced:
            monitorPellet()
        return True
    else:
        pLog("Pellet not placed")
        return False

start_stream = threading.Thread(target=addFrames)
start_stream.start()

blob_stream = threading.Thread(target=blobStream)
blob_stream.start()
