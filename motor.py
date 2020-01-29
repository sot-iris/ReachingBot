#!/usr/bin/env python3
import time
import threading
import RPi.GPIO as GPIO
from smbus import SMBus
from uuid import getnode as get_mac

mac = get_mac()
b = SMBus(1)
motoraddr = int(14)

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

def moveCols(direction, speed=15000, duration=1):
    first = time.time()
    if direction == "CW":
        signed_speed = speed * -1
    elif direction == "CCW":
        signed_speed = speed
    motorController(motoraddr, exit_safe_start, "ExitSafeStart")
    motorController(motoraddr, energize, "Energize")
    motorController(motoraddr, set_velocity, "SetVelocity", convert(signed_speed))
    time.sleep(duration)
    motorController(motoraddr, de_energize, "DeEnergize")

def initiateMotors():
    global MotorActive
    while True:
        if not MotorActive:
            motorController(motoraddr, de_energize, "de_energize")
        motorController(motoraddr, exit_safe_start, "ExitSafeStart")
        time.sleep(0.8)

def goDown():
    print("going Down")
    global MotorActive
    MotorActive = True
    moveCols(direction="CW", duration=20)
    MotorActive = False

def goUp():
    print("going Up")
    global MotorActive
    MotorActive = True
    moveCols(direction="CCW", duration=20)
    MotorActive = False

startMotors = threading.Thread(target=initiateMotors)
startMotors.start()
