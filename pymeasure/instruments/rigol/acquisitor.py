
import numpy as np

from .enums import *
from ..oscilloscope import IWaveformAcquisitor

RigolAcquisitionChannel = None

class WaveformAcquisitor(IWaveformAcquisitor):
    __slots__ = ("hal", "preamble")
    def __init__(self, hal, channels):
        super().__init__(hal, channels)
        self.hal.waveform_mode = WaveformMode.raw
        self.hal.format = self.selectWaveformSampleFormat()
        
        for i, ch in enumerate(self.channels):
            sms = ch.supported_memory_sizes
            if sms is not None:
                selectedMemorySize = max(sms)
                print("WaveformAcquisitor.__init__ ch", ch, "selectedMemorySize", selectedMemorySize, "ch.total_points", ch.total_points)
                if ch.total_points != selectedMemorySize:
                    ch.total_points = selectedMemorySize
        
        self.preamble = self.hal.waveform_preamble


class WaveformSynchronisedAcquisitor(WaveformAcquisitor):
    def __init__(self, hal, channels):
        print("WaveformSynchronisedAcquisitor.__init__ channels", channels)
        super().__init__(hal, channels)
        self.hal.trigger_sweep_mode = SweepMode.single
        self.hal.mode = DeviceMode.single
        self.points_in_batch = self.get_points_in_a_batch(channels)
        acquisition_type = self.hal.acquisition_type
        self.preamble = self.hal.waveform_preamble
        
        self.total_points = self.get_total_points()
    
    def selectWaveformSampleFormat(self):
        selectedF = None
        selectedFLen = 0
        
        for f in self.hal.get_supported_waveform_formats():
            if 0 <= f.value < len(waveformFormatMapping):
                curL = waveformFormatMapping[f.value].itemsize
                if curL > selectedFLen:
                    selectedF = f
                    selectedFLen = curL
        return selectedF
    
    def get_points_in_a_batch(self, channels):
        waveform_mode = self.hal.waveform_mode
        acquisition_type = self.hal.acquisition_type
        points_in_batch = float("inf")
        for c in channels:
            curRes = c.get_points_in_a_batch(waveform_mode, acquisition_type, channels)
            if curRes is not None:
                points_in_batch = min(points_in_batch, curRes)
        return points_in_batch
    
    def get_total_points(self):
        #return self.preamble.points
        total_points = 0
        for i, ch in enumerate(self.channels):
            totalPointsCh = ch.total_points
            print("get_total_points", i, "ch", ch, "ch.total_points", ch.total_points)
            if totalPointsCh:
                total_points = max(totalPointsCh, total_points)
        
        #for i, ch in enumerate(self.channels):
        #    ch.total_points = total_points
        return total_points
    
    def __call__(self):
        self.hal.mode = DeviceMode.stop
        self.hal.trigger()
        self.hal.wait_acquisition()
        res = [None] * len(self.channels)
        for i, ch in enumerate(self.channels):
            #ch.
            if isinstance(ch, RigolAcquisitionChannel):
                print("WaveformSynchronisedAcquisitor.__call__", i, "ch", ch, "total_points", ch.total_points, )
            gotWf = ch.get_waveform(self.total_points, self.preamble.type, self.points_in_batch)
            print("WaveformSynchronisedAcquisitor.__call__", "len(gotWf)", len(gotWf))
            res[i] = ch.decode_waveform(gotWf, self.preamble)
            print("WaveformSynchronisedAcquisitor.__call__", "len(res[" + repr(i) + "])", len(res[i]))
        
        return np.array(res)



class AxisParams():
    __slots__ = ("increment", "origin", "reference")
    def __init__(self, increment, origin, reference):
        self.increment = float(increment)
        self.origin = float(origin)
        self.reference = float(reference)
    
    def decode(self, val):
        return (val - self.reference - self.origin) * self.increment

    def __repr__(self):
        return self.__class__.__name__ + "(" + ", ".join(k + "=" + repr(getattr(self, k)) for k in __class__.__slots__) + ")"


class Preamble():
    __slots__ = ("format", "type", "points", "averages", "x", "y")
    def __init__(self, format, type, points, averages, x_increment, x_origin, x_reference, y_increment, y_origin, y_reference):
        self.format = WaveformFormat(int(format))
        self.type = AcquisitionType(int(type))
        self.points = int(float(points))
        self.averages = int(float(averages))
        self.x = AxisParams(x_increment, x_origin, x_reference)
        self.y = AxisParams(y_increment, y_origin, y_reference)

    def __repr__(self):
        return self.__class__.__name__ + "<" + ", ".join(k + "=" + repr(getattr(self, k)) for k in __class__.__slots__) + ">"
