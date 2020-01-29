from pellet import *
import argparse
import time

trial = 0
error = 0

print("Starting. Waiting 3 seconds to initiate.")
time.sleep(3)

while True:
    try:
        if trial < 50:
            if error < 6:
                print("Trial {}".format(trial))
                if isPellet(): #asks whether there's a pellet on the spoon
                    activateTrial() #returns true if the pellet was positioned correctly
                    error = 0
                    trial += 1
                elif getPellet(): #gets a pellet from the dispenser (which turns for 3 seconds), returns true if pellet dispense is successful
                    activateTrial()
                    trial += 1
                    error = 0
                else:
                    print("No pellet detected.")
                    error += 1
            else:
                primt("Too many failed pellet retrievals")
                break
        else:
            print("Trials ended")
            break

    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        print("program terminated")
