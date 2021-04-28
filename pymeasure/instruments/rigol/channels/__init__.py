from ...oscilloscope import ChannelHAL, IChannel

class RigolChannelHAL(ChannelHAL):
    def get_offset(self, channelId):
        return float(self.hal.inst.query(':'+ str(channelId) + ':OFFS?'.format()))

    def set_offset(self, channelId, offset):
        self.hal.write(':'+ str(channelId) + ":OFFS "+ offset)

    def get_scale(self, channelId):
        return float(self.hal.inst.query(":" + str(channelId) + ":SCALe?"))

    def set_scale(self, channelId, scale):
        self.hal.inst.write(":" + str(channelId) + ":SCAL " + str(scale))
    
    def get_visibility(self, channelId):
        return self.hal.inst.query(":" + str(channelId) + ":DISP?").lower() in {"on", "1"}

    def set_visibility(self, channelId, vis):
        self.hal.inst.write(":" + str(channelId) + ":DISP " + str(int(vis)))
    
    def get_unit(self, channelId):
        return self.hal.inst.query(":" + str(channelId) + ":UNIT?")

    def set_unit(self, channelId, unit):
        self.hal.inst.write(":" + str(channelId) + ":UNIT " + str(unit))

    def decodeWaveformFormula(self, val, axisParam):
        return axisParam.decode(val)
    
    def get_points_in_a_batch(self, channel, waveform_mode, acquisition_type, channels):
        raise NotImplementedError()


class RigolChannel(IChannel):
    __slots__ = ("innerId", )
    HAL_CLASS = RigolChannelHAL
    def __init__(self, hal, id):
        super().__init__(hal, id)
        self.innerId = self.id
    
    @property
    def scale(self):
        return self.hal.get_scale(self.innerId)
    
    @scale.setter
    def scale(self, v):
        self.hal.set_scale(self.innerId, v)

    @property
    def offset(self):
        return self.hal.get_offset(self.innerId)
    
    @offset.setter
    def offset(self, v):
        self.hal.set_offset(self.innerId, v)

    @property
    def sample_rate(self):
        raise NotImplementedError()
    
    @sample_rate.setter
    def sample_rate(self, v):
        raise NotImplementedError()

    @property
    def supported_memory_sizes(self):
        """None means that supports any"""
        raise NotImplementedError()

    @property
    def inverted(self):
        return self.hal.get_is_inverted(self.innerId)
    
    @inverted.setter
    def inverted(self, v):
        self.hal.set_is_inverted(self.innerId, v)
    
    @property
    def bandwidth_limit(self):
        return self.bandwidth_limit_frequency if get_is_band_width_limited_20mhz(self.innerId) else float("inf")
    
    @inverted.setter
    def bandwidth_limit(self, v):
        if v == float("inf"):
            set_is_band_width_limited(self.innerId, False)
        elif v == self.bandwidth_limit_frequency:
            set_is_band_width_limited(self.innerId, True)
        else:
            raise ValueError("Only inf or " + str(self.bandwidth_limit_frequency) + " Hz are supported for this oscilloscope")
    
    def get_supported_memory_sizes(self, channelId):
        return self.hal.get_supported_memory_sizes()

    def get_samples_per_channel_sample(self, chn):
        return self.sample_rate / chn.sample_rate
    
    def set_samples_per_channel_sample(self, chn, v):
        self.sample_rate = v * chn.sample_rate
