from __future__ import division
from motor import *
from collections import deque
from camera import *
import time
import threading
import numpy as np

from uuid import getnode as get_mac

videoProcessed = True
mac = get_mac()
animalName = input("Please enter RFID number for aninal: ")
Cam = Camera(width=480, height=640, FPS=250, rotation=90)
waitTime = 60 #number of seconds the pellet is monitored for
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

def videoProcess(ID=None, _frames=None):
    global videoProcessed
    global trial_number
    videoProcessed = False
    finalFrames = _frames
    if len(finalFrames) > 0:
        print("number of frames: {}".format(len(finalFrames)))
     #accepts RFID tag of animal and the list of frames to encode to video
        timestamp = str(datetime.datetime.now()).split(" ")[1].split(".")[0].strip(":")
        date = str(datetime.datetime.now()).split(" ")[0]
        videoName = "AnimalID{}_TrialNo{}_{}_{}.avi".format(ID, trial_number, date, remove(":", timestamp)) #creature _ trial number _ date _ time
        trial_number += 1
        out = cv2.VideoWriter(videoName, cv2.cv.CV_FOURCC(*"XVID"), 30, (480, 350))
        fps = len(finalFrames) / (finalFrames[-1].time - finalFrames[0].time)
        print("fps: {}".format(fps))
        for n in range(len(finalFrames)):
            try:
                roi = cv2.cvtColor(finalFrames[n].frame[50:400, 0:480], cv2.COLOR_GRAY2BGR)
                out.write(roi)
            except:
                print("this was the frame number: {}".format(n))
        out.release()
        framesforvideo.clear()
        videoProcessed = True
        print("done")
    else:
        print("No frames to process...")

def processFrame(frametoProcess, cropping=[160,480,0,480]):
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
                cv2.circle(image, (int(pel.x/0.4), int(pel.y/0.4)), int(pel.size), (0, 0, 255), thickness=2, shift=0)
            cv2.imshow("live frame", image)
            cv2.waitKey(1) & 0xFF

def isPellet():
    if len(blobs):
        return True
    else:
        return False

def getPellet():
    global videoProcessed
    goDown()
    while not videoProcessed:
        time.sleep(0.5)
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
            print("Trial took too long.")
            pelletPlaced = False
            break
        elif not blobs:
            pelletPlaced = False
            print("Pellet no longer present.")
            print("Video saving.")
            vidSave = threading.Thread(target=videoProcess, kwargs=dict(ID=animalName, _frames=framesforvideo))
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
        print("Video saved locally.")
        return True
    else:
        print("Pellet not placed")
        return False

start_stream = threading.Thread(target=addFrames)
start_stream.start()

blob_stream = threading.Thread(target=blobStream)
blob_stream.start()
