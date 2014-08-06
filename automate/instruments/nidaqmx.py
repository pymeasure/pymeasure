#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# DAQmx wrapper -- DAQ device
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Most of this code originally from http://www.scipy.org/Cookbook/Data_Acquisition_with_NIDAQmx

import ctypes
import numpy as np
import logging
nidaq = ctypes.windll.nicaiu

# Data Types
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
# Constants
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 1

class DAQ(object):
	"""Instrument object for interfacing with NI-DAQmx devices."""
	def __init__(self, name, *args, **kwargs):
		super(DAQ, self).__init__()
		self.resourceName = name
		self.numChannels = 0
		self.numSamples = 0
		self.dataBuffer = 0
		self.taskHandleAI = TaskHandle(0)
		self.taskHandleAO = TaskHandle(0)
		self.terminated = False

	def setupAnalogVoltageIn(self, channelList, numSamples, sampleRate=10000, scale=3.0):
		resourceString = ""
		for num, channel in enumerate(channelList):
			if num > 0:
				resourceString += ", " # Add a comma before entries 2 and so on
			resourceString += self.resourceName + "/ai" + str(num)
		self.numChannels = len(channelList)
		self.numSamples = numSamples
		self.taskHandleAI = TaskHandle(0)
		self.dataBuffer = np.zeros((self.numSamples,self.numChannels), dtype=np.float64)
		self.CHK(nidaq.DAQmxCreateTask("",ctypes.byref(self.taskHandleAI)))
		self.CHK(nidaq.DAQmxCreateAIVoltageChan(self.taskHandleAI,resourceString,"",
								   DAQmx_Val_Cfg_Default,
								   float64(-scale),float64(scale),
								   DAQmx_Val_Volts,None))
		self.CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandleAI,"",float64(sampleRate),
								DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,
								uInt64(self.numSamples)));

	def setupAnalogVoltageOut(self, channel=0):
		resourceString = self.resourceName + "/ao" + str(channel)
		self.taskHandleAO = TaskHandle(0)
		self.CHK(nidaq.DAQmxCreateTask("", ctypes.byref( self.taskHandleAO )))
		self.CHK(nidaq.DAQmxCreateAOVoltageChan( self.taskHandleAO,
				resourceString, "",
				float64(-10.0), float64(10.0),
				DAQmx_Val_Volts, None))

	def setupAnalogVoltageOutMultipleChannels(self, channelList):
		resourceString = ""
		for num, channel in enumerate(channelList):
			if num > 0:
				resourceString += ", " # Add a comma before entries 2 and so on
			resourceString += self.resourceName + "/ao" + str(num)
		self.taskHandleAO = TaskHandle(0)
		self.CHK(nidaq.DAQmxCreateTask("", ctypes.byref( self.taskHandleAO )))
		self.CHK(nidaq.DAQmxCreateAOVoltageChan( self.taskHandleAO,
				resourceString, "",
				float64(-10.0), float64(10.0),
				DAQmx_Val_Volts, None))


	def writeAnalogVoltage(self, value):
		timeout = -1.0 
		self.CHK(nidaq.DAQmxWriteAnalogScalarF64( self.taskHandleAO,
			1, # Autostart 
			float64(timeout), 
			float64(value), 
			None))

	def writeAnalogVoltageMultipleChannels(self, values):
		timeout = -1.0 
		self.CHK(nidaq.DAQmxWriteAnalogF64( self.taskHandleAO,
			1, # Samples per channel
			1, # Autostart 
			float64(timeout),
			DAQmx_Val_GroupByChannel,
			(np.array(values)).ctypes.data,
            None, None))

	def acquire(self):
		read = int32()
		self.CHK(nidaq.DAQmxReadAnalogF64(self.taskHandleAI ,self.numSamples,float64(10.0),
								DAQmx_Val_GroupByChannel, self.dataBuffer.ctypes.data,
								self.numChannels*self.numSamples,ctypes.byref(read),None))	
		return self.dataBuffer.transpose()

	def acquireAverage(self):
		if not self.terminated:
			avg = np.mean(self.acquire(), axis=1)
			return avg
		else:
			return np.zeros(3)

	def stop(self):
		if self.taskHandleAI.value != 0:
			nidaq.DAQmxStopTask(self.taskHandleAI)
			nidaq.DAQmxClearTask(self.taskHandleAI)
		if self.taskHandleAO.value != 0:
			nidaq.DAQmxStopTask(self.taskHandleAO)
			nidaq.DAQmxClearTask(self.taskHandleAO)

	def CHK(self, err):
		"""a simple error checking routine"""
		if err < 0:
			buf_size = 100
			buf = ctypes.create_string_buffer('\000' * buf_size)
			nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
			raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))
		if err > 0:
			buf_size = 100
			buf = ctypes.create_string_buffer('\000' * buf_size)
			nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
			raise RuntimeError('nidaq generated warning %d: %s'%(err,repr(buf.value)))

	def shutdown(self):
		self.stop()
		self.terminated = True
