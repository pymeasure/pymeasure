#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from pymeasure.instruments import Instrument, SCPIMixin, Channel
from pymeasure.instruments.validators import strict_range, strict_discrete_range, \
    strict_discrete_set

from pyvisa.errors import VisaIOError
import numpy as np

import functools


DISPLAY_LAYOUT_OPTIONS = [
        "D1",
        "D12",
        "D1_2",
        "D112",
        "D1_1_2",
        "D123",
        "D1_2_3",
        "D12_33",
        "D11_23",
        "D13_23",
        "D12_13",
        "D1234",
        "D1_2_3_4",
        "D12_34"
]


class VNATrace(Channel):
    """A trace (of a channel) of the E5061A/E5062A"""

    placeholder = 'tr'      # default ch would collide with VNAChannel

    def activate(self):
        """Select this trace. """
        self.write('CALC{{ch}}:PAR{tr}:SEL')

    parameter = Channel.control(
        "CALCulate{{ch}}:PARameter{tr}:DEFine?",
        "CALCulate{{ch}}:PARameter{tr}:DEFine %s",
        """Control the measurement parameter of the trace (str). Can be
        S11, S21, S12, or S22""",
        validator=strict_discrete_set,
        values=['S11', 'S12', 'S21', 'S22']
    )


class VNAChannel(Channel):
    """A measurement channel of the E5061A/E5062A"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_trace(override_id=1)                 # add just a single trace to init it all
        self._update_trace_count(self.visible_traces)  # add remaining traces if necessary
        self._update_power_values(self.attenuation)    # update dynamic limits of power

    def _add_trace(self, override_id=None):
        """Internal method that adds a trace to the traces list"""
        tr_id = len(self.traces) + 1 if override_id is None else override_id
        self.add_child(VNATrace, tr_id, 'traces', 'tr_')

    def _update_trace_count(self, visible_traces):
        """Internal method that updates the trace list based on the number
        of visible traces.
        """
        while len(self.traces) > visible_traces:
            self.remove_child(self.traces[max(self.traces.keys())])
        while len(self.traces) < visible_traces:
            self._add_trace()

    def _update_power_values(self, attenuation):
        """Internal method that updates the valid range of stimulus power
        based on the configured attenuation"""
        self.power_values = (
            -attenuation - 5,
            -attenuation + 10)

    start_frequency = Channel.control(
        "SENSe{ch}:FREQuency:STARt?", "SENSe{ch}:FREQuency:STARt %g",
        """Control the start frequency in Hz (float).""",
        validator=strict_range,
        values=[3e5, 3e9]
    )

    stop_frequency = Channel.control(
        "SENSe{ch}:FREQuency:STOP?", "SENSe{ch}:FREQuency:STOP %g",
        """Control the stop frequency in Hz (float).""",
        validator=strict_range,
        values=[3e5, 3e9]
    )

    scan_points = Channel.control(
        "SENSe{ch}:SWEep:POINts?", "SENSe{ch}:SWEep:POINts %g",
        """Control the number of points used in a sweep (int). Valid range 2 - 1601.""",
        cast=int,
        validator=functools.partial(strict_discrete_range, step=1),
        values=range(2, 1602)
    )

    sweep_time = Channel.control(
        "SENSe{ch}:SWEep:TIME?", "SENSe{ch}:SWEep:TIME %g",
        """Control the sweep time in seconds (float). The allowable range
        varies on config and the set value is truncated. Note that
        ``sweep_time_auto_enabled`` needs to be ``False`` for changes to this
        property to have an effect."""
    )

    sweep_time_auto_enabled = Channel.control(
        "SENSe{ch}:SWEep:TIME:AUTO?", "SENSe{ch}:SWEep:TIME:AUTO %d",
        """Control whether to automatically set the sweep time (bool). You
        probably want this on to always keep the sweep time to a minimum (given
        the range, IF BW, and sweep delay time).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
    )

    sweep_type = Channel.control(
        "SENSe{ch}:SWEep:TYPE?", "SENSe{ch}:SWEep:TYPE %s",
        """Control the type of the sweep (string).

        =======  ===========
        Setting  Description
        =======  ===========
        LIN      Linear
        LOG      Logarithmic
        SEGM     Segment
        POW      Power
        =======  ===========

        Defaults to linear. Note that the API for configuring segment type
        sweeps is not implememented in this class.""",
        validator=strict_discrete_set,
        values=['LIN', 'LOG', 'SEGM', 'POW']
    )

    averaging_enabled = Channel.control(
        "SENSe{ch}:AVERage?", "SENSe{ch}:AVERage %d",
        """Control whether to average the measurement data (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
    )

    def restart_averaging(self):
        """
        Clear averaging history.
        """
        self.write("SENSe{ch}:AVERage:CLEar")

    averages = Channel.control(
        "SENSe{ch}:AVERage:COUNt?", "SENSe{ch}:AVERage:COUNt %d",
        """Control how many averages to take, from 1-999 (int). Note that
        ``averaging_enabled`` needs to be true for averaging to be enabled.""",
        cast=lambda x: int(float(x)),
        validator=strict_range,
        values=[1, 999]
    )

    IF_bandwidth = Channel.control(
        "SENSe{ch}:BANDwidth?", "SENSe{ch}:BANDwidth %d",
        """Control the IF bandwidth in Hz (int), from 10 Hz to 30 kHz. Default
        30 kHz.""",
        cast=lambda x: int(float(x)),
        validator=strict_range,
        values=[10, 30000]
    )

    def activate(self):
        """Activate (select) the current channel. Note that the channel
        must first be displayed (via AgilentE5062A.display_layout) for it
        to be activatable.

        """
        if str(self.id) not in self.parent.display_layout:
            raise ValueError('Cannot activate a channel that is not displayed')
        self.write("DISP:WIND{ch}:ACT")

    @property
    def visible_traces(self):
        """Control the number of traces visible in the channel (int)."""
        return int(self.ask("CALC{ch}:PARameter:COUNt?"))

    @visible_traces.setter
    def visible_traces(self, value):
        value = int(float(value))
        value = strict_range(value, [1, 4])
        self.write("CALC{ch}:PARameter:COUNt %d" % value)
        self._update_trace_count(value)

    power = Channel.control(
        "SOURce{ch}:POWer?", "SOURce{ch}:POWer %g",
        """Control the simulus power in dBm (float). The allowable range is
        influenced by the value of ``attenuation``. """,
        validator=strict_range,
        values=(-5, 10),
        dynamic=True,
    )

    @property
    def attenuation(self):
        """Control the stimulus attenuation in dB (positive int), from 0 to 40
        in incrememnts of 10. Default is 0 dB. The allowable stimulus power
        range is a 15 dB range: (``attenuation`` - 5 dB, ``attenuation`` + 10
        dB).

        This requires the power range extension, and the command is ignored
        if the extension is not installed.

        """
        return int(float(self.ask("SOURce{ch}:POWer:ATTenuation?")))

    @attenuation.setter
    def attenuation(self, value):
        value = int(float(value))
        value = strict_discrete_set(value, [0, 10, 20, 30, 40])
        self.write("SOURce{ch}:POWer:ATTenuation %d" % value)
        self._update_power_values(value)

    display_layout = Channel.control(
        "DISPlay:WINDow{ch}:SPLit?", "DISPlay:WINDow{ch}:SPLit %s",
        """Control the graph layout of the traces in the channel (str). Does
        not affect how many traces are active. See the list of valid options:

        - D1
        - D12
        - D1_2
        - D112
        - D1_1_2
        - D123
        - D1_2_3
        - D12_33
        - D11_23
        - D13_23
        - D12_13
        - D1234
        - D1_2_3_4
        - D12_34

        In general, an occurance of a number denotes the associated trace
        having it's own subplot and an occurence of '_' denotes a vertical
        split. Multiple occurences of the same number denote the trace
        having a larger window than the other traces. Refer to Figure 3-1
        in the the programmer's manual for details. If a trace is active
        but it's associated number is not present in the ``display_layout``
        identifier, it is plotted in the first subplot.

        """,
        validator=strict_discrete_set,
        values=DISPLAY_LAYOUT_OPTIONS
    )

    TRACE_FORMAT = [
        'MLOG',
        'PHAS',
        'GDEL',
        'SLIN',
        'SLOG',
        'SCOM',
        'SMIT',
        'SADM',
        'PLIN',
        'PLOG',
        'POL',
        'MLIN',
        'SWR',
        'REAL',
        'IMAG',
        'UPH',
        'PPH'
    ]

    trace_format = Channel.control(
        "CALCulate{ch}:FORMat?",
        "CALCulate{ch}:FORMat %s",
        """Control the data format of the *active trace* of the channel
        (str). Default is MLOGarithmic. From the programmer's manual:

        =======  =============================================
        Setting  Description
        =======  =============================================
        MLOG     Specifies the logarithmic magnitude format.
        PHAS     Specifies the phase format.
        GDEL     Specifies the group delay format.
        SLIN     Specifies the Smith chart format (Lin/Phase).
        SLOG     Specifies the Smith chart format (Log/Phase).
        SCOM     Specifies the Smith chart format (Real/Imag).
        SMIT     Specifies the Smith chart format (R+jX).
        SADM     Specifies the Smith chart format (G+jB).
        PLIN     Specifies the polar format (Lin).
        PLOG     Specifies the polar format (Log).
        POr      Specifies the polar format (Re/Im).
        MLI      Specifies the linear magnitude format.
        SWR      Specifies the SWR format.
        REAL     Specifies the real format.
        IMAG     Specifies the imaginary format.
        UPH      Specifies the expanded phase format.
        PPH      Specifies the positive phase format.
        =======  =============================================

        """,
        validator=strict_discrete_set,
        values=TRACE_FORMAT
        )

    def _read_binary_data(self):
        """Internal method that reads and interprents binary data arrays as
        floats. Assumes the query has already been sent.

        Uses the IEEE 64-bit fp transer format (little-endian).

        """
        header = self.read_bytes(8)  # 2 start bytes + 6 <nbytes> bytes
        if not header[0:2].decode('ascii') == '#6':
            raise ValueError('''Unrecognized header. Ensure the data transfer
            format (FORM:DATA?) is set to "REAL"''')
        nbytes = int(header[2:].decode('ascii'))
        binary_data = self.read_bytes(nbytes)
        terminator = self.read_bytes(1)
        if terminator.decode('ascii') != '\n':
            raise ValueError(f'Unexpected terminator {terminator} (expected \\n)')
        return np.frombuffer(binary_data, dtype='<f8')

    @property
    def data(self):
        """Measure the Formatted Data of the *active trace*.

        Each trace consists of ``scan_points`` plotted either vs. frequency
        or in something like a smith-chart configuration. This property
        does not access any frequency information. So for rectangular
        plots, this query returns only the y-values of the trace (no
        frequency information). For smith- and polar- plots, this two
        values per data point.

        This function returns a tuple containing both a primary and a
        secondary data numpy array. The secondary data is all zeros for all
        trace formats that are not smith or polar. The implication for this
        is that the best way to save complex S-parameter data in one go is
        to use a Smith (Real/Imag) or Polar (Real/Imag) trace format,
        (SCOMplex and POLar, respectively).

        The formatted data array is settable in the VNA but not implemented
        in this python API.

        Frequency data is accessed via the ``frequencies`` property.

        .. code-block:: python

            # build an s-parameter matrix by measuring the trace data,
            # where s_matrix[i] = [[S11, S12], [S21, S22]] @ freqs[i]
            freqs = ch.frequencies
            s_matrix = np.empty((freqs.size, 4), dtype=np.complex64)
            for i, tr in enumerate(ch.traces.values()):
                tr.activate()
                ch.trace_format = 'POL'
                re, im = ch.data
                s_matrix[:, i] = re + 1j * im
            s_matrix = s_matrix.reshape(-1, 2, 2)  # ready for use with e.g. skrf

        """
        self.write(f'CALC{self.id}:DATA:FDAT?')
        numeric_data = self._read_binary_data()
        primary_data = numeric_data[::2]
        secondary_data = numeric_data[1::2]
        return primary_data, secondary_data

    @property
    def frequencies(self):
        """Measure the frequency in Hz associated with each data point of the
        *active trace*. Returns a numpy array.

        """
        self.write(f'SENS{self.id}:FREQ:DATA?')
        return self._read_binary_data()

    trigger_continuous = Instrument.control(
        "INITiate{ch}:CONTinuous?", "INITiate{ch}:CONTinuous %d",
        """Control whether the channel triggers continuously (bool). If
        not, after a sweep is complete, the global trigger enters the hold
        state, and will not respond to triggers.  """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
    )

    def trigger_initiate(self):
        """If the trigger is in the hold state (i.e. ``trigger_continuous``
        is off and the measurement has completed), re-initialize the
        trigger for a single measurement.

        """
        self.write(f'INITiate{self.id}')


class AgilentE5062A(SCPIMixin, Instrument):
    """Represents the Agilent E5062A Vector Network Analyzer

    This VNA has 4 separate channels, each of which has its own sweep. The
    channels are stored in the ``channels`` dictionary. Channels can be enabled
    even if not displayed. Many trace-specific operations, including reading
    out data, happen at the channel level, but pertain to only the *active
    trace*.

    Each channel can display up to 4 traces (controlled via the
    ``visible_traces`` parameter). Each channel also has a ``display_layout``
    property that controls the layout of the traces in the channel. The traces
    are accessed via the ``traces`` dictionary
    (i.e. ``vna.channels[1].traces[1]``).

    The VNA supports multiple transfer formats. This API only supports the IEEE
    64-bit floating point format. The VNA is configured for this format during
    initialization, and the data transfer format is not a publicly accessible
    property.

    This class implements only a subset of the total E5062A functionality. The
    more significant missing functionality includes (TODO):

    - editing the scale of the display
    - markers
    - calibration
    - power sweeps

    .. code-block:: python

        # connect to the VNA and make a measurement consisting of 10 averages
        vna = AgilentE5062A("TCPIP::192.168.2.233::INSTR")
        ch = vna.channels[1]            # use channel 1
        ch.visible_traces = 4            # use all 4 traces
        for i, (tr, parameter) in enumerate(zip(
                ch.traces.values(),
                ['S11', 'S12', 'S21', 'S22'])):
            tr.parameter = parameter

        ch.averages = 10                # use 10x averaging
        ch.averaging_enabled = True     # turn averaging on
        ch.trigger_continuous = False   # turn off continuous triggering
        vna.trigger_source = 'BUS'      # require remote trigger
        vna.abort()                     # stop the current sweep
        ch.restart_averaging()          # clear current averaging
        for _ in range(ch.averages):
            ch.trigger_initiate()       # arm channel 1 for single sweep
            vna.trigger_single()        # send a trigger
            vna.wait_for_complete()     # wait until the sweep is complete

        # see `agilentE5062A.data` for an example of saving the measurement

    """

    ch_1 = Instrument.ChannelCreator(VNAChannel, 1)
    ch_2 = Instrument.ChannelCreator(VNAChannel, 2)
    ch_3 = Instrument.ChannelCreator(VNAChannel, 3)
    ch_4 = Instrument.ChannelCreator(VNAChannel, 4)

    def __init__(
            self,
            adapter,
            name="Agilent E5062A Vector Network Analyzer",
            **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.write("FORMat:DATA REAL")  # set data transfer format to IEEE fp64
        self.write("FORMat:BORDer SWAPped")  # ensure byte-order is little-endian

    display_layout = Instrument.control(
        "DISPlay:SPLit?", "DISPlay:SPLit %s",
        """Control the layout of the windows (channels) on the display
        (str). See the list of valid options below:

        - D1
        - D12
        - D1_2
        - D112
        - D1_1_2
        - D123
        - D1_2_3
        - D12_33
        - D11_23
        - D13_23
        - D12_13
        - D1234
        - D1_2_3_4
        - D12_34

        In general, an occurance of a number denotes the associated channel
        being visible and an occurence of '_' denotes a vertical
        split. Multiple occurences of the same number denote the channel having
        a larger window than the other channels. Refer to Figure 3-1 in the the
        programmer's manual for details.

        Note that this splits windows for multiple *channels*, not
        traces. Basic S-param measurements most likely want to use only a
        single channel, but with multuple *traces* instead. See
        e.g. ``AgilentE5062A.channels[1].visible_traces``
        """,
        validator=strict_discrete_set,
        values=DISPLAY_LAYOUT_OPTIONS
    )

    output_enabled = Instrument.control(
        "OUTPut?", "OUTPUT %d",
        """Control whether to turn on the RF stimulus (bool). The stimulus
        needs to be on to perform any measurement. Beware that the stimulus is
        on by default! (i.e. after reset())""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
    )

    def abort(self):
        """Abort the current sweep (affects the trigger fsm, see page 80 of the
        programmer's manual for details)

        """
        self.write(":ABOR")

    trigger_source = Instrument.control(
        "TRIGger:SOURce?", "TRIGger:SOURce %s",
        """Control the trigger source (str). From the documentation:

        - INT: Uses the internal trigger to generate continuous triggers
          automatically (default).
        - EXT: Generates a trigger when the trigger signal is inputted
          externally via the Ext Trig connector or the handler interface.
        - MAN: Generates a trigger when the key operation of [Trigger] -
          Trigger is executed from the front panel.
        - BUS: Generates a trigger when the ``*TRG`` command is executed.

        """,
        validator=strict_discrete_set,
        values=[
            'INT',
            'EXT',
            'MAN',
            'BUS'])

    def trigger_bus(self):
        """If the trigger source is BUS and the VNA is waiting for a trigger
        (the trigger has been initialized), generate a trigger.

        """
        self.write('*TRG')

    def trigger(self):
        """Regardless of the trigger setting, generate a trigger (if the
        trigger has been initialized, i.e. is in the trigger wait state)

        """
        self.write('TRIGger')

    def trigger_single(self):
        """like trigger(), but the `complete` SCPI property (synchronization
        bit) waits for the sweep to be complete (see
        `agilentE5062A.wait_for_complete()`).

        """
        self.write('TRIGger:SINGle')

    def wait_for_complete(self, attempt=1, max_attempts=20):
        """Wait a potentially long time for the synchronization bit.  This is
        useful in conjunction with `agilentE5062A.trigger_single()` to wait for
        a single sweep to complete.

        """
        try:
            self.complete
        except VisaIOError:
            if attempt == max_attempts:
                raise
            else:
                self.wait_for_complete(
                    attempt=attempt+1,
                    max_attempts=max_attempts)

    def pop_err(self):

        """Pop an error off the error queue. Returns a tuple containing the
        code and error description. An error code 0 indicates success.

        The Error queue can be cleared using the standard SCPI
        ``agilentE5062A.clear()`` method.

        """
        error_str = self.ask('SYST:ERR?').strip()
        error_code_str, error_desc_str = error_str.split(',')
        error_code = int(error_code_str)
        error_desc = error_desc_str.strip('"')
        return error_code, error_desc
