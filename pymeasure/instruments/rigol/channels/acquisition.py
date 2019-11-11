import warnings

from ...oscilloscope import AcquisitionChannelMixin
from . import RigolChannelHAL, RigolChannel
from .. import acquisitor
from ..acquisitor import *

class RigolAcqChannelHAL(RigolChannelHAL):
    def get_channel_visibility(self, channelId):
        return int(self.hal.inst.query(":" + str(channelId) + ":DISP?"))

    def set_channel_visibility(self, channelId, v):
        return self.hal.inst.write(":" + str(channelId) + ":DISP", int(v))

    def get_sample_rate(self, channelId):
        return float(self.hal.inst.query(":ACQ:SRAT? " + str(channelId)))
    
    def set_sample_rate(self, channelId, v):
        return float(self.hal.inst.query(":ACQ:SRAT " + str(channelId) + " " + str(v)))
    
    def get_coupling(self, channelId):
        res = self.hal.inst.query(":" + str(channelId) + ":COUP?")
        return Coupling[res]

    def set_coupling(self, channelId, coupling):
        self.hal.inst.write(":" + str(channelId) + ":COUP " + coupling.value)

    def get_waveform_(self, type):
        return self.hal.get_waveform(dType=type)

    def get_total_points(self, channelId):
        return int(float(self.hal.inst.query(":" + str(channelId) + ":MEMD?")))
    
    def set_total_points(self, channelId, v):
        self.hal.inst.write(":" + str(channelId) + ":MEMD" + str(v))

    def get_is_inverted(self, channelId):
        return bool(int(self.hal.inst.query(":" + str(channelId) + ":INV?")))
    
    def set_is_inverted(self, channelId, v):
        self.hal.inst.write(":" + str(channelId) + ":INV " + str(int(v)))

    def get_is_band_width_limited_20mhz(self, channelId):
        return float(self.hal.inst.query(":" + str(channelId) + ":BWL?"))
    
    def set_is_band_width_limited(self, channelId, v):
        self.hal.inst.write(":" + str(channelId) + ":BWL " + str(v))
    
    def get_supported_memory_sizes(self, channelId):
        return self.hal.get_supported_memory_sizes()
    
    def get_supported_waveform_formats(self, channelId):
        return self.hal.get_supported_memory_sizes()
    
    def get_bandwidth_limit_frequency(self):
        return 20e6
    
    def get_screen_data(self, channelId, dType):
        cmd = ':WAV:SCREENDATA? ' + str(channelId)
        if dType != WaveformFormat.ascii:
            return self.hal.inst.binary_values(cmd, header_bytes="ieee", dtype=waveformFormatMapping[dType.value])
        else:
            return self.hal.inst.values(cmd)

    def get_memory_data(self, channelId, dType):
        cmd = ':WAV:MEM? ' + str(channelId)
        if dType != WaveformFormat.ascii:
            return self.hal.inst.binary_values(cmd, header_bytes="ieee", dtype=waveformFormatMapping[dType.value])
        else:
            return self.hal.inst.values(cmd)

    def get_waveform(self, preamble:Preamble, points_in_batch:int):
        raise NotImplementedError()


class RigolAcqChannelHALMultipleCommands(RigolAcqChannelHAL):
    def get_waveform(self, innerId, totalPoints, dType, points_in_batch:int):
        self.hal.source = innerId
        batches = totalPoints // points_in_batch
        print("RigolAcqChannelHALMultipleCommands.get_waveform", "preamble.points", totalPoints, "points_in_batch", points_in_batch, "batches", batches)
        if not batches:
            warnings.warn("No full batches! WTF?")
        
        for i in range(batches):
            self.wfStart = i * points_in_batch
            self.wfStop = (i+1) * points_in_batch
            wf = self.get_waveform()
        
        self.wfStart = batches * points_in_batch
        self.wfStop = batches * points_in_batch + totalPoints % points_in_batch
        wf = self.get_waveform_(dType)
        return wf
    
    @property
    def wfStart(self):
        return int(self.hal.inst.query(":WAV:STAR?"))
    
    @wfStart.setter
    def wfStart(self, pos):
        self.hal.inst.write(":WAV:STAR " + str(pos))

    @property
    def wfStop(self):
        return int(self.hal.inst.query(":WAV:STOP?"))
    
    @wfStop.setter
    def wfStop(self, pos):
        self.hal.inst.write(":WAV:STOP " + str(pos))


class RigolAcqChannelHALSingleCommand(RigolAcqChannelHAL):
    def get_waveform(self, innerId, totalPoints, dType, points_in_batch:int):
        res = self.get_memory_data(innerId, dType)
        print("RigolAcqChannelHALSingleCommand.get_waveform", res, len(res))
        return res
    #total_points


class RigolAcquisitionChannel(RigolChannel, AcquisitionChannelMixin):
    __slots__ = ("bandwidth_limit_frequency",)
    HAL_CLASS = None
    
    def __init__(self, hal, id):
        super().__init__(hal, id)
        self.bandwidth_limit_frequency = self.hal.get_bandwidth_limit_frequency()

    def select(self):
        self.hal.hal.source = self.id
    
    @property
    def supported_memory_sizes(self):
        return self.hal.get_supported_memory_sizes(self.innerId)
    
    def decode_waveform(self, waveform, preamble):
        return self.hal.decodeWaveformFormula(waveform, preamble.y)
    
    def get_waveform(self, totalPoints, dType, points_in_batch:int):
        res = self.hal.get_waveform(self.innerId, totalPoints, dType, points_in_batch)
        return res

    @property
    def visible(self):
        return self.hal.get_visibility(self.innerId)

    @visible.setter
    def visible(self, v):
        return self.hal.set_visibility(self.innerId, v)

    @property
    def total_points(self):
        return self.hal.get_total_points(self.innerId)

    @total_points.setter
    def total_points(self, v):
        self.hal.set_total_points(self.innerId, v)

    @property
    def sample_rate(self):
        return self.hal.get_sample_rate(self.innerId)
    
    @sample_rate.setter
    def sample_rate(self, v):
        return self.hal.set_sample_rate(self.innerId, v)
    
    
    def get_points_in_a_batch(self, waveform_mode, acquisition_type, channels):
        return self.hal.get_points_in_a_batch(self, waveform_mode, acquisition_type, channels)
    
    @property
    def unit(self):
        return "V"


acquisitor.RigolAcquisitionChannel = RigolAcquisitionChannel
