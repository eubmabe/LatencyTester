# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 22:48:09 2016

@author: Mats
"""
import pyaudio
import wave
import time
import numpy as np

class testCtrl:
    
    def __init__(self,defaultSoundFile='test.wav',NOISE_FACTOR=1.0,PULSE_DETECT_SAMP=1000,filterLengthPrePeak=500,filterLengthPostPeak=200):
        self.recordedData = []
        self.NOISE_FACTOR=NOISE_FACTOR
        self.PULSE_DETECT_SAMP=PULSE_DETECT_SAMP
        self.edgeFilter = np.append(np.ones(filterLengthPrePeak)*-1,np.ones(filterLengthPostPeak))
        self.callBackCompleted = False
        self.playDuringNSRflag = False
        self.detectionLevels = {}
        self.p = pyaudio.PyAudio()
        self.defaultSoundFile = defaultSoundFile
        self.callBackFunctionPtr = None
        self.wf = wave.open(defaultSoundFile, 'rb') # wf part of class to simplify clean up
        self.PULSE_RATE = self.wf.getframerate()
        self.bytesPerSample = self.wf.getsampwidth()*self.wf.getnchannels()
        
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                    channels=self.wf.getnchannels(),
                    rate=self.PULSE_RATE,
                    output=True,
                    input = True,
                    stream_callback=self.callBackFunction)
        
        self.stream.start_stream()
        self.wf.close()
        self.wf = None # wf used to get correct audio file data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.stop_stream()
        self.stream.close()
        if self.wf is not None:
            self.wf.close()
        self.p.terminate()
        print 'Test ctrl destructed!!!'
        
    def waitForCallbackCompleted (self, timeout,callBack=None,callArg=None): # Timeout in number of loops
        loop_cnt =0
        while self.stream.is_active() and loop_cnt < timeout and not self.callBackCompleted:
            time.sleep(1)
            print 'Tick'
            if callBack is not None:
                retVal = callBack (loop_cnt,timeout,callArg)
            else:
                retVal = None
            if retVal is None:
                loop_cnt += 1
            else:
                loop_cnt = retVal
        self.callBackCompleted = False

    def setCallBackFunction (self,callBackPtr):
        self.callBackFunctionPtr = callBackPtr
        
    def callBackFunction(self,in_data, frame_count, time_info, status):
        data=''
        returnCode = pyaudio.paContinue
        if self.callBackFunctionPtr is not None:
            (data,returnCode,self.callBackCompleted) = self.callBackFunctionPtr (in_data, self.recordedData, frame_count, time_info, status)
        
        data += '\x00'*(frame_count*self.bytesPerSample-len (data))
        return (data, returnCode)
 
    def playSoundCallBack (self, in_data, recordedData, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        if data == '':
            return (data, pyaudio.paContinue,True)
        else:          
            return (data, pyaudio.paContinue,False)
        
    def playSound (self,maxTime,waveSrc):
        self.wf = wave.open(waveSrc, 'rb')
        self.setCallBackFunction (self.playSoundCallBack)
        print 'Wait for sound completion..'
        self.waitForCallbackCompleted(maxTime,None)
        print 'Sound completed...'
        self.setCallBackFunction(None)
        self.wf.close()
        self.wf = None

        
        
    def measureNSRcallBack (self,in_data, recordedData, frame_count, time_info, status):
        recordedData.append (in_data)
        data=''
        if self.playDuringNSRflag:
            data = self.wf.readframes(frame_count)
            dataSamples = len(data)/self.bytesPerSample
            while dataSamples < frame_count:
                self.wf.rewind()
                data += self.wf.readframes(frame_count-dataSamples)
                dataSamples = len(data)/self.bytesPerSample
        return (data, pyaudio.paContinue,False)
        
    def measureNSRLevel (self,testTime,waveSrc):
        self.recordedData = []
        self.playDuringNSRflag = False
        self.setCallBackFunction (self.measureNSRcallBack)
        time.sleep(testTime*0.5)
        dataChunkSilence = b''.join(self.recordedData)
        self.wf = wave.open(waveSrc, 'rb')
        self.recordedData = []
        self.playDuringNSRflag = False
        time.sleep(testTime*0.4)
        self.playDuringNSRflag = True
        time.sleep(testTime*0.1) # Pulse 20% of measure time
        dataChunkNoise = b''.join(self.recordedData)
        self.recordedData = []
        self.playDuringNSRflag = False
        self.setCallBackFunction(None)
        self.wf.close()
        self.wf = None

        recordedDataVec = np.abs(np.fromstring(dataChunkSilence, dtype='int{0}'.format(16)))
        recordedDataVec.shape = [len(dataChunkSilence)/self.bytesPerSample,2]
        self.detectionLevels[waveSrc]={'noiseLevel' : np.percentile (recordedDataVec, 95, axis=0)}
        print "Noise level = " + str(self.detectionLevels[waveSrc]['noiseLevel'])

        recordedDataVec = np.abs(np.fromstring(dataChunkNoise, dtype='int{0}'.format(16)))
        recordedDataVec.shape = [len(dataChunkNoise)/self.bytesPerSample,2]
        self.detectionLevels[waveSrc]['pulseLevel'] = np.percentile (recordedDataVec, 95, axis=0)
        print "Pulse level = " + str(self.detectionLevels[waveSrc]['pulseLevel'])
        
    def measureCallDelayCallBack (self, in_data, recordedData, frame_count, time_info, status):
        recordedData.append (in_data)

        data = self.wf.readframes(frame_count)
        
        return (data, pyaudio.paContinue,False)
        
    def measureCallDelay (self,testTime,waveSrc,outFile,devA,devB):
        self.recordedData = []
        self.wf = wave.open(waveSrc, 'rb')
        self.setCallBackFunction (self.measureCallDelayCallBack)
        self.waitForCallbackCompleted(testTime,self.detectPulses,waveSrc)
        time.sleep(0.1)
        self.setCallBackFunction(None)
        self.wf.close()
        self.wf = None
        dataChunk = b''.join(self.recordedData)
        self.recordedData = []
        
        recordedDataVec = np.abs(np.fromstring(dataChunk, dtype='int{0}'.format(16)))
        recordedDataVec.shape = [len(dataChunk)/self.bytesPerSample,2]
        #recordedDataVec = np.reshape(self.recordedData,newshape = [-1,2])
        np.save (outFile,recordedDataVec)
        ch0_SignalEdgeMask = np.correlate(recordedDataVec[:,0],self.edgeFilter)
        ch1_SignalEdgeMask = np.correlate(recordedDataVec[:,1],self.edgeFilter)
        np.save ('_0_'+outFile,ch0_SignalEdgeMask)
        np.save ('_1_'+outFile,ch1_SignalEdgeMask)
        ch0_SignalEdgeIndex = ch0_SignalEdgeMask.argmax()
        ch1_SignalEdgeIndex = ch1_SignalEdgeMask.argmax()
        pulseDelay = np.abs(ch0_SignalEdgeIndex-ch1_SignalEdgeIndex)*1.0/self.PULSE_RATE
        print devA,'-->',devB,str(pulseDelay),str(ch0_SignalEdgeIndex),str(ch1_SignalEdgeIndex)
        return (devA,devB,pulseDelay,ch0_SignalEdgeIndex,ch1_SignalEdgeIndex)
        
    def detectPulses (self,currTime,endTime,waveSrc):
        dataChunk = b''.join(self.recordedData)
        recordedDataVec = np.abs(np.fromstring(dataChunk, dtype='int{0}'.format(16)))
        recordedDataVec.shape = [len(dataChunk)/self.bytesPerSample,2]
        #recordedData.append (dataChunk)
        #recordedDataVec = np.reshape(self.recordedData,newshape = [-1,2])
        detectVec = (recordedDataVec>((self.detectionLevels[waveSrc]['pulseLevel']+self.detectionLevels[waveSrc]['noiseLevel'])/2*self.NOISE_FACTOR)).sum(axis=0)
        print 'Detections' + str(detectVec) + ' Limit ' + str((self.detectionLevels[waveSrc]['pulseLevel']+self.detectionLevels[waveSrc]['noiseLevel'])/2*self.NOISE_FACTOR)
        if (detectVec>self.PULSE_DETECT_SAMP).sum() == 2:
            print "Pulse on both channels detected!!!"
            return endTime

        return None