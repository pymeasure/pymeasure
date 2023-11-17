#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import numpy as np
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from time import sleep, time
from pyvisa.errors import VisaIOError


class ChannelBase():
    """ Implementation of a Lecroy MAUI channel. Note, that is
    The primary command style is the VBS style instead of the SCPI-like commands. Why?
    There is literally no complete command reference. I had to root around the instrument
    COM explorer to figure out how to access these parameters. Subclass this for a
    specific scope.

    Implementation modeled on Channel object of Tektronix AFG3152C instrument. Majority of
     driver re-used from  DSOX1102G. Maybe this is a deep statement about a base oscilloscope class.
     """

    BOOLS = {True: -1, False: 0}

    coupling = Instrument.control(
        'Coupling', """Coupling = "%s" """,
        """A string parameter that gets or sets the input impedance of the channel""",
        validator=strict_discrete_set,
        values=['DC1M', 'AC1M', 'DC50', 'GND'],
    )

    average_sweeps = Instrument.control(
        # good?
        "AverageSweeps", """AverageSweeps = %d """,
        """ An integer parameter that sets the number of sweeps to average on this channel.
        Range is 1 to 1,000,000""",
        validator=strict_range,
        values=[1,1000000],
    )

    display = Instrument.control(
        #good?
        "View", "View = %d",
        """ A boolean parameter that toggles the display.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )


    offset = Instrument.control(
        #good?
        "VerOffset", "VerOffset = %f",
        """ A float parameter to set value that is represented at center of screen in 
        Volts. The range of legal values varies depending on range and scale. If the specified value 
        is outside of the legal range, the offset value is automatically set to the nearest legal value. """
    )


    scale = Instrument.control(
        #good
        "VerScale", "VerScale = %f",
        """ A float parameter that specifies the vertical scale, or units per division, in Volts. 
        Limits are [1e-3,1]"""
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        #good
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values("""vbs? 'return = app.acquisition.C%d.%s'""" % (
            self.number, command), **kwargs)

    def ask(self, command):
        #good
        self.instrument.ask("""vbs? 'return = app.acquisition.C%d.%s'""" % (self.number, command))

    def write(self, command):
        #good
        self.instrument.write("""vbs 'app.acquisition.C%d.%s'""" % (self.number, command))


class LecroyMAUIBase(Instrument):
    """ Represents the Lecroy MAUI interface. Make sure you set the communication to LXI
    and not TCPIP (VICP) on the scope if you want this code to work out of the box.
    You'll get a message of "Warning: Remote Interface is TCPIP" if you forget.
    Also, when passing strings in a write command using the vbs system, the string arguments
    need to be inside double quotes. This is because the scope executes the sent command locally
    so it needs to be correctly delimited inside the SCPI style string. String-ception.

    .. code-block:: python

        scope = LecroyWM845Zi_A(resource)
        scope.autoscale()
        ch1_data_array, ch1_preamble = scope.download_data(source="channel1", points=2000)
        # ...
        scope.shutdown()

    """

    BOOLS = {True: 1, False: 0}

    def __init__(self, adapter, *args, **kwargs):
        super(LecroyMAUIBase, self).__init__(
            adapter, "Lecroy MAUI Base", **kwargs
        )
        # Account for setup time for timebase_mode, waveform_points_mode
        self.adapter.connection.timeout = 6000
        self.system_headers = False
        self.ch1 = ChannelBase(self, 1)
        self.ch2 = ChannelBase(self, 2)
        self.ch3 = ChannelBase(self, 3)
        self.ch4 = ChannelBase(self, 4)
        self.ch5 = ChannelBase(self, 5)
        self.ch6 = ChannelBase(self, 6)
        self.ch7 = ChannelBase(self, 7)
        self.ch8 = ChannelBase(self, 8)


    system_headers = Instrument.control(
        #good
        "CHDR?", "CHDR %s",
        """ A boolean parameter controlling whether or not the oscope returns headers with queries""",
        validator=strict_discrete_set,
        values={True: 'SHORT', False: 'OFF'},
        map_values=True
    )

    ##################
    # Timebase Setup #
    ##################

    timebase_offset = Instrument.control(
        #good
        "vbs? 'return = app.acquisition.horizontal.HorOffset'",
        "vbs 'app.acquisition.horizontal.HorOffset = %.4E'",
        """ A float parameter that sets the time interval in seconds between the trigger 
        event and the reference position (at center of screen by default). Reference position set
        by self.timebase_origin in divs.""",
        validator=strict_range,
        values=[-2e-4, 1.4999e-3]
    )

    timebase_origin = Instrument.control(
        #good
        "vbs? 'return = app.acquisition.horizontal.HorOffsetOrigin'",
        "vbs 'app.acquisition.horizontal.HorOffsetOrigin = %.4E'",
        """ A float parameter that sets the time interval in seconds between the trigger 
        event and the reference position (at center of screen by default). Reference position set
        by self.timebase_origin in divs.""",
        validator=strict_discrete_set,
        values=list(range(11))
    )

    timebase_scale = Instrument.control(
        #good
        "vbs? 'return = app.acquisition.horizontal.HorScale'",
        "vbs 'app.acquisition.horizontal.HorScale = %.4E'",
        """ A float parameter that sets the horizontal scale (units per division) in seconds 
        for the main window."""
    )

    ###########
    # Trigger #
    ###########

    aux_in_coupling = Instrument.control(
        # good
        "vbs? 'return = app.acquisition.auxin.Coupling'",
        """vbs 'app.acquisition.auxin.Coupling = "%s"'""",
        """ A string control that sets the aux input coupling. Can be DC50, DC1M, or GND""",
        validator=strict_discrete_set,
        values=['DC50', 'DC1M', 'GND']
    )

    trigger_mode = Instrument.control(
        #good
        "vbs? 'return = app.acquisition.trigger.Type'",
        """vbs 'app.acquisition.trigger.Type = "%s"'""",
        """ A string control that sets the trigger mode. Only EDGE is implemented. 
        EDGE is the most common option""",
        validator=strict_discrete_set,
        values=['EDGE']
    )


    trigger_edge_slope = Instrument.control(
        #good
        "vbs? 'return = app.acquisition.trigger.edge.Slope'",
        """vbs 'app.acquisition.trigger.edge.Slope = "%s"'""",
        """ A string control that sets the slope of the edge trigger to:
        'POSITIVE', 'NEGATIVE', or 'EITHER' """,
        validator=strict_discrete_set,
        values=['POSITIVE', 'NEGATIVE','EITHER']
    )

    trigger_coupling = Instrument.control(
        # good
        "vbs? 'return = app.acquisition.trigger.edge.Coupling'",
        """vbs 'app.acquisition.trigger.edge.Coupling = "%s"'""",
        """ A string control that sets the coupling of the trigger:
        'DC', 'AC', 'LFREJ', 'HFREJ' """,
        validator=strict_discrete_set,
        values=['DC', 'AC', 'LFREJ', 'HFREJ']
    )

    trigger_edge_level = Instrument.control(
        #good
        "vbs? 'return = app.acquisition.trigger.edge.Level'",
        """vbs 'app.acquisition.trigger.edge.Level = %.3E'""",
        """ A float control that sets the trigger level in V, range is +-0.82 V""",
        validator=strict_range,
        values=[-0.82, 0.82]
    )

    def setup_sequence(self, sequence_on, n_sequences=1):
        """
        Turn sequence mode on or off with sequence_on = [True, False] and
        if True, specify the number of sequences to record. Memory depth is left
        to the scope to optimize. Note: turning sequence on or off will invoke an
        auto-calibrate.
        """
        if sequence_on:
            self.write(f'SEQ ON, {n_sequences}')
        else:
            self.write('SEQ OFF')

    def sequence_status(self):
        """Returns the status of the sequencing mode on the oscillscope."""
        status = self.ask('SEQ?').strip()
        state, nseq, memdepth = status.split(',')
        mapper = {'ON': True, 'OFF': False}
        return {'is_on': mapper[state], 'n_sequences': int(nseq), 'memdepth': float(memdepth)}


    def clear_sweeps(self):
        self.write("""VBS 'app.ClearSweeps'""")

    def trigger_edge_source(self, channel):
        #good
        """
        Function to set the edge trigger source
        :param channel: Integer corresponding to a given channel (0 is aux)
        :return:
        """
        if channel == 0:
            source = 'Ext'
        elif channel in [1, 2, 3, 4, 5, 6, 7, 8]:
            source = 'C%d' % channel
        else:
            raise ValueError(f'{channel} not a valid trigger source')
        self.write(f"""VBS 'app.Acquisition.trigger.edge.Source ="{source}"'""")

    def set_edge_trigger(self, source, level, slope):
        """
        Convenience function to set the scope trigger to edge, source to channel source at the specified level
        """
        self.trigger_mode = 'EDGE'
        self.trigger_edge_level = level
        self.trigger_edge_slope = slope
        self.trigger_edge_source(source)

    ###############
    # Acquisition #
    ###############

    run_state = Instrument.control(
        "TRMD?", "TRMD %s",
        """Control of the instrument run state. Can be:
         NORM, STOP, SINGLE, AUTO""",
        validator=strict_discrete_set,
        values=['NORM', 'STOP', 'SINGLE', 'AUTO']
    )

    def run(self):
        #good
        """ Starts repetitive acquisitions. This is the same as pressing the Run key on the front panel."""
        self.run_state = 'NORM'

    def stop(self):
        #good
        """  Stops the acquisition. This is the same as pressing the Stop key on the front panel."""
        self.run_state = 'STOP'

    def single(self):
        #good
        """ Causes the instrument to acquire a single trigger of data.
        This is the same as pressing the Single key on the front panel. """
        self.run_state = 'SINGLE'

    def wait_for_idle(self, basewait=0.01, timeout=5):
        cmd = f"""vbs? 'return=app.WaitUntilIdle({basewait})"""
        returned = int(self.ask(cmd))
        breaker = int(timeout / basewait)
        if breaker <= 0:
            raise ValueError(f'timeout {timeout} is shorter than wait {basewait}')
        i = 0
        while returned == 0. and i < breaker:
            sleep(basewait)
            returned = int(self.ask(cmd))
            i += 1


    def wait_for_op(self, timeout=3600, should_stop=lambda: False):
        #good
        """ Wait until all operations have finished or timeout is reached.

        :param timeout: The maximum time the waiting is allowed to take. If
                        timeout is exceeded, a TimeoutError is raised. If
                        timeout is set to zero, no timeout will be used.
        :param should_stop: Optional function (returning a bool) to allow the
                            waiting to be stopped before its end.

        """
        self.write("*OPC?")

        t0 = time()
        while True:
            try:
                ready = bool(self.read())
            except VisaIOError:
                ready = False

            if ready:
                return

            if timeout != 0 and time() - t0 > timeout:
                raise TimeoutError(
                    "Timeout expired while waiting for the Agilent 33220A" +
                    " to finish the triggering."
                )

            if should_stop():
                return

    autocalibrate = Instrument.control(
        # good
        "AUTO_CALIBRATE?", "AUTO_CALIBRATE %s",
        """ A boolean parameter controlling whether or not the oscope autocalibrates at every setup change""",
        validator=strict_discrete_set,
        values={True: 'ON', False: 'OFF'},
        map_values=True
    )

    def force_cal(self):
        self.write('*CAL?')

    waveform_format = Instrument.control(
        #good
        "CFMT?", "CFMT DEF9, %s, BIN",
        """ A string parameter that controls how the data is formatted when sent from the 
        oscilloscope.  "WORD" or "BYTE". Words are transmitted in little endian by default.""",
        validator=strict_discrete_set,
        values=["WORD", "BYTE"],
    )

    waveform_byteorder = Instrument.control(
        #good
        "COMM_ORDER?", "COMM_ORDER %s",
        """ A string parameter that endianess of the transmitted data. options are 'big' or 'little'""",
        validator=strict_discrete_set,
        values={"little": "LO", "big": "HI"},
        map_values=True
    )

    @property
    def waveform_sparsing(self):
        full = self.ask('WAVEFORM_SETUP?')
        full = full.split(',')
        return int(full[1])

    @waveform_sparsing.setter
    def waveform_sparsing(self, val):
        self.write(f'WAVEFORM_SETUP SP,{int(val)}')

    @property
    def waveform_preamble(self, channel=None):
        #good
        """ Get preamble information for the selected waveform source as a dict with the following keys:
            - "format": byte, word, or ascii (str)
            - "type": normal, peak detect, or average (str)
            - "points": nb of data points transferred (int)
            - "count": always 1 (int)
            - "xincrement": time difference between data points (float)
            - "xorigin": first data point in memory (float)
            - "xreference": data point associated with xorigin (int)
            - "yincrement": voltage difference between data points (float)
            - "yorigin": voltage at center of screen (float)
            - "yreference": data point associated with yorigin (int)"""
        return self._waveform_preamble(channel=channel)



    def waveform_data_word(self, source, sparsing=0):
        #good
        """ Get the block of sampled data points transmitted using the IEEE 488.2 arbitrary
        block data format. valid sources are C1, C2, C3, C4, F1-4, M1-4
        Sparsing is the Lecroy sparsing factor. If you want to keep every nth point,
        set sparsing to n-1. """
        # Other waveform formats raise UnicodeDecodeError
        self.waveform_sparsing = sparsing
        self.waveform_format = "WORD"
        self.waveform_byteorder = 'little'
        preamble = self.waveform_preamble
        data = self.adapter.connection.query_binary_values(f"{source}:WAVEFORM? ", datatype='h')
        sparsing_factor = 1
        if preamble['SPARSING_FACTOR'] > 0:
            sparsing_factor = int(preamble['SPARSING_FACTOR'])
        data = data[-preamble['points']//(sparsing_factor):]

        return data

    ################
    # System Setup #
    ################


    def ch(self, channel_number):
        #good
        if not isinstance(channel_number, int):
            raise ValueError(f'Channel number must be an int, not {type(channel_number)}')
        if channel_number in [1,2,3,4,5,6,7,8]:
            return getattr(self, f'ch{channel_number}')
        else:
            raise ValueError(f"Invalid channel number: {channel_number}. Must be 1-8.")

    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.values(":SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Lecroy MAUI: %s: %s" % (err[0], err[1])
                log.error(errmsg + "\n")
            else:
                break

    def clear_status(self):
        """ Clear device status. """
        self.write("*CLS")


    def factory_reset(self):
        """ Factory default setup, no user settings remain unchanged. """
        self.write("*RST")

    def default_setup(self):
        """ Default setup, some user settings (like preferences) remain unchanged. """
        self.write("""vbs 'app.settodefaultsetup' """)

    def timebase_setup(self, offset=None, horizontal_range=None, scale=None):
        """ Set up timebase. Unspecified parameters are not modified. Modifying a single parameter might
        impact other parameters. Refer to oscilloscope documentation and make multiple consecutive calls
        to channel_setup if needed.

        :param mode: Timebase mode, can be "main", "window", "xy", or "roll".
        :param offset: Offset in seconds between trigger and center of screen.
        :param horizontal_range: Full-scale range in seconds.
        :param scale: Units-per-division in seconds."""

        if offset is not None: self.timebase_offset = offset
        if horizontal_range is not None: self.timebase_range = horizontal_range
        if scale is not None: self.timebase_scale = scale


    def _waveform_preamble(self, channel=None):
        #good
        """
        Reads waveform preamble and converts it to a more convenient dict of values.
        """
        wfdata = {}
        if channel is not None:
            out = self.ask(f'C{channel}:INSPECT? "WAVEDESC"').split('\r\n')[1:-1]
        else:
            out = self.ask('INSPECT? "WAVEDESC"').split('\r\n')[1:-1]
        for elem in out:
            key = elem.split(':')[0].strip()
            value = elem.split(':')[1].strip()
            try:
                value = int(value)
            except:
                try:
                    value = float(value)
                except:
                    pass
            wfdata[key] = value

        wfdata["format"] = wfdata['COMM_TYPE']
        wfdata['points'] = wfdata['PNTS_PER_SCREEN']
        if wfdata['SPARSING_FACTOR'] > 0:
            wfdata['xincrement'] = wfdata['HORIZ_INTERVAL'] * wfdata['SPARSING_FACTOR']
        else:
            wfdata['xincrement'] = wfdata['HORIZ_INTERVAL']
        wfdata['xorigin'] = wfdata['HORIZ_OFFSET']
        wfdata['yincrement'] = wfdata['VERTICAL_GAIN']
        wfdata['yorigin'] = wfdata['VERTICAL_OFFSET']
        wfdata['xreference'] = wfdata['FIRST_POINT']

        return wfdata
