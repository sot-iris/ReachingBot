from __future__ import division
from motor import *
from collections import deque
from camera import *
import time
import threading
import numpy as np

from uuid import getnode as get_mac
mac = get_mac()

Cam = Camera(width=480, height=640, FPS=250, rotation=90)
waitTime = 600 #number of seconds the pellet is monitored for
framesforvideo = deque(maxlen=700) #contains the frames that'll get stored to video
cameraStream = deque(maxlen=10) #containts the frames from the live stream
blobs = deque(maxlen=10) #contains instances of the Pellet class
pelletPlaced = False #used to stop and start appending frames to buffer that'll get

class Pellet:
    def __init__(self, x, y, size, timestamp):
        self.x = x
        self.y = y
        self.size = size
        self.timestamp = timestamp

def processFrame(frametoProcess, cropping=[0,320,0,480]):
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
            image = cameraStream[-1][160:480,0:480]
            if pel:
                blobs.append(pel)
                #cv2.circle(image, (int(pel.x/0.4), int(pel.y/0.4)), int(pel.size), (0, 0, 255), thickness=2, shift=0)
            cv2.imshow("live frame", image)
            #cv2.destroyAllWindows()
            cv2.waitKey(1) & 0xFF

def isPellet():
    if len(blobs):
        return True
    else:
        return False

def getPellet():
    goDown()
    goUp()
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
            sotLog("Trial took too long.")
            pelletPlaced = False
            break
        elif not blobs:
            sotLog("Video saving thread started...")
            #savetheVid = threading.Thread(target=videoProcess, args=(getTagStatus(), cameraStream))
            #savetheVid.start()
            pelletPlaced = False
            sotLog("Pellet no longer present.")
            videoProcess(getTagStatus(), framesforvideo)
            framesforvideo.clear()
            break
        time.sleep(0.1)

def activateTrial():
    global pelletPlaced
    print("Trial active.")
    if getPellet():
        pelletPlaced = True
        while pelletPlaced:
            monitorPellet()
        print("Video saved locally.")
        return True
    else:
        print("Pellet not placed")
        return False

start_stream = threading.Thread(target=addFrames)
start_stream.start()

blob_stream = threading.Thread(target=blobStream)
blob_stream.start()
