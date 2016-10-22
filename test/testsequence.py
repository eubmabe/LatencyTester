# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 03:44:25 2016

@author: Mats
"""

import RPi.GPIO as GPIO
import time
import pyaudio
import wave




# Init test bed
#wf = wave.open('OKgoogleLeft.wav', 'rb')
wf = wave.open('CallB_Left.wav', 'rb')
# instantiate PyAudio (1)
p = pyaudio.PyAudio()
# define callback (2)
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

# Wait a couple of seconds and play "go google" to activate google voice recognition
time.sleep(3)
print 'Start play OK google on left channel'
# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=pyAudioCallback)
stream.start_stream()

while stream.is_active():
    time.sleep(0.1)


# Clean up everything....
# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()
# close PyAudio (7)

time.sleep(20)

# Press button 2 sec (left channel)
print 'Press mic button'
GPIO.output(channel, GPIO.HIGH)
# Wait 2 seconds and release
time.sleep(1)
print 'Release mic button'
GPIO.setup(channel, GPIO.OUT, initial=GPIO.LOW)


"""
wf = wave.open('CallB_Left.wav', 'rb')
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=pyAudioCallback)
stream.start_stream()

while stream.is_active():
    time.sleep(0.1)

# Clean up everything....
# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()
# close PyAudio (7)
"""

p.terminate()

GPIO.cleanup()



# Play Call B to left channel

# Listen for reply??? (or at least tones stopping...)
# Maybe start easy with long delay....

# Perform tests

# Hang ut by press button left channel (and maybe b as well)