import typing

from ..acquisitor import *
from ...oscilloscope import OscilloscopeHAL
from ..channels import RigolChannel
from ..channels.acquisition import RigolAcquisitionChannel
from ..channels.time import TimeChannel

class RigolHAL(OscilloscopeHAL):
    __slots__ = ()
    ACQUISITION_CHANNEL_CLASS = RigolAcquisitionChannel
    TIME_CHANNEL_CLASS = TimeChannel
    MATH_CHANNEL_CLASS = RigolChannel
    
    def __init__(self, inst):
        super().__init__(inst, WaveformSynchronisedAcquisitor)

    def opc_wait(self) -> int:
        return int(self.inst.query("*OPC?"))

    @property
    def mode(self) -> DeviceMode:
        return self.status
    
    @mode.setter
    def mode(self, v:DeviceMode):
        v = DeviceMode(v)
        self.inst.write(":" + v.value)
    
    def trigger(self) -> None:
        print(":TFORce")
        self.mode = DeviceMode.single
        self.inst.write(":TFOR")

    def getChannelsList(self) -> typing.Iterable[RigolChannel]:
        remap = {}
        for i in range(1, self.getChannelsCount()+1):
            remap[i] = self.__class__.ACQUISITION_CHANNEL_CLASS(self, "CHAN" + str(i))
        res = [self.__class__.TIME_CHANNEL_CLASS(self, "T")]
        res.extend(remap.values())
        res.append(self.__class__.MATH_CHANNEL_CLASS(self, "MATH"))
        for c in res:
            remap[c.id] = c
        return tuple(res), remap
    
    def get_display_picture(self, format):
        return self.inst.values(":DISP:DATA? " + str(format))
    
    @property
    def total_points(self) -> int:
        return int(float(self.inst.query(":ACQ:MDEP?")))

    @total_points.setter
    def total_points(self, v: int):
        return self.inst.write(":ACQ:MDEP " + str(v))
    
    @property
    def status(self) -> DeviceMode:
        res = self.inst.query(':TRIG:STAT?').strip()
        try:
            return DeviceMode(int(res))
        except ValueError:
            return DeviceMode[res]

    @property
    def waveform_mode(self) -> WaveformMode:
        return WaveformMode[self.inst.query(':WAV:MODE?').strip().lower()]

    @waveform_mode.setter
    def waveform_mode(self, mode=WaveformMode.NORMal):
        """ Changing the waveform mode """
        mode = WaveformMode(mode)
        self.inst.write('WAV:MODE ' + str(mode.value))
    
    @property
    def sample_rate(self):
        return float(self.inst.sample_rate)
    
    @property
    def source(self):
        self.inst.query(":WAV:SOUR?")
    
    @source.setter
    def source(self, chan):
        self.inst.write(":WAV:SOUR " + chan)
    
    @property
    def format(self) -> WaveformFormat:
        res = self.inst.query(":WAV:FORM?").strip().lower()
        return WaveformFormat[res]
    
    @format.setter
    def format(self, v: WaveformFormat):
        print("set format", v)
        self.inst.write(":WAV:FORM " + v.name)
    
    def get_supported_waveform_formats(self) -> typing.Iterable[WaveformFormat]:
        yield from WaveformFormat
    
    def getSupportedTriggerModes(self):
        return TriggerMode
    
    def getSupportedTriggerSweepModes(self):
        return SweepMode
    
    @property
    def trigger_mode(self) -> TriggerMode:
        r = self.inst.query(":TRIG:MODE?").strip()
        r = TriggerMode(r)
        return r
    
    @trigger_mode.setter
    def trigger_mode(self, v: TriggerMode):
        v = TriggerMode(v)
        self.inst.write(":TRIG:MODE " + v.value)

    @property
    def trigger_sweep_mode(self) -> SweepMode:
        return self.inst.query(":TRIG:SWE?")
    
    @trigger_sweep_mode.setter
    def trigger_sweep_mode(self, v: SweepMode):
        v = SweepMode(v)
        self.inst.write(":TRIG:SWE " + v.value)

    @property
    def waveform_preamble(self) -> Preamble:
        return Preamble(*self.inst.query(":WAV:PRE?").split(','))
    
    @property
    def waveform_parameter(self):
        """
        A completely undocumented struct presumably containing essential information needed to acquire the signal.
        The model it is used in has no SCPI events (if one tries to use them the model hangs, so are the software (because VISA drivers for Windows are shit), the only way to unhang is to detach USB and then RESTART THE DEVICE).
        If one reads the signal immediately after the trigger, the result is truncated.
        So I guess the command must contain the time PC must wait for.
        So we need to figure out the format of this blob.

        https://www.manualslib.com/manual/1368673/Rigol-Ds1204b.html?page=94#manual
        What is DSO_WAVE_PARAMETER? Google doesn't find it anywhere in The Net.
        
        """
        res = self.inst.binary_values(":WAV:PARAMETER?", dtype=np.uint8)
        #800000xxx
        header = bytes(res[:10])
        print("waveform_parameter header", header)
        res = res[10:]
        return res
    
    def get_points_in_a_batch(self, channels) -> int:
        raise NotImplementedError()
    
    def device_maximum_points_count(self) -> int:
        return int(float(self.inst.query(":WAVeform:SYSMemsize?").strip()))
    
    def get_supported_memory_sizes(self) -> int:
        return {self.device_maximum_points_count()}

    @property
    def acquisition_type(self) -> AcquisitionType:
        res = self.inst.query(":ACQ:TYPE?")
        try:
            res = AcquisitionType(int(res))
        except:
            res = AcquisitionType[res.strip().lower()]
        return res
    
    @acquisition_type.setter
    def acquisition_type(self, tp: AcquisitionType):
        tp = AcquisitionType(tp)
        self.inst.write(":ACQ:TYPE " + str(tp.name))

    @property
    def acquisition_mode(self) -> AcquisitionMode:
        res = self.inst.query(":ACQ:MODE?").strip()
        return AcquisitionMode[res.lower()]
    
    @acquisition_mode.setter
    def acquisition_mode(self, md: AcquisitionMode):
        md = AcquisitionMode(md)
        self.inst.write(":ACQ:MODE " + str(md.value))

    def get_waveform(self, *args, dType) -> np.ndarray:
        q = [":WAV:DATA?"]
        q.extend(args)
        if dType != WaveformFormat.ascii:
            return self.inst.binary_values(" ".join(q), header_bytes="ieee", dtype=waveformFormatMapping[dType.value])
        else:
            return self.inst.values(" ".join(q))
    
    def getChannelsCount(self) -> int:
        raise NotImplementedError()

    def wait_acquisition(self) -> None:
        self.inst.assert_trigger()
        self.inst.wait_on_event()
    
    @property
    def locked(self) -> bool:
        return self.inst.query(":SYST:LOCK?").lower() in {"on", "1"}

    @locked.setter
    def locked(self, v: bool):
        self.inst.write(":SYST:LOCK " + str(int(v)))
    