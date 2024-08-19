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
import struct
from pyvisa.errors import VisaIOError

tdiv_enum=[100e-12,200e-12,500e-12,\
 1e-9,2e-9,5e-9,10e-9,20e-9,50e-9,100e-9,200e-9,500e-9,\
 1e-6,2e-6,5e-6,10e-6,20e-6,50e-6,100e-6,200e-6,500e-6,\
 1e-3,2e-3,5e-3,10e-3,20e-3,50e-3,100e-3,200e-3,500e-3,\
 1,2,5,10,20,50,100,200,500,1000]

STR_BOOLS = {True: 'ON', False: 'OFF'}

class ChannelBase():
    """ Implementation of a Lecroy T3DSO channel. This scope isn't running windows and
    thus does not have MAUI. Instead we get bare-bones SCPI.

    Implementation modeled on Channel object of Tektronix AFG3152C instrument. Majority of
     driver re-used from  DSOX1102G. Maybe this is a deep statement about a base oscilloscope class.
     """

    BOOLS = {True: -1, False: 0}
    

    bwlimit = Instrument.control(
        'BWLimit?', "BWLimit %s",
        """A string parameter that gets or sets the bandwidth limit of the channel""",
        validator=strict_discrete_set,
        values=['FULL', '20M', '200M'],
    )

    coupling = Instrument.control(
        'Coupling?', "Coupling %s",
        """A string parameter that gets or sets the input coupling of the channel""",
        validator=strict_discrete_set,
        values=['DC', 'AC', 'GND'],
    )

    impedance = Instrument.control(
        'IMPedance?', "IMPedance %s",
        """A string parameter that gets or sets the input impedance of the channel""",
        validator=strict_discrete_set,
        values=['ONEM', 'FIFT', 'ONEMeg', 'FIFTY'],
    )

    offset = Instrument.control(
        'OFFset?', "OFFset %f",
        """A parameter that gets or sets the offset of the channel""",
    )

    scale = Instrument.control(
        # good
        "SCALe?", "SCALe %f",
        """ A float parameter that specifies the vertical scale, or units per division, in Volts. 
        Limits are [1e-3,1]"""
    )

    switch = Instrument.control(
        # good
        "SWITch?", "SWITch %s",
        """ A string parameter that physically switches the channel on or off,
        also setting the display on or off""",
        validator=strict_discrete_set,
        values=STR_BOOLS,
        map_values=True
    )

    display = Instrument.control(
        #good?
        "VISible", "VISible %s",
        """ A boolean parameter that toggles the display only.""",
        validator=strict_discrete_set,
        values=STR_BOOLS,
        map_values=True
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        #good
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values(""":CHAN%d:%s""" % (
            self.number, command), **kwargs)

    def ask(self, command):
        #good
        self.instrument.ask(""":CHAN%d:%s""" % (self.number, command))

    def write(self, command):
        #good
        self.instrument.write(""":CHAN%d:%s""" % (self.number, command))


class LecroyT3DSOBase(Instrument):
    """ Represents the Lecroy T3DSO interface.

    .. code-block:: python

        scope = LecroyT3DSOBase(resource)
        scope.autoscale()
        ch1_data_array, ch1_preamble = scope.download_data(source="channel1", points=2000)
        # ...
        scope.shutdown()

    """

    BOOLS = {True: 1, False: 0}

    def __init__(self, adapter, *args, **kwargs):
        super(LecroyT3DSOBase, self).__init__(
            adapter, "Lecroy T3DSO Base", **kwargs
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




    ##################
    # Timebase Setup #
    ##################

    timebase_offset = Instrument.control(
        ":TIMebase:DELay?",
        ":TIMebase:DELay %.4E",
        """ A float parameter that sets the time interval in seconds between the trigger 
        event and the reference position (at center of screen by default). Positive value means
        trigger is left of the center""",
        validator=strict_range,
        values=[-2e-4, 1.4999e-3]
    )

    timebase_scale = Instrument.control(
        #good
        ":TIMebase:SCALe?",
        ":TIMebase:SCALe %.4E",
        """ A float parameter that sets the horizontal scale (units per division) in seconds 
        for the main window."""
    )

    ###########
    # Trigger #
    ###########


    trigger_type = Instrument.control(
        ":TRIGger:TYPE?",
        """:TRIGger:TYPE %s""",
        """ A string control that sets the trigger mode. Only EDGE is implemented. 
        EDGE is the most common option""",
        validator=strict_discrete_set,
        values=['EDGE', 'PULSE','SLOPe','INTerval','PATTern','RUNT','QUALified',
                'WINDow','DROPout','VIDeo','QUALified','NTHEdge','DELay','SETuphold',
                'IIC','SPI','UART','LIN','CAN','FLEXray','CANFd','IIS','1553B','SENT']
    )


    trigger_edge_slope = Instrument.control(
        #good
        ":TRIGger:EDGE:SLOPe?",
        """:TRIGger:EDGE:SLOPe %s""",
        """ A string control that sets the slope of the edge trigger to:
        'RIS', 'FALL', or 'ALT' """,
        validator=strict_discrete_set,
        values=['RIS', 'FALL', 'ALT']
    )

    trigger_coupling = Instrument.control(
        # good
        ":TRIGger:EDGE:COUPling?",
        """:TRIGger:EDGE:COUPling %s""",
        """ A string control that sets the coupling of the trigger:
        'DC', 'AC', 'LFREJ', 'HFREJ' """,
        validator=strict_discrete_set,
        values=['DC', 'AC', 'LFREJ', 'HFREJ']
    )

    impedance = Instrument.control(
        ':TRIGger:EDGE:IMPedance?',
          ":TRIGger:EDGE:IMPedance %s",
        """A string parameter that gets or sets the input impedance of the EXT 
        trigger channel""",
        validator=strict_discrete_set,
        values=['ONEM', 'FIFT', 'ONEMeg', 'FIFTY'],
    )

    trigger_edge_level = Instrument.control(
        #good
        ":TRIGger:EDGE:LEVel?'",
        """:TRIGger:EDGE:LEVel %.4E""",
        """ A float control that sets the trigger level in V, range is +-0.82 V""",
        validator=strict_range,
        values=[-0.82, 0.82]
    )


    def trigger_edge_source(self, channel):
        #good
        """
        Function to set the edge trigger source. Does not implement Digital
        Line. 
        :param channel: Integer corresponding to a given channel (0 is aux)
        :return:
        """
        if channel == 0:
            source = 'EX'
        elif channel in [1, 2, 3, 4, 5, 6, 7, 8]:
            source = 'C%d' % channel
        else:
            raise ValueError(f'{channel} not a valid trigger source')
        self.write(f""":TRIGger:EDGE:SOURce {source}""")


    def set_edge_trigger(self, source, level, slope):
        """
        Convenience function to set the scope trigger to edge, source to channel source at the specified level
        """
        self.trigger_mode = 'EDGE'
        self.trigger_edge_level = level
        self.trigger_edge_slope = slope
        self.trigger_edge_source(source)


    n_sequences = Instrument.control(
        ":ACQ:SEQ:COUN?",
        ":ACQ:SEQ:COUN %d",
        """Set the number of sequences in sequence mode"""
    )

    sequence_status = Instrument.control(
        ":ACQ:SEQ?",
        ":ACQ:SEQ %s",
        """Turns sequence mode on or off""",
        validator=strict_discrete_set,
        values=STR_BOOLS,
        map_values=True
    )
    


    def setup_sequence(self, sequence_on, n_sequences=1):
        """
        Turn sequence mode on or off with sequence_on = [True, False] and
        if True, specify the number of sequences to record. Memory depth is left
        to the scope to optimize. Note: turning sequence on or off will invoke an
        auto-calibrate.
        """
        if sequence_on:
            self.acquisition_type = 'NORM'
            self.wait_for_op()
            self.sequence_status = True
            self.n_sequences = n_sequences

        else:
            self.sequence_status = False

    def sequence_status_dict(self):
        """Returns the status of the sequencing mode on the oscillscope."""
    
        return {'is_on': self.sequence_status,
                 'n_sequences': int(self.n_sequences),
                'memdepth': float(self.acquisition_mdepth)}


    def clear_sweeps(self):
        self.write(""":ACQuire:CSWeep""")

    

    ###############
    # Acquisition #
    ###############

    interpolation = Instrument.control(
        ":ACQuire:INTerpolation?", ":ACQuire:INTerpolation %s",
        """Control of the interpolation mode of the scope. ON is sinc, OFF is linear""",
        validator=strict_discrete_set,
        values=['ON','OFF']
    )

    acquisition_memory_mode = Instrument.control(
        ":ACQuire:MMANagement?",
          ":ACQuire:MMANanagement %s",
        """Control of the memory mode of the oscilloscope.
        
        -AUTO mode maintain the maximum sampling rate, and
        automatically set the memory depth and sampling rate
        according to the time base.
        - FSRate mode is Fixed Samling Rate, maintain the
        specified sampling rate and automatically set the
        memory depth according to the time base.
        - FMDepth mode is Fixed Memory Depth, the
        oscilloscope automatically sets the sampling rate
        according to the storage depth and time base
        """,
        validator=strict_discrete_set,
        values=['AUTO', 'FSRate', 'FMDepth', 'FSR', 'FMD']
    )


    acquisition_mode = Instrument.control(
        ":ACQuire:MODE?",
          ":ACQuire:MODE %s",
        """Control of the acquisition mode of the oscilloscope.
        
        • YT mode plots amplitude (Y) vs. time (T)
        • XY mode plots channel X vs. channel Y, commonly
        referred to as a Lissajous curve
        • Roll mode plots amplitude (Y) vs. time (T) as in YT
        mode, but begins to write the waveforms from the
        right-hand side of the display. This is similar to a “strip
        chart” recording and is ideal for slow events that
        happen a few times/second.
        """,
        validator=strict_discrete_set,
        values=['YT', 'XY', 'ROLL']
    )

    acquisition_mdepth = Instrument.control(
        ":ACQuire:MDEPth?",
          ":ACQuire:MDEPth %s",
        """Control of the maximum memory depth of the oscilloscope.
        options are {2.5k|5k|25k|50k|250k|500k|2.5M|5M|12.5M|25M|
        50M|125M|250M|250M|500M}
        """,
        validator=strict_discrete_set,
        values=['2.5k','5k','25k','50k','250k''500k','2.5M','5M','12.5M','25M',
                '50M','125M','250M','250M','500M']
    )

    acquisition_nacq = Instrument.measurement(
        ":ACQuire:NUMAcq?",
        """The query returns the number of waveform acquisitions that have
            occurred since starting acquisition. This value is reset to zero
            when any acquisition,horizontal, or vertical arguments that affect
            the waveform are changed.""",
    )

    acquisition_srate = Instrument.control(
        ":ACQuire:SRATe?",
          ":ACQuire:SRATe %.4f",
        """Control of the sampling rate of the oscilloscope when in fixed sampling
        rate mode.
        """
    )

    average_n = Instrument.control(
        ":ACQuire:TYPE?",
        ":ACQuire:TYPE AVERage,%d",
        """Turns on averaging and sets to requested number of averages. Not available when in 
        sequence mode."""
    )

    acquisition_type = Instrument.control(
        ":ACQuire:TYPE?",
          ":ACQuire:TYPE %s",
        """Control of the acquisition type, self.average_n uses the same command to
        set the number of averages. In reality you should only use this to set and confirm
        that the type is NORM.
        """,
        validator=strict_discrete_set,
        values=['NORM']
    )

    run_mode = Instrument.control(
        ":TRIGger:MODE?", ":TRIGger:MODE %s",
        """Control of the instrument run state. Can be:
         NORM, SINGLE, AUTO""",
        validator=strict_discrete_set,
        values=['NORM', 'SINGLE', 'AUTO']
    )

    run_state = Instrument.measurement(
        ":TRIGger:STATUS?",
        """Returns the status of the scope. Can be Arm, Ready, Auto, Trig'd, Stop, Roll.
        Yes, you read that right, first letter capitalized, full word.""",
    )

    def run(self):
        #good
        """ Starts repetitive acquisitions. This is the same as pressing the Run key on the front panel."""
        self.write(':TRIG:RUN')

    def stop(self):
        #good
        """  Stops the acquisition. This is the same as pressing the Stop key on the front panel."""
        self.write(':TRIG:STOP')


    def single(self):
        #good
        """ Causes the instrument to acquire a single trigger of data.
        This is the same as pressing the Single key on the front panel. """
        self.run_mode = 'SINGLE'


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

    _waveform_source = Instrument.control(
        # good
        ":WAVeform:SOURce?", ":WAVeform:SOURce %s",
        """Source of the data to get in get_waveform. Not normally called by
        user. Can be {C<x>|F<x>|D<m>} where C is a channel, F is a function and
        D is a digital channel"""
    )

    _waveform_start = Instrument.control(
        # good
        ":WAVeform:STARt?", ":WAVeform:STARt %d",
        """Start of waveform, 1-indexed. Not normally called by user"""
    )

    _waveform_point = Instrument.control(
        # good
        ":WAVeform:POINt?", ":WAVeform:POINt %d",
        """How many points to transfer from the _waveform_start.
         Not normally called by user"""
    )

    _waveform_sparsing = Instrument.control(
        # good
        ":WAVeform:INTerval?", ":WAVeform:INTerval %d",
        """How many points between each point during data transfer. Also called sparsing.
         Not normally called by user"""
    )

    waveform_format = Instrument.control(
        #good
        ":WAVeform:WIDTh?", ":WAVeform:WIDTh %s",
        """ A string parameter that controls how the data is formatted when sent from the 
        oscilloscope.  "WORD" or "BYTE". Words are transmitted in big endian by default.
        These are 12 bit ADC's so if you choose byte, you better have good reason to throw away
        those extra four bits""",
        validator=strict_discrete_set,
        values=["WORD", "BYTE"],
    )


    @property
    def waveform_preamble(self):
        #good
        """ Get preamble information for the selected waveform source as a dict with the following keys:
            -'data_bytes' : the number of bytes transfered. If you request the full 12 bits of precision 
            be transfered this will always be double the number of actual points. However, the default is 
            to only transmit bytes, which returns a lower precision result but only 1 byte per point
            - 'point_num' : number of points transfered, see note above
            - 'fp' : the first point of the waveform, relevant if you are returning a subset of the total wf
            - 'sp' : sparsing factor for the data return
            - 'interval' : time distance between points, should be 1/sampling rate
            - 'delay' : time distance from the trigger point to the center of the acquisition window. I.e.
            a positive value means the trigger happens to the left of the center
            - 'probe' : probe attenuation factor
            - 'vdiv' : Volts per divsion
            - 'offset' : offset of the vertical scale,
            - 'code' : waveform data out / code * vdiv = actual signal,
            - 'tdiv' : time per division
           """
        return self._waveform_preamble()



    def waveform_data_word(self, source, sparsing=1):
        #good
        """ Get the block of sampled data points transmitted using the IEEE 488.2 arbitrary
        block data format. valid sources are C1, C2, C3, C4, F1-4, M1-4
        Sparsing is the Lecroy sparsing factor. If you want to keep every nth point,
        set sparsing to n-1. """
        # Other waveform formats raise UnicodeDecodeError
        self.waveform_format = "WORD"
        self._waveform_sparsing = sparsing
        self._waveform_source = source
        data = self.adapter.connection.query_binary_values(f":WAV:DATA?", datatype='h')

        return data
    
    def waveform_data_formatted(self, source, sparsing=1):
        """
        Get the full trace of the data and covert it to voltage, not just the integers the scope
        spits out.
        """
        data = self.waveform_data_word(source, sparsing)
        preamble = self.waveform_preamble

        formatted = np.array(data) / preamble["code"] * preamble['vdiv']
        return formatted


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
                errmsg = "Lecroy T3DSO: %s: %s" % (err[0], err[1])
                log.error(errmsg + "\n")
            else:
                break

    def clear_status(self):
        """ Clear device status. """
        self.write("*CLS")


    def factory_reset(self):
        """ Factory default setup, no user settings remain unchanged. """
        self.write("*RST")


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

        Unlike the MAUI-based lecroy scopes, we only get binary which needs to be decoded
        according to a table on page 725 of the programming manual. As such, we need to
        read_raw and then unpack the slices with the struct library according to their dtype.


        """
        if channel is not None:
            self._waveform_source=channel
        self.write(":WAV:PREamble?")
        recv_raw = self.adapter.connection.read_raw()
        # there is always a preable of #9 then 9 digits representing the number
        # of bytes. Most of those are 0's as the preamble is like 356 bytes.
        # This is the standard format for binary transfer. I could be smart
        # and read the #9 and then add the 9 to the first two bytes, but I
        # didnt'. I hope no one pays for this sin later. -Neal
        recv = recv_raw[recv_raw.find(b'#')+11:]
        WAVE_ARRAY_1 = recv[60:63+1]
        wave_array_count = recv[116:119+1]
        first_point = recv[132:135+1]
        sp = recv[136:139+1]
        v_scale = recv[156:159+1]
        v_offset = recv[160:163+1]
        horiz_interval = recv[176:179+1]
        code_per_div = recv[164:167 + 1]
        delay = recv[180:187+1]
        tdiv = recv[324:325+1]
        probe = recv[328:331+1]
        probe = struct.unpack('f',probe)[0]
        tdiv_index = struct.unpack('h',tdiv)[0]
        horiz_interval = struct.unpack('f',horiz_interval)[0]
        nearestlog = int(np.log10(horiz_interval))
        rational = horiz_interval / 10**(nearestlog)
        rational = np.round(rational, 7)
        horiz_interval = rational * 10**(nearestlog)
        ddict={
            'data_bytes' : struct.unpack('i',WAVE_ARRAY_1)[0],
            'point_num' : struct.unpack('i',wave_array_count)[0],
            'fp' : struct.unpack('i',first_point)[0],
            'sp' : struct.unpack('i',sp)[0],
            'xincrement' : horiz_interval,
            'delay' : struct.unpack('d',delay)[0],
            'probe' : probe,
            'vdiv' : np.round(struct.unpack('f',v_scale)[0], 8)*probe,
            'offset' : struct.unpack('f',v_offset)[0]*probe,
            'code' : struct.unpack('f', code_per_div)[0],
            'tdiv' : tdiv_enum[tdiv_index]}
        return ddict