# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 03:44:25 2016

@author: Mats
"""

import testCtrl as TC
import time
import sys
import numpy as np


    

click_delay = 0.5
filterLengthPrePeak = 500
filterLengthPostPeak = 200
NOISE_FACTOR=0.8
PULSE_DETECT_SAMP=500
if len(sys.argv) >=2:
    click_delay = float(sys.argv[1])
if len(sys.argv) >=4:
    filterLengthPrePeak = float(sys.argv[2])
    filterLengthPostPeak = float(sys.argv[3])
if len(sys.argv) >=6:
    NOISE_FACTOR = float(sys.argv[4])
    PULSE_DETECT_SAMP = float(sys.argv[5])
print("Click delay = " + str (click_delay))
print("Filter param = " + str (filterLengthPrePeak),str (filterLengthPostPeak))
print("Edge param = " + str (NOISE_FACTOR),str (PULSE_DETECT_SAMP))


# Init test bed
# instantiate testObject
with TC.testCtrl(defaultSoundFile='test.wav',NOISE_FACTOR=NOISE_FACTOR,PULSE_DETECT_SAMP=PULSE_DETECT_SAMP,filterLengthPrePeak=filterLengthPrePeak,filterLengthPostPeak=filterLengthPostPeak) as testObj:
    #testObj = TC.testCtrl(defaultSoundFile='test.wav',NOISE_FACTOR=20,PULSE_DETECT_SAMP=1000)
    
    testName=raw_input('Enter test name: ')
    devAName=raw_input('Enter device A descriptor: ')
    devBName=raw_input('Enter device B descriptor: ')
    print 'Starting test: '+testName, devAName,'<-->',devBName
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
    noTestSeq = 5
    noTestPerSeq = 5
    testResultList = []
    for i in range(noTestSeq):
        for j in range(noTestPerSeq):
            testResultList.append(testObj.measureCallDelay(2,'testPulseLeft.wav','out1NP.npy',devAName,devBName))
            time.sleep(0.1)
    for i in range(noTestSeq):
        for j in range(noTestPerSeq):
            testResultList.append(testObj.measureCallDelay(2,'testPulseRight.wav','out2NP.npy',devBName,devAName))
            time.sleep(0.1)
    
    print 'COMPLETED!!!!'
    
    np.savetxt(testName+'.csv',np.asarray(testResultList),header='deviceA,deviceB,delay,indexIn,indexOut',comments='',fmt="%s",delimiter=',') 
