from __future__ import division
from motor import *
from collections import deque
from tqdm import tqdm
from camera import *
from reachingLogs import *
import time
import threading
import os
import pickle
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Firmware for running the ReachingBot.')
parser.add_argument('-v', '--videoSave', action='store_true', help='Do you want to save the videos?')
parser.add_argument('-s', '--showImage', action='store_true', help='Do you want to display the live image?')
parser.add_argument('-m', '--maxTrials', type=int, metavar='', required=True, help='Number of trials to execute.')
parser.add_argument('-o', '--timeTrial', type=int, metavar='', required=True, help='Number of minutes for session.')
parser.add_argument('-r', '--RFID', metavar='', help='RFID number of the animal.')
parser.add_argument('-t','--timePoint', metavar='', help='Time point within your study in weeks.')
args = parser.parse_args()

if args.videoSave and (args.RFID is None or args.timePoint is None):
    parser.error('--videoSave requires --RFID and --timePoint.')

if args.videoSave:
    folder = "{}_{}".format(args.RFID, args.timePoint)
    if not os.path.exists(folder):
        os.makedirs((folder))
else:
    pLog("Not saving videos.")

overallTime = args.timeTrial * 60
waitTime = 60
Cam = Camera()
framesforvideo = deque(maxlen=350) #contains the frames that'll get stored to video
cameraStream = deque(maxlen=10) #containts the frames from the live stream
blobs = deque(maxlen=10) #contains instances of the Pellet class
pelletPlaced = False #used to stop and start appending frames to buffer that'll get
trial_number = 1
cameraOn = True
active = True

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

def stopCamera():
    global cameraOn
    turnOff()
    cameraOn = False

def videoProcess(_frames=None):
    global trial_number
    finalFrames = _frames
    videoName = "{}/{}_{}_trial{}.avi".format(folder, args.RFID, args.timePoint, trial_number)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(videoName, fourcc, 30, (320, 240))
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
                if args.showImage:
                    cv2.circle(image, (int(pel.x), int(pel.y)), int(pel.size), (0, 0, 255), thickness=2, shift=0)
            if args.showImage:
                cv2.imshow("live frame", image)#[140:240,90:160])
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
            if args.videoSave:
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

def timer():
    global active
    counter = 0
    while True:
        counter += 1
        time.sleep(1)
        print(counter)
        if counter > overallTime:
            active = False
            break

start_stream = threading.Thread(target=addFrames)
start_stream.start()

blob_stream = threading.Thread(target=blobStream)
blob_stream.start()

time_stream = threading.Thread(target=timer)
time_stream.start()

if __name__ == '__main__':
    trial = 0
    error = 0
    while active:
        try:
            if trial < int(args.maxTrials):
                if error < 5:
                    if getPellet(): #gets a pellet from the dispenser (which turns for 3 seconds), returns true if pellet dispense is successful
                        pLog("Trial {}".format(trial))
                        activateTrial()
                        trial += 1
                        error = 0
                    else:
                        pLog("No pellet detected.")
                        error += 1
                elif error > 5:
                    pLog("Too many failed pellet retrievals")
                    break
            else:
                pLog("Trials ended")
                break

        except KeyboardInterrupt:
            stopCamera()
            cv2.destroyAllWindows()
            pLog("program terminated")
            break

    print("Session ended after {} minute(s).".format(args.timeTrial))
    cv2.destroyAllWindows()
    stopCamera()
    print("All done here")
