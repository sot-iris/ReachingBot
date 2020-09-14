#!/usr/bin/env python3
import time
import threading
import RPi.GPIO as GPIO
from smbus import SMBus
from uuid import getnode as get_mac

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

mac = get_mac()
b = SMBus(1)
motoraddr = int(17)

rest_command_timeout = 0x8C
energize = 0x85
exit_safe_start = 0x83
de_energize = 0x86
set_velocity = 0xE3

MotorActive = False

def computeTime(firstTime, secondInput):
    first = firstTime
    second = secondInput
    difference = second - first
    return difference

def convert(x):
    Byte4 = x & 0xff
    Byte3 = (x >> 8) & 0xff
    Byte2 = (x >> 16) & 0xff
    Byte1 = x >> 24
    bytearray = [Byte4, Byte3, Byte2, Byte1]
    return bytearray

def reset(motor):
    motorController(motor, exit_safe_start, "ExitSafeStart")
    motorController(motor, energize, "Energize")

def motorController(motor, command, function_name, data=None):
    while True:
        try:
            if function_name == 'SetVelocity':
                b.write_block_data(motor, command, data)
            else:
                b.write_byte(motor, command)
            break
        except IOError:
            time.sleep(1)
            try:
                while True:
                    reset(motor)
                    b.write_byte(motor, command)
                    break
            except IOError:
                pass
            print("IOError -- Motor: " + str(motor) + " Command: " + function_name)

def moveCols(direction, speed=15000, duration=0):
    first = time.time()
    if direction == "CW":
        signed_speed = speed * -1
    elif direction == "CCW":
        signed_speed = speed
    motorController(motoraddr, exit_safe_start, "ExitSafeStart")
    motorController(motoraddr, energize, "Energize")
    motorController(motoraddr, set_velocity, "SetVelocity", convert(signed_speed))
    if duration == 0:
        print("Motor activated.")
    else:
        time.sleep(duration)
        motorController(motoraddr, de_energize, "DeEnergize")

def initiateMotors():
    global MotorActive
    while True:
        if not MotorActive:
            motorController(motoraddr, de_energize, "de_energize")
        motorController(motoraddr, exit_safe_start, "ExitSafeStart")
        time.sleep(0.8)

def actuate():
    global MotorActive
    MotorActive = True
    moveCols(direction="CW", duration=0)

def stop():
    global MotorActive
    MotorActive = False

def isHome():
    if GPIO.input(27) == 1:
        return True
    else:
        return False

def goHome():
    actuate()
    time.sleep(1)
    while not isHome():
        time.sleep(0.3)
    stop()

startMotors = threading.Thread(target=initiateMotors)
startMotors.start()

if __name__ == "__main__":
    while True:
        time.sleep(4)
        actuate(5)
