from .generic import RigolHAL
from ..enums import *
from ..channels.acquisition import RigolAcquisitionChannel, RigolAcqChannelHALSingleCommand

class DS1204AcqChannelHAL(RigolAcqChannelHALSingleCommand):
    __slots__ = ()
    
    def get_total_points(self, channelId):
        return int(float(self.hal.inst.query(":WAV:WINM? "+ str(channelId))))
    
    def set_total_points(self, channelId, v):
        raise NotImplementedError()
    
    def get_points_in_a_batch(self, channel, waveform_mode, acquisition_type, channels):
        print("DS1204AcqChannelHAL.get_points_in_a_batch", channel.innerId, waveform_mode, acquisition_type, "isinstance(channel, RigolAcquisitionChannel)", isinstance(channel, RigolAcquisitionChannel), " len(channels)", len(channels))
        if channel.innerId == "FFT":
            return 500
        
        if waveform_mode == WaveformMode.normal:
            if acquisition_type == AcquisitionType.peakDetect:
                return 1200
            elif acquisition_type == AcquisitionType.normal or acquisition_type == AcquisitionType.average:
                return 600
        elif waveform_mode == WaveformMode.raw:
            if channel.innerId == "MATH":
                return 600
            elif isinstance(channel, RigolAcquisitionChannel):
                if len(channels) == 1:
                    return 16384
                else:
                    return 8192
        elif waveform_mode == WaveformMode.max:
            return max(
                self.get_points_in_a_batch(WaveformMode.normal, acquisition_type, channel_type, channels),
                self.get_points_in_a_batch(WaveformMode.raw, acquisition_type, channel_type, channels)
            )

class DS1204BAcquisitionChannel(RigolAcquisitionChannel):
    __slots__ = ()
    HAL_CLASS = DS1204AcqChannelHAL

class DS1204BHAL(RigolHAL):
    __slots__ = ("_waveform_mode",)
    ACQUISITION_CHANNEL_CLASS = DS1204BAcquisitionChannel
    
    
    def __init__(self, inst):
        super().__init__(inst)
        self.waveform_mode = WaveformMode.RAW
    
    def getChannelsCount(self):
        return 4
    
    
    def beep():
        self.inst.inst.write(":BEEP:ACTion")

    @property
    def waveform_mode(self):
        return WaveformMode[self.inst.query(':WAV:POIN:MODE?').strip().lower()]

    @waveform_mode.setter
    def waveform_mode(self, mode=WaveformMode.NORMal):
        """ Changing the waveform mode """
        mode = WaveformMode(mode)
        self.inst.write(':WAV:POIN:MODE ' + str(mode.name))

    @property
    def total_points(self):
        #raise NotImplementedError("Use RigolAcqChannelHALSingleCommand.get_total_points")
        return super().device_maximum_points_count()

    @total_points.setter
    def total_points(self, v):
        raise NotImplementedError()
        #raise NotImplementedError("Use RigolAcqChannelHALSingleCommand.get_total_points")

    @property
    def trigger_sweep_mode(self):
        return SweepMode(self.inst.query(":TRIG:" + self.trigger_mode.value + ":SWE?"))
    
    @trigger_sweep_mode.setter
    def trigger_sweep_mode(self, v):
        v = SweepMode(v)
        self.inst.write(":TRIG:" + self.trigger_mode.value + ":SWE " + v.value)

    @property
    def locked(self):
        warnings.warn("You cannot retrieve locked state for this model because queriing this command causes lock.")
        return None
    
    @locked.setter
    def locked(self, v):
        self.inst.write(":SYST:LOCK " + "ENAB" if v else "DIS")
        self.inst.write(":KEY:LOCK " + "ENAB" if v else "DIS")
    
    def get_display_picture(self, format):
        return self.inst.query_raw(":DISP:DATA?")
    
    def wait_acquisition(self):
        return self.opc_wait()
        status = DeviceMode.run
        while(status == DeviceMode.run):
            #self.inst.opc()
            status = self.status
            print("wait_acquisition status", status)
            print("self.inst.complete", self.inst.complete)
    
    @property
    def acquisition_points_count(self):
        return int(float(self.inst.query(":WAV:POIN?").strip()))
    
    @acquisition_points_count.setter
    def acquisition_points_count(self, v):
        return self.inst.write(":WAV:POIN " + str(v))
    
    def get_points_in_a_batch(self, channels):
        res = super().get_points_in_a_batch(channels)
        print("get_points_in_a_batch super().get_points_in_a_batch res", res)
        self.acquisition_points_count = res
        print("get_points_in_a_batch self.acquisition_points_count", self.acquisition_points_count)
        return res
    
    # Todo: undocumented functionality
    # self.inst.write(":TIMEBASE:FORMAT? "+"X-Y")
    # :WAV:DATA? XY
    # https://www.manualslib.com/manual/1368673/Rigol-Ds1204b.html?page=95#manual