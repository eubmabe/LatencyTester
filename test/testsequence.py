# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 03:44:25 2016

@author: Mats
"""

import RPi.GPIO as GPIO
import time
import pyaudio
import wave
import sys
import numpy as np

def dummyPrint ():
    return
    
def handleSound (fileName, callBackFunction, inFlag = False, printFunction = dummyPrint):
    wf = wave.open(fileName, 'rb')
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    input = inFlag,
                    stream_callback=callBackFunction)
    stream.start_stream()
    
    while stream.is_active():
        time.sleep(0.1)
        printFunction ()
     
    # Clean up everything....
    # stop stream (6)
    stream.stop_stream()
    stream.close()
    wf.close()


click_delay = 0.5
if len(sys.argv) >=2:
    click_delay = float(sys.argv[1])

print("Click delay = " + str (click_delay))


# Init test bed
# instantiate PyAudio (1)
p = pyaudio.PyAudio()
# define callback (2)
wf = None
def pyAudioCallback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    return (data, pyaudio.paContinue)

    
print 'Init GPIO'
channel = 12 #pin #12 used
GPIO.setmode(GPIO.BOARD)
# Mic button not pressed GPIO.HIGH activate button
GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)
time.sleep(5)




# Press button 2 sec (left channel)
print 'Press mic button'
GPIO.output(channel, GPIO.HIGH)
# Wait 2 seconds and release
time.sleep(2)
print 'Release mic button'
GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)



# Wait a couple of seconds and play "command" to set-up call via voice recognition
time.sleep(3)
print 'Start play OK google on left channel'
# open stream using callback (3)
handleSound ('CallB_Left.wav', pyAudioCallback)

#Wait for call set-up to complete
# Can be improved by sending sound from phone B
# But let's keep it simple to start with
time.sleep(20)

#Play test sound to see that it works in both directions
handleSound ('test.wav', pyAudioCallback)
time.sleep(2) # Give time to sence silence

# Start test

def printState ():
    global recordTestState
    global printTestState
    
    if printTestState != recordTestState:
        print 'STATE = ' + str(recordTestState)
        printTestState = recordTestState

def pyTestSequenceCallback (in_data, frame_count, time_info, status, printState):
    global recordedData
    global noiseLevel
    global RECORD_STATE
    global recordTestState
    global noRecData

    returnCode = pyaudio.paContinue
    if len(in_data) > 0:
        dataChunk = np.abs(np.fromstring(in_data, dtype='int{0}'.format(16)))
        dataChunk.shape = [frame_count,2]
        recordedData.append (dataChunk)
        noRecData += frame_count
    
        if recordTestState <= RECORD_STATE['MEASURE_NOISE_LEVEL']:
            recordTestState += 1
            if noiseLevel:
                noiseLevel = (noiseLevel+dataChunk.mean())/2
            else:
                noiseLevel = dataChunk.mean()
        elif recordTestState == RECORD_STATE['SEND_PULSE']:
            data = wf.readframes(frame_count)
            if data == '':
                recordTestState = RECORD_STATE['DETECT_OUT_PULSE']
        elif recordTestState == RECORD_STATE['DETECT_OUT_PULSE']:
            if dataChunk.mean() > noiseLevel * 10:
                wf.rewind()
                recordTestState = RECORD_STATE['WAIT_FOR_PULSE_TIME']
        elif recordTestState == RECORD_STATE['WAIT_FOR_PULSE_TIME']:
            measureTimePulse = wf.readframes(frame_count)
            if measureTimePulse == '':
                recordTestState = RECORD_STATE['DETECT_RETURN_PULSE']
        elif recordTestState == RECORD_STATE['DETECT_RETURN_PULSE']:
            if dataChunk.mean() > noiseLevel * 10:
                wf.rewind()
                recordTestState = RECORD_STATE['WAIT_FOR_RET_PULSE_TIME']
        elif recordTestState == RECORD_STATE['WAIT_FOR_RET_PULSE_TIME']:
            measureTimePulse = wf.readframes(frame_count/4) # Add some extra delay
            if measureTimePulse == '':
                returnCode = pyaudio.paComplete
            
            
    if data == '': # Play silence
        data = '\x00'*frame_count*4 # wf.getsampwidth()*wf.getnchannels()
    
    return (data, returnCode)
    
recordedData = []
noRecData = 0
noiseLevel = 0
RECORD_STATE = {'START':-10,'MEASURE_NOISE_LEVEL':0,'SEND_PULSE':1,'DETECT_OUT_PULSE':2,'WAIT_FOR_PULSE_TIME':3,'DETECT_RETURN_PULSE':4,'WAIT_FOR_RET_PULSE_TIME':3}
recordTestState = RECORD_STATE['START']
printTestState = recordTestState

handleSound ('testPulseLeft.wav', pyTestSequenceCallback, True)

recordedDataVec = np.reshape(recordedData,newshape = [noRecData,2])




#handleSound ('testPulseRight.wav', pyTestSequenceCallback, True)


#Play Call B to left channel

# Listen for reply??? (or at least tones stopping...)
# Maybe start easy with long delay....

# Perform tests

# Hang ut by press button left channel (and maybe b as well)

#a=np.fromstring(wf.readframes(int(100)), dtype='int{0}'.format(16))
#a.shape=(100,2)

# Clean up
# Short press mic button (left channel to hang-up, long press mute phone)
print 'Press mic button'
GPIO.output(channel, GPIO.HIGH)
# Wait 2 seconds and release
time.sleep(click_delay)
print 'Release mic button'
GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)

time.sleep(1) # Give time to sence LOW


p.terminate()
GPIO.cleanup()
