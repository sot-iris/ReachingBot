import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def isHome():
    if GPIO.input(27) == 1:
        return True
    else:
        return False

while True:
    print(isHome())
