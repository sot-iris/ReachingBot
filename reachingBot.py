from pellet import *
from reachingLogs import *
import argparse

maxTrials = input("Please enter the number of trials: ")

trial = 0
error = 0

while True:
    try:
        if trial < int(maxTrials):
            if error < 5:
                if getPellet(): #gets a pellet from the dispenser (which turns for 3 seconds), returns true if pellet dispense is successful
                    pLog("Trial {}".format(trial))
                    activateTrial()
                    trial += 1
                    error = 0
                else:
                    pLog("No pellet detected.")
                    error += 1
            else:
                pLog("Too many failed pellet retrievals")
                break
        else:
            pLog("Trials ended")
            break

    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        pLog("program terminated")
