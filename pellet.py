from __future__ import division
from motor import *
from collections import deque
from camera import *
import time
import threading
import numpy as np

from uuid import getnode as get_mac

Cam = Camera(width=320, height=240, FPS=250, rotation=90)
framesforvideo = deque(maxlen=700) #contains the frames that'll get stored to video
cameraStream = deque(maxlen=10) #containts the frames from the live stream
blobs = deque(maxlen=10) #contains instances of the Pellet class
pelletPlaced = False #used to stop and start appending frames to buffer that'll get
trial_number = 1

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
    finalFrames = _frames
    videoName = "test.avi"
    out = cv2.VideoWriter(videoName, cv2.cv.CV_FOURCC(*"XVID"), 30, (320, 240))
    fps = len(finalFrames) / (finalFrames[-1].time - finalFrames[0].time)
    print("fps: {}".format(fps))
    for n in range(len(finalFrames)):
        try:
            roi = cv2.cvtColor(finalFrames[n].frame, cv2.COLOR_GRAY2BGR)
            out.write(roi)
        except:
            print("this was the frame number: {}".format(n))
    out.release()
    print("{} saved.".format(videoName))

def processFrame(frametoProcess, cropping=[140,240,130,200]):
    y1, y2, x1, x2 = cropping
    _frame_ = frametoProcess[y1:y2, x1:x2]
    processed =  BlobDetection(_frame_)
    if processed:
        x, y, size, time = processed
        return Pellet(x, y, size, time)
    else:
        return None

def blobStream():
    while True:
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
    print("cam stream started")
    global pelletPlaced
    while True:
        frametoProcess = Cam.FrameGenerator()
        cameraStream.append(frametoProcess.frame)
        if pelletPlaced:
            framesforvideo.append(frametoProcess)

def monitorPellet():
    global pelletPlaced
    first = time.time()
    while isPellet():
        blobs.pop()
        if computeTime(first, time.time()) > waitTime:
            print("Trial took too long.")
            pelletPlaced = False
            break
        elif not blobs:
            pelletPlaced = False
            print("Pellet no longer present.")
            if len(framesforvideo) > 150:
                print("Video now saving...")
                videoProcess(_frames=framesforvideo)
                vidSave.start()
            break
        time.sleep(0.1)

def activateTrial():
    global pelletPlaced
    print("Trial active.")
    if isPellet():
        pelletPlaced = True
        while pelletPlaced:
            monitorPellet()
        return True
    else:
        print("Pellet not placed")
        return False

start_stream = threading.Thread(target=addFrames)
start_stream.start()

blob_stream = threading.Thread(target=blobStream)
blob_stream.start()
