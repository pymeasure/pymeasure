import numpy as np
from . import RigolChannel

class TimeChannel(RigolChannel):
    __slots__ = ()
    def __init__(self, hal, id):
        super().__init__(hal, id)
        self.innerId = "TIMebase:MAIN"
    
    @property
    def unit(self):
        return "s"
    
    def decode_waveform(self, waveform, preamble):
        return self.hal.decodeWaveformFormula(waveform, preamble.x)
    
    def get_waveform(self, totalPoints, dType, points_in_batch:int):
        print("TimeChannel.get_waveform", "totalPoints", totalPoints, "dType", dType)
        return np.arange(totalPoints)
    
    @property
    def supported_memory_sizes(self):
        return None
    
    @property
    def sample_rate(self):
        return 1.
    
    def set_samples_per_channel_sample(self, chn, v):
        chn.sample_rate = self.sample_rate / v
    
    def get_points_in_a_batch(self, waveform_mode, acquisition_type, channels):
        return None

    @property
    def total_points(self):
        return None
