# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 03:44:25 2016

@author: Mats
"""

import RPi.GPIO as GPIO
import testCtrl as TC
import time
import sys


    

click_delay = 0.5
if len(sys.argv) >=2:
    click_delay = float(sys.argv[1])
print("Click delay = " + str (click_delay))


# Init test bed
# instantiate testObject
with TC.testCtrl(defaultSoundFile='test.wav',NOISE_FACTOR=1,PULSE_DETECT_SAMP=1000) as testObj:
    #testObj = TC.testCtrl(defaultSoundFile='test.wav',NOISE_FACTOR=20,PULSE_DETECT_SAMP=1000)
    
    print 'Init GPIO'
    channel = 12 #pin #12 used
    GPIO.setmode(GPIO.BOARD)
    # Mic button not pressed GPIO.HIGH activate button
    GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)
    time.sleep(2)
    
    # Press button 2 sec (left channel)
    print 'Press mic button'
    GPIO.output(channel, GPIO.HIGH)
    # Wait 2 seconds and release
    time.sleep(2)
    print 'Release mic button'
    GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)
    
    
    
    # Wait a couple of seconds and play "command" to set-up call via voice recognition
    time.sleep(3)
    print 'Play call test number on left channel'
    
    testObj.playSound (10,'CallB_Left.wav')
    
    print 'Command played'
    #Wait for call set-up to complete
    # Can be improved by sending sound from phone B
    # But let's keep it simple to start with
    time.sleep(15)
    
    print 'Play test sound'
    testObj.playSound (10,'test.wav')
    time.sleep(1)
    print 'Start noise measurement'
    testObj.measureNSRLevel(5,'testPulseLeft.wav')
    time.sleep(3)
    print 'Start noise measurement'
    testObj.measureNSRLevel(5,'testPulseRight.wav')
    time.sleep(3)
    print 'Start test ..'
    testObj.measureCallDelay(10,'testPulseLeft.wav','out1NP.npy')
    time.sleep(1)
    testObj.measureCallDelay(10,'testPulseRight.wav','out2NP.npy')
    time.sleep(1)
    testObj.measureCallDelay(10,'testPulseLeft.wav','out1bNP.npy')
    time.sleep(1)
    testObj.measureCallDelay(10,'testPulseRight.wav','out2bNP.npy')
    
    print 'COMPLETED!!!!'
    
    
    print 'Press mic button'
    GPIO.output(channel, GPIO.HIGH)
    # Wait 2 seconds and release
    time.sleep(click_delay)
    print 'Release mic button'
    GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)
    
    time.sleep(1) # Give time to sence LOW


GPIO.cleanup()
