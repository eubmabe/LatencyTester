# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 00:34:53 2016

@author: Mats
"""

import RPi.GPIO as GPIO
import time

channel = 12
state = GPIO.LOW
GPIO.setmode(GPIO.BOARD)
GPIO.setup(channel, GPIO.OUT, initial=state)

while True:
    GPIO.output(channel, state)
    if state = GPIO.LOW:
        print 'LOW'
        state = GPIO.HIGH
    else:
        print 'HIGH'
        state = GPIO.LOW
    time.sleep(5)

GPIO.cleanup()