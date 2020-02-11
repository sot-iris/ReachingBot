from pellet import *
import argparse

maxTrials = input("Please enter the number of trials: ")

trial = 0
error = 0

while True:
    try:
        if trial < int(maxTrials):
            if error < 6:
                print("Trial {}".format(trial))
                if getPellet(): #gets a pellet from the dispenser (which turns for 3 seconds), returns true if pellet dispense is successful
                    activateTrial()
                    trial += 1
                    error = 0
                else:
                    print("No pellet detected.")
                    error += 1
            else:
                print("Too many failed pellet retrievals")
                break
        else:
            print("Trials ended")
            break

    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        print("program terminated")
