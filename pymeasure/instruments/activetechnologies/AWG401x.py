#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""This module implements an interface for Active Technologies AWG-401x, both
for the Arbitrary Waveform Generator (AWG) mode and the Arbitrary Function
Generator (AFG) mode. The module has been developed from the official
documentation available on https://www.activetechnologies.it"""

from collections import abc, namedtuple

import pprint

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_set, \
    strict_range


class ChannelBase(Channel):
    """Implementation of a base Active Technologies AWG-4000 channel."""

    def __init__(self, instrument, id):
        super().__init__(instrument, id)

        self.delay_values = [self.delay_min, self.delay_max]

    enabled = Instrument.control(
        "OUTPut{ch}:STATe?", "OUTPut{ch}:STATe %d",
        """A boolean property that enables or disables the output for the
        specified channel.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    polarity = Instrument.control(
        "OUTPut{ch}:POLarity?", "OUTPut{ch}:POLarity %s",
        """This property inverts the output waveform relative to its average
        value: (High Level – Low Level)/2. NORM for normal, INV for inverted
        """,
        validator=strict_discrete_set,
        values=["NORMAL", "NORM", "INVERTED", "INV"],
        get_process=lambda v: "NORM" if v == 0 else ("INV" if v == 1 else v)
    )

    delay = Instrument.control(
        None, None,
        """This property sets or queries the initial delay, set 0 for disable
        it. When you send this command in AFG mode, if the instrument is
        running, it will be stopped.""",
        dynamic=True
    )

    delay_max = Instrument.measurement(
        None,
        """This property queries the maximum delay that can be set to the
        output waveform.""",
        dynamic=True
    )

    delay_min = Instrument.measurement(
        None,
        """This property queries the minimum delay that can be set to the
        output waveform.""",
        dynamic=True
    )


class ChannelAFG(ChannelBase):
    """Implementation of a Active Technologies AWG-4000 channel in AFG mode."""

    def __init__(self, instrument, id):
        super().__init__(instrument, id)

        self.calculate_voltage_range()
        self.frequency_values = [self.frequency_min, self.frequency_max]

        self.phase_values = [self.phase_min, self.phase_max]

    load_impedance = Instrument.control(
        "OUTPut{ch}:IMPedance?", "OUTPut{ch}:IMPedance %d",
        """This property sets the output load impedance for the specified
        channel. The specified value is used for amplitude, offset, and
        high/low level settings. You can set the impedance to any value from
        1 Ω to 1 MΩ. The default value is 50 Ω.""",
        validator=strict_range,
        values=[1, 1000000]
    )

    output_impedance = Instrument.control(
        "OUTPut{ch}:LOW:IMPedance?", "OUTPut{ch}:LOW:IMPedance %d",
        """This property sets the instrument output impedance, the possible
        values are: 5 Ohm or 50 Ohm (default).""",
        validator=strict_discrete_set,
        values={5: 1, 50: 0},
        map_values=True
    )

    shape = Instrument.control(
        "SOURce{ch}:FUNCtion:SHAPe?", "SOURce{ch}:FUNCtion:SHAPe %s",
        """This property sets or queries the shape of the carrier waveform.
        Allowed choices depends on the choosen modality, please refer on
        instrument manual. When you set this property with a different value,
        if the instrument is running it will be stopped.
        Can be set to: SIN<USOID>, SQU<ARE>, PULS<E>, RAMP, PRN<OISE>, DC,
        SINC, GAUS<SIAN>, LOR<ENTZ>, ERIS<E>, EDEC<AY>, HAV<ERSINE>, ARBB,
        EFIL<E>, DOUBLEPUL<SE>""",
        validator=strict_discrete_set,
        values=["SINUSOID", "SIN", "SQUARE", "SQU", "PULSE", "PULS", "RAMP",
                "PRNOISE", "PRN", "DC", "SINC", "GAUSSIAN", "GAUS", "LORENTZ",
                "LOR", "ERISE", "ERIS", "EDECAY", "EDEC", "HAVERSINE", "HAV",
                "ARBB", "EFILE", "EFIL", "DOUBLEPULSE", "DOUBLEPUL"]
    )

    # Default delay override
    delay_get_command = "SOURce{ch}:INITDELay?"
    delay_set_command = "SOURce{ch}:INITDELay %s"
    delay_max_get_command = "SOURce{ch}:INITDELay? MAXimum"
    delay_min_get_command = "SOURce{ch}:INITDELay? MINimum"

    frequency = Instrument.control(
        "SOURce{ch}:FREQuency?", "SOURce{ch}:FREQuency %s",
        """This property sets or queries the frequency of the output waveform.
        This command is available when the Run Mode is set to any setting other
        than Sweep. The output frequency range setting depends on the type of
        output waveform. If you change the type of output waveform, it may
        change the output frequency because changing waveform types affects the
        setting range of the output frequency. The output frequency range
        setting depends also on the amplitude parameter.""",
        validator=strict_range,
        dynamic=True
    )

    frequency_max = Instrument.measurement(
        "SOURce{ch}:FREQuency? MAXimum",
        """This property queries the maximum frequency that can be set to the
        output waveform."""
    )

    frequency_min = Instrument.measurement(
        "SOURce{ch}:FREQuency? MINimum",
        """This property queries the minimum frequency that can be set to the
        output waveform."""
    )

    phase = Instrument.control(
        "SOURce{ch}:PHASe:ADJust?", "SOURce{ch}:PHASe:ADJust %s",
        """This property sets or queries the phase of the output waveform for
        the specified channel. The value is in degrees.""",
        validator=strict_range,
        dynamic=True
    )

    phase_max = Instrument.measurement(
        "SOURce{ch}:PHASe:ADJust? MAXimum",
        """This property queries the maximum phase that can be set to the
        output waveform."""
    )

    phase_min = Instrument.measurement(
        "SOURce{ch}:PHASe:ADJust? MINimum",
        """This property queries the minimum phase that can be set to the
        output waveform."""
    )

    voltage_unit = Instrument.control(
        "OUTPut{ch}:VOLTage:UNIT?", "OUTPut{ch}:VOLTage:UNIT %s",
        """This property sets or queries the units of output amplitude, the
        possible choices are: VPP, VRMS, DBM. This command does not affect the
        offset, high level, or low level of output.""",
        validator=strict_discrete_set,
        values=["VPP", "VRMS", "DBM"]
    )

    voltage_low = Instrument.control(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:LOW?",
        "SOURce{ch}:VOLTage:LEVel:IMMediate:LOW %s",
        """This property sets or queries the low level of the waveform. The
        low level could be limited by noise level to not exceed the maximum
        amplitude. If the carrier is Noise or DC level, this command and this
        query cause an error.""",
        validator=strict_range,
        dynamic=True
    )

    voltage_low_max = Instrument.measurement(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:LOW? MAXimum",
        """This property queries the maximum low voltage level that can be set
        to the output waveform."""
    )

    voltage_low_min = Instrument.measurement(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:LOW? MINimum",
        """This property queries the minimum low voltage level that can be set
        to the output waveform."""
    )

    voltage_high = Instrument.control(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:HIGH?",
        "SOURce{ch}:VOLTage:LEVel:IMMediate:HIGH %s",
        """This property sets or queries the high level of the waveform. The
        high level could be limited by noise level to not exceed the maximum
        amplitude. If the carrier is Noise or DC level, this command and this
        query cause an error.""",
        validator=strict_range,
        dynamic=True
    )

    voltage_high_max = Instrument.measurement(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:HIGH? MAXimum",
        """This property queries the maximum high voltage level that can be set
        to the output waveform."""
    )

    voltage_high_min = Instrument.measurement(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:HIGH? MINimum",
        """This property queries the minimum high voltage level that can be set
        to the output waveform."""
    )

    voltage_amplitude = Instrument.control(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:AMPLitude?",
        "SOURce{ch}:VOLTage:LEVel:IMMediate:AMPLitude %s",
        """This property sets or queries the output amplitude for the specified
        channel. The measurement unit of amplitude depends on the selection
        operated using the voltage_unit property. If the carrier is Noise the
        amplitude is Vpk instead of Vpp. If the carrier is DC level this
        command causes an error. The range of the amplitude setting could be
        limited by the frequency and offset parameter of the carrier waveform.
        """,
        validator=strict_range,
        dynamic=True
    )

    voltage_amplitude_max = Instrument.measurement(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:AMPLitude? MAXimum",
        """This property queries the maximum amplitude voltage level that can
        be set to the output waveform.""",
        get_process=lambda value: float(value.replace("VPP", ""))
    )

    voltage_amplitude_min = Instrument.measurement(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:AMPLitude? MINimum",
        """This property queries the minimum amplitude voltage level that can
        be set to the output waveform.""",
        get_process=lambda value: float(value.replace("VPP", ""))
    )

    voltage_offset = Instrument.control(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:OFFSet?",
        "SOURce{ch}:VOLTage:LEVel:IMMediate:OFFSet %s",
        """This property sets or queries the offset level for the specified
        channel. The offset range setting depends on the amplitude parameter.
        """,
        validator=strict_range,
        dynamic=True
    )

    voltage_offset_max = Instrument.measurement(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:OFFSet? MAXimum",
        """This property queries the maximum offset voltage level that can be
        set to the output waveform."""
    )

    voltage_offset_min = Instrument.measurement(
        "SOURce{ch}:VOLTage:LEVel:IMMediate:OFFSet? MINimum",
        """This property queries the minimum offset voltage level that can be
        set to the output waveform."""
    )

    baseline_offset = Instrument.control(
        "SOURce{ch}:VOLTage:BASELINE:OFFSET?",
        "SOURce{ch}:VOLTage:BASELINE:OFFSET %s",
        """This property sets or queries the offset level for the specified
        channel. The offset range setting depends on the amplitude parameter.
        """,
        validator=strict_range,
        dynamic=True
    )

    baseline_offset_max = Instrument.measurement(
        "SOURce{ch}:VOLTage:BASELINE:OFFSET? MAXimum",
        """This property queries the maximum offset voltage level that can be
        set to the output waveform."""
    )

    baseline_offset_min = Instrument.measurement(
        "SOURce{ch}:VOLTage:BASELINE:OFFSET? MINimum",
        """This property queries the minimum offset voltage level that can be
        set to the output waveform."""
    )

    def calculate_voltage_range(self):
        self.voltage_low_values = [self.voltage_low_min, self.voltage_low_max]

        self.voltage_high_values = [self.voltage_high_min,
                                    self.voltage_high_max]

        self.voltage_amplitude_values = [self.voltage_amplitude_min,
                                         self.voltage_amplitude_max]

        self.voltage_offset_values = [self.voltage_offset_min,
                                      self.voltage_offset_max]

        self.baseline_offset_values = [self.baseline_offset_min,
                                       self.baseline_offset_max]


class ChannelAWG(ChannelBase):
    """Implementation of a Active Technologies AWG-4000 channel in AWG mode."""

    # Default delay override
    delay_get_command = "OUTPut{ch}:DELay?"
    delay_set_command = "OUTPut{ch}:DELay %s"
    delay_max_get_command = "OUTPut{ch}:DELay? MAXimum"
    delay_min_get_command = "OUTPut{ch}:DELay? MINimum"

    scale = Instrument.control(
        "OUTPut{ch}:SCALe?",
        "OUTPut{ch}:SCALe %f",
        """This property sets or returns the Amplitude Scale parameter of the
        analog channel “n”. This property can be modified at run-time to adjust
        the waveform amplitude while the instrument is running and it is
        applied to all the waveforms contained in the sequencer. It is
        expressed in % and it has a range of 0% to 100%. 100% means that the
        waveform keeps its original amplitude.""",
        validator=strict_range,
        values=[0, 100]
    )


class AWG401x_base(Instrument):
    """AWG-401x base class"""

    def __init__(self, adapter,
                 name="Active Technologies AWG-4014 1.2GS/s Arbitrary Waveform Generator",
                 **kwargs):

        # Insert an higher timeout because, often, when starting the
        # instrument, can pass some time and the adapted goes in timeout
        kwargs.setdefault('timeout', 7500)

        super().__init__(
            adapter,
            name,
            **kwargs
        )

    def beep(self):
        """Causes a system beep."""
        self.write("SYST:BEEP")

    def save(self, position):
        """Save the actual configuration in memory.

        :param int position: Instrument save position [0,4]

        :raises ValueError: If position is outside permitted limit [0,4].
        """

        if position >= 0 or position <= 4:
            self.write(f"*SAV {position}")
        else:
            raise ValueError("position value outside permitted range [0,4]")

    def load(self, position):
        """Load the actual configuration in memory.

        :param int position: Instrument load position [0,4]

        :raises ValueError: If position is outside permitted limit [0,4].
        """

        if position >= 0 or position <= 4:
            self.write(f"*RCL {position}")
        else:
            raise ValueError("position value outside permitted range [0,4]")

    def wait_last(self):
        """Wait for last operation completition"""

        self.write("*WAI")


class AWG401x_AFG(AWG401x_base):
    """Represents the Active Technologies AWG-401x Arbitrary Waveform Generator
    in AFG mode.

    .. code-block:: python

        wfg = AWG401x_AFG("TCPIP::192.168.0.123::INSTR")

        wfg.reset()                     # Reset the instrument at default state

        wfg.ch[1].shape = "SINUSOID"    # Sets a sine waveform on CH1
        wfg.ch[1].frequency = 4.7e3     # Sets the frequency to 4.7 kHz on CH1
        wfg.ch[1].amplitude = 1         # Set amplitude of 1 V on CH1
        wfg.ch[1].offset = 0            # Set the amplitude to 0 V on CH1
        wfg.ch[1].enabled = True        # Enables the CH1

        wfg.ch[2].shape = "SQUARE"      # Sets a square waveform on CH2
        wfg.ch[2].frequency = 100e6     # Sets the frequency to 100 MHz on CH2
        wfg.ch[2].amplitude = 0.5         # Set amplitude of 0.5 V on CH2
        wfg.ch[2].offset = 0            # Set the amplitude to 0 V on CH2
        wfg.ch[2].enabled = True        # Enables the CH2

        wfg.enabled = True              # Enable output of waveform generator
        wfg.beep()                      # "beep"

        print(wfg.check_errors())       # Get the error queue

    """
    ch_1 = Instrument.ChannelCreator(ChannelAFG, 1)
    ch_2 = Instrument.ChannelCreator(ChannelAFG, 2)

    enabled = Instrument.control(
        "AFGControl:STATus?", "AFGControl:%s",
        """A boolean property that enables the generation of signals.""",
        validator=strict_discrete_set,
        values={True: "START", False: "STOP"},
        map_values=True,
        get_process=lambda v: "START" if v == 1 else ("STOP" if v == 0 else v)
    )

    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, **kwargs)

        model = self.id.split(",")[1]
        if model == "AWG4012":
            num_ch = 2
        elif model == "AWG4014":
            num_ch = 4
        elif model == "AWG4018":
            num_ch = 8
        else:
            raise NotImplementedError(f"Instrument {model} not implemented in"
                                      "class AWG401x")

        for i in range(3, num_ch + 1):
            child = self.add_child(ChannelAFG, i, collection="ch")
            child._protected = True


class AWG401x_AWG(AWG401x_base):
    """Represents the Active Technologies AWG-401x Arbitrary Waveform Generator
    in AWG mode.

    .. code-block:: python

        wfg = AWG401x_AWG("TCPIP::192.168.0.123::INSTR")

        wfg.reset()             # Reset the instrument at default state

        # Set a oscillating waveform
        wfg.waveforms["MyWaveform"] = [1, 0] * 8

        for i in range(1, wfg.num_ch + 1):
            wfg.entries[1].ch[i].voltage_high = 1       # Sets high voltage = 1
            wfg.entries[1].ch[i].voltage_low = 0        # Sets low voltage = 1
            wfg.entries[1].ch[i].waveform = "SQUARE"    # Sets a square wave
            wfg.setting_ch[i].enabled = True            # Enable channel

        wfg.entries.resize(2)           # Resize the number of entries to 2

        wfg.entries[2].ch[1].waveform = "MyWaveform"   # Set custom waveform

        wfg.enabled = True              # Enable output of waveform generator
        wfg.beep()                      # "beep"

        print(wfg.check_errors())       # Get the error queue

    """

    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, **kwargs)

        for i in range(1, self.num_ch + 1):
            self.add_child(ChannelAWG, i, collection="setting_ch")

        self.entries = self.DummyEntriesElements(self, self.num_ch)
        self.burst_count_values = [self.burst_count_min, self.burst_count_max]

        self.sampling_rate_values = [self.sampling_rate_min,
                                     self.sampling_rate_max]

        self._waveforms = self.WaveformsLazyDict(self)

    num_ch = Instrument.measurement(
        "AWGControl:CONFigure:CNUMber?",
        """This property queries the number of analog channels.""",
        cast=int
    )

    num_dch = Instrument.measurement(
        "AWGControl:CONFigure:DNUMber?",
        """This property queries the number of digital channels.""",
        cast=int
    )

    sample_decreasing_strategy = Instrument.control(
        "AWGControl:DECreasing?", "AWGControl:DECreasing %s",
        """This property sets or returns the Sample Decreasing Strategy. The
        “Sample decreasing strategy” parameter defines the strategy used to
        adapt the waveform length to the sequencer entry length in the case
        where the original waveform length is longer than the sequencer entry
        length. Can be set to: DECIM<ATION>, CUTT<AIL>, CUTH<EAD>""",
        validator=strict_discrete_set,
        values=["DECIMATION", "DECIM", "CUTTAIL", "CUTT", "CUTHEAD", "CUTH"]
    )

    sample_increasing_strategy = Instrument.control(
        "AWGControl:INCreasing?", "AWGControl:INCreasing %s",
        """This property sets or or returns the Sample Increasing Strategy. The
        “Sample increasing strategy” parameter defines the strategy used to
        adapt the waveform length to the sequencer entry length in the case
        where the original waveform length is shorter than the sequencer entry
        length. Can be set to: INTER<POLATION>, RETURN<ZERO>, HOLD<LAST>,
        SAMPLESM<ULTIPLICATION>""",
        validator=strict_discrete_set,
        values=["INTERPOLATION", "INTER", "RETURNZERO", "RETURN", "HOLDLAST",
                "HOLD", "SAMPLESMULTIPLICATION", "SAMPLESM"]
    )

    entry_level_strategy = Instrument.control(
        "AWGControl:LENGth:MODE?", "AWGControl:LENGth:MODE %s",
        """This property sets or or returns the Entry Length Strategy. This
        strategy manages the length of the sequencer entries in relationship
        with the length of the channel waveforms defined for each entry. The
        possible values are:

        * ADAPTL<ONGER>: the length of an entry of the sequencer by default
          will be equal to the length of the longer channel waveform, among all
          analog channels, assigned to the entry.
        * ADAPTS<HORTER>: the length of an entry of the sequencer by default
          will be equal to the length of the shorter channel waveform, among
          all analog channels, assigned to the entry.
        * DEF<AULT>:the length of an entry of the sequencer by default will be
          equal to the value specified in the Sequencer Item Default Length [N]
          parameter""",
        validator=strict_discrete_set,
        values=["ADAPTLONGER", "ADAPTL", "ADAPTSHORTER", "ADAPTS", "DEFAULT",
                "DEF"]
    )

    run_mode = Instrument.control(
        "AWGControl:RMODe?", "AWGControl:RMODe %s",
        """This property sets or returns the AWG run mode. The possible values
        are:

        * CONT<INUOUS>: each waveform will loop as written in the entry
          repetition parameter and the entire sequence is repeated circularly
        * BURS<T>: the AWG waits for a trigger event. When the trigger event
          occurs each waveform will loop as written in the entry repetition
          parameter and the entire sequence will be repeated circularly many
          times as written in the Burst Count[N] parameter. If you set Burst
          Count[N]=1 the instrument is in Single mode and the sequence will be
          repeated only once.
        * TCON<TINUOUS>: the AWG waits for a trigger event. When the trigger
          event occurs each waveform will loop as written in the entry
          repetition parameter and the entire sequence will be repeated
          circularly.
        * STEP<PED>: the AWG, for each entry, waits for a trigger event before
          the execution of the sequencer entry. The waveform of the entry will
          loop as written in the entry repetition parameter. After the
          generation of an entry has completed, the last sample of the current
          entry or the first sample of the next entry is held until the next
          trigger is received. At the end of the entire sequence the execution
          will restart from the first entry.
        * ADVA<NCED>: it enables the “Advanced” mode. In this mode the
          execution of the sequence can be changed by using conditional and
          unconditional jumps (JUMPTO and GOTO commands) and dynamic jumps
          (PATTERN JUMP commands).

        The \\*RST command sets this parameter to CONTinuous.""",
        validator=strict_discrete_set,
        values=["CONTINUOUS", "CONT", "BURST", "BURS", "TCONTINUOUS",
                "TCON", "STEPPED", "STEP", "ADVANCED", "ADVA"]
    )

    burst_count = Instrument.control(
        "AWGControl:BURST?",
        "AWGControl:BURST %d",
        """This property sets or queries the burst count parameter.""",
        validator=strict_range,
        dynamic=True
    )

    burst_count_max = Instrument.measurement(
        "AWGControl:BURST? MAXimum",
        """This property queries the maximum burst count parameter.""",
        cast=int
    )

    burst_count_min = Instrument.measurement(
        "AWGControl:BURST? MINimum",
        """This property queries the minimum burst count parameter.""",
        cast=int
    )

    sampling_rate = Instrument.control(
        "AWGControl:SRATe?",
        "AWGControl:SRATe %f",
        """This property sets or queries the sample rate for the Sampling
        Clock.""",
        validator=strict_range,
        dynamic=True
    )

    sampling_rate_max = Instrument.measurement(
        "AWGControl:SRATe? MAXimum",
        """This property queries the maximum sample rate for the Sampling
        Clock."""
    )

    sampling_rate_min = Instrument.measurement(
        "AWGControl:SRATe? MINimum",
        """This property queries the minimum sample rate for the Sampling
        Clock."""
    )

    run_status = Instrument.measurement(
        "AWGControl:RSTATe?",
        """This property returns the run state of the AWG. The possible values
        are: STOPPED, WAITING_TRIGGER, RUNNING""",
        values={"STOPPED": 0, "WAITING_TRIGGER": 1, "RUNNING": 2},
        map_values=True
    )

    enabled = Instrument.control(
        "AWGControl:RSTATe?", "AWGControl:%s",
        """A boolean property that enables the generation of signals.""",
        validator=strict_discrete_set,
        values={True: "RUN", False: "STOP"},
        map_values=True,
        get_process=lambda v: "STOP" if v == 0 else "RUN"
    )

    trigger_source = Instrument.control(
        "TRIGger:SEQuence:SOURce?", "TRIGger:SEQuence:SOURce %s",
        """This property sets or returns the instrument trigger source. The
        possible values are:

        * TIM<ER>: the trigger is sent at regular intervals.
        * EXT<ERNAL>: the trigger come from the external BNC connector.
        * MAN<UAL>: the trigger is sent via software or using the trigger
          button on front panel.""",
        validator=strict_discrete_set,
        values=["TIMER", "TIM", "EXTERNAL", "EXT", "MANUAL", "MAN"]
    )

    waveforms = property(
        lambda self: self._waveforms,
        doc="""This property returns a dict with all the waveform present
        in the instrument system (Wave. List). It is possible to modify the
        values, delete them or create new waveforms""")

    def trigger(self):
        """Force a trigger event to occour."""
        self.write("TRIGger:SEQuence:IMMediate")

    def save_file(self,
                  file_name,
                  data,
                  path=None,
                  override_existing=False):
        """Write a string in a file in the instrument"""

        if path is not None:
            raise NotImplementedError("Specify path is not implemented")

        if file_name in [file.name
                         for file in self.list_files(path=path)
                         if file.type == '']:
            if override_existing:
                self.remove_file(file_name, path=path)
            else:
                raise ValueError("File already exist and override is disabled")

        self.adapter.write_binary_values(
            'MMEM:DATA "' + file_name + '", 0, ',
            data.encode("ASCII"),
            datatype='s')
        # HACK: Send an unuseful command to ensure the last command was
        # executed because if it is more than 1024 bytes it doesn't work
        self.wait_last()

    def remove_file(self, file_name, path=None):
        """Remove a specified file"""

        if path is not None:
            raise NotImplementedError("Specify path is not implemented")

        if file_name not in [file.name
                             for file in self.list_files(path=path)
                             if file.type == '']:
            raise ValueError("File do not exist")

        self.write('MMEMORY:DELETE "' + file_name + '"')

    def list_files(self, path=None):
        """Return a List of tuples with all file found in a directory. If the
        path is not specified the current directory will be used"""

        if path is not None:
            raise NotImplementedError("Specify path is not implemented")

        catalog = self.values("MMEMory:CATalog?")
        catalog = catalog[1:]

        FS_Element = namedtuple("FS_Element", "name type dimension")

        elements = []
        for i in range(int(len(catalog) / 3)):
            elements.append(FS_Element(catalog[i * 3 + 0],
                                       catalog[i * 3 + 1],
                                       catalog[i * 3 + 2]))

        return elements

    class WaveformsLazyDict(abc.MutableMapping):
        """This class inherit from MutableMapping in order to create a custom
        dict to lazy load, modify, delete and create instrument waveform."""

        def __init__(self, parent):
            self.parent = parent
            self.reset()

        def __getitem__(self, key):
            """Load data from instrument if not present"""
            if self._data[key] is None:
                self._data[key] = self._get_waveform(key)
            return self._data[key]

        def __setitem__(self, key, value):
            """Create a new waveform from key and value"""

            if len(value) < 16:
                raise ValueError("The minimum waveform length is 16 samples")
            elif len(value) < 384 and len(value) % 16 != 0:
                raise ValueError("From 16 to 384 samples the granularity of"
                                 "the waveform is 16")

            class VoltageOutOfRangeError(Exception):
                pass

            if max(value) > self.parent.entries[1].ch[1].voltage_high_max:
                raise VoltageOutOfRangeError(
                    f"{max(value)}V is higher than maximum possible voltage, "
                    f"which is "
                    f"{self.instrument.entries[1].ch[1].voltage_high_max}V")
            if min(value) < self.parent.entries[1].ch[1].voltage_low_min:
                raise VoltageOutOfRangeError(
                    f"{min(value)}V is lower than minimum possible voltage, "
                    f"which is "
                    f"{self.instrument.entries[1].ch[1].voltage_low_min}V")

            self.parent.save_file(f"{key}.txt",
                                  "\n".join(map(str, value)),
                                  override_existing=True)

            try:
                del self[key]
            except KeyError:
                pass

            self.parent.write(f'WLISt:WAVeform:IMPort "{key}",'
                              f'"{key}.txt",ANAlog')

            self.parent.wait_last()

            self.parent.remove_file(f"{key}.txt")

            self._data[key] = None
            return

        def __delitem__(self, key):
            """When removing an element this method removes also the
            corresponding waveform in the instrument"""
            del self._data[key]
            self.parent.write(f'WLISt:WAVeform:DELete "{key}"')
            return

        def __iter__(self):
            try:
                for el in self._data:
                    yield el
            except KeyError:
                return

        def __len__(self):
            return len(self._data)

        def __str__(self):
            """Return a str without the waveforms points because it is useless
            and loads all waveforms uselessy"""
            return pprint.pformat({el: "Waveform Points" for el in self._data})

        def reset(self):
            """Reset the class reloading the waveforms from instrument"""
            waveforms_name = self.parent.values("WLISt:LIST?")
            self._data = {v: None for v in waveforms_name}

        def _get_waveform(self, waveform_name):
            """Get the waveform point of a specified waveform"""

            bin_value = self.parent.adapter.connection.query_binary_values(
                'WLISt:WAVeform:DATA? "' + waveform_name + '"',
                header_fmt='ieee',
                datatype='h')

            return bin_value

    class DummyEntriesElements(abc.Sequence):
        """Dummy List Class to list every sequencer entry. The content is
        loaded in real-time."""

        def __init__(self, parent, number_of_channel):
            self.parent = parent
            self.num_ch = number_of_channel

        def resize(self, new_size):
            self.parent.write(f"SEQuence:LENGth {new_size}")

        def __getitem__(self, key):
            if key <= 0:
                raise IndexError("Entry numeration start from 1")
            if key > int(self.parent.values("SEQuence:LENGth?")[0]):
                raise IndexError("Index out of range")
            return (self.parent, self.num_ch, key)

        def __len__(self):
            return int(self.parent.values("SEQuence:LENGth?")[0])


class SequenceEntry(Channel):
    """Implementation of sequencer entry."""

    def __init__(self, parent, number_of_channels, sequence_number):
        super().__init__(parent, sequence_number)
        self.number_of_channels = number_of_channels

        self.length_values = [self.length_min, self.length_max]
        self.loop_count_values = [self.loop_count_min, self.loop_count_max]

        for i in range(1, self.number_of_channels + 1):
            self.add_child(self.AnalogChannel, i, collection="ch",
                           sequence_number=sequence_number)

    def insert_id(self, command):
        return command.format(ent=self.id)

    length = Instrument.control(
        "SEQuence:ELEM{ent}:LENGth?",
        "SEQuence:ELEM{ent}:LENGth %s",
        """This property sets or returns the number of samples of the entry.
        """,
        validator=strict_range,
        dynamic=True
    )

    length_max = Instrument.measurement(
        "SEQuence:ELEM{ent}:LENGth? MAXimum",
        """This property queries the maximum entry samples length.""",
        get_process=lambda v: int(v)
    )

    length_min = Instrument.measurement(
        "SEQuence:ELEM{ent}:LENGth? MINimum",
        """This property queries the minimum entry samples length.""",
        get_process=lambda v: int(v)
    )

    loop_count = Instrument.control(
        "SEQuence:ELEM{ent}:LOOP:COUNt?",
        "SEQuence:ELEM{ent}:LOOP:COUNt %s",
        """This property sets or returns the number of waveform repetitions for
        the entry.
        """,
        validator=strict_range,
        dynamic=True
    )

    loop_count_max = Instrument.measurement(
        "SEQuence:ELEM{ent}:LOOP:COUNt? MAXimum",
        """This property queries the maximum number of waveform repetitions for
        the entry.""",
        get_process=lambda v: int(v)
    )

    loop_count_min = Instrument.measurement(
        "SEQuence:ELEM{ent}:LOOP:COUNt? MINimum",
        """This property queries the minimum number of waveform repetitions for
        the entry.""",
        get_process=lambda v: int(v)
    )

    class AnalogChannel(Channel):
        """Implementation of an analog channel for a single sequencer entry."""

        def __init__(self, parent, id, sequence_number):
            super().__init__(parent, id)
            self.seq_num = sequence_number

            self.waveform_values = list(self.parent.parent.waveforms.keys())
            self.calculate_voltage_range()

        def insert_id(self, command):
            return command.format(ent=self.seq_num, ch=self.id)

        voltage_amplitude = Instrument.control(
            "SEQuence:ELEM{ent}:AMPlitude{ch}?",
            "SEQuence:ELEM{ent}:AMPlitude{ch} %s",
            """This property sets or returns the voltage peak-to-peak
            amplitude.""",
            validator=strict_range,
            dynamic=True
        )

        voltage_amplitude_max = Instrument.measurement(
            "SEQuence:ELEM{ent}:AMPlitude{ch}? MAXimum",
            """This property queries the maximum amplitude voltage level that
            can be set."""
        )

        voltage_amplitude_min = Instrument.measurement(
            "SEQuence:ELEM{ent}:AMPlitude{ch}? MINimum",
            """This property queries the minimum amplitude voltage level that
            can be set."""
        )

        voltage_offset = Instrument.control(
            "SEQuence:ELEM{ent}:OFFset{ch}?",
            "SEQuence:ELEM{ent}:OFFset{ch} %s",
            """This property sets or returns the voltage offset.""",
            validator=strict_range,
            dynamic=True
        )

        voltage_offset_max = Instrument.measurement(
            "SEQuence:ELEM{ent}:OFFset{ch}? MAXimum",
            """This property queries the maximum voltage offset that can be
            set."""
        )

        voltage_offset_min = Instrument.measurement(
            "SEQuence:ELEM{ent}:OFFset{ch}? MINimum",
            """This property queries the minimum voltage offset that can be
            set."""
        )

        voltage_high = Instrument.control(
            "SEQuence:ELEM{ent}:VOLTage:HIGH{ch}?",
            "SEQuence:ELEM{ent}:VOLTage:HIGH{ch} %s",
            """This property sets or returns the high voltage level of the
            waveform.""",
            validator=strict_range,
            dynamic=True
        )

        voltage_high_max = Instrument.measurement(
            "SEQuence:ELEM{ent}:VOLTage:HIGH{ch}? MAXimum",
            """This property queries the maximum high voltage level of the
            waveform that can be set to the output waveform."""
        )

        voltage_high_min = Instrument.measurement(
            "SEQuence:ELEM{ent}:VOLTage:HIGH{ch}? MINimum",
            """This property queries the minimum high voltage level of the
            waveform that can be set to the output waveform."""
        )

        voltage_low = Instrument.control(
            "SEQuence:ELEM{ent}:VOLTage:LOW{ch}?",
            "SEQuence:ELEM{ent}:VOLTage:LOW{ch} %s",
            """This property sets or returns the low voltage level of the
            waveform.""",
            validator=strict_range,
            dynamic=True
        )

        voltage_low_max = Instrument.measurement(
            "SEQuence:ELEM{ent}:VOLTage:LOW{ch}? MAXimum",
            """This property queries the maximum low voltage level of the
            waveform that can be set to the output waveform."""
        )

        voltage_low_min = Instrument.measurement(
            "SEQuence:ELEM{ent}:VOLTage:LOW{ch}? MINimum",
            """This property queries the minimum low voltage level of the
            waveform that can be set to the output waveform."""
        )

        waveform = Instrument.control(
            "SEQuence:ELEM{ent}:WAVeform{ch}?",
            "SEQuence:ELEM{ent}:WAVeform{ch} %s",
            """This property sets or returns the waveform. It’s possible select
            a waveform only from those in the waveform list. In waveform list
            are already present 10 predefined waveform: Sine, Ramp, Square,
            Sync, DC, Gaussian, Lorentz, Haversine, Exp_Rise and Exp_Decay but
            user can import in the list others customized waveforms.""",
            validator=strict_discrete_set,
            set_process=lambda v: f"\"{v}\"",
            dynamic=True
        )

        def calculate_voltage_range(self):
            self.voltage_amplitude_values = [self.voltage_amplitude_min,
                                             self.voltage_amplitude_max]

            self.voltage_offset_values = [self.voltage_offset_min,
                                          self.voltage_offset_max]

            self.voltage_high_values = [self.voltage_high_min,
                                        self.voltage_high_max]

            self.voltage_low_values = [self.voltage_low_min,
                                       self.voltage_low_max]
