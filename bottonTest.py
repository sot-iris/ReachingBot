from motor import *
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def isHome():
    if GPIO.input(27) == 1:
        return True
    else:
        return False

def goHome():
    print("Going home.")
    actuate()
    time.sleep(1)
    while not isHome():
        time.sleep(0.3)
    stop()
    print("Home position.")

for i in range(10):
    goHome()
    time.sleep(1)
