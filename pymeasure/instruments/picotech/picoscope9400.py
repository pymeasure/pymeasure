#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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
from pymeasure.adapters.picoscope9400com import COMAdapter

BOOLS = {True: 'ON', False: 'OFF'}

class Channel():
    """ Implementation of a Picoscope9400 Oscilloscope channel.
    Implementation modeled on Channel object of Tektronix AFG3152C instrument. """

    bwlimit = Instrument.control(
        "Band?", "Band %s",
        """ A string parameter that sets the bandwidth of the channel. Options are:
        "full", "middle", "narrow""",
        validator=strict_discrete_set,
        values=['full', 'middle', 'narrow'],
    )

    display = Instrument.control(
        "DISPlay?", "DISPlay %s",
        """ A boolean parameter that toggles the display.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    offset = Instrument.control(
        "OFFSet?", "OFFSet %g",
        """ A float parameter to set value that is represented at center of screen in 
        Volts. From [-1,1]""",
        validator=strict_range,
        values=[-1,1]
    )

    scale = Instrument.control(
        "SCALe?", "SCALe %g",
        """ A float parameter that specifies the vertical scale V/div. From [0.01, .25]""",
        #validator=strict_range,
        #values = [0.01, 0.25]
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values("Ch%d:%s" % (
            self.number, command), **kwargs)

    def ask(self, command):
        self.instrument.ask("Ch%d:%s" % (self.number, command))

    def write(self, command):
        self.instrument.write("Ch%d:%s" % (self.number, command))



class Picoscope9400(Instrument):
    """ Represents the Picotech Picoscope 9400 series SRXTO Oscilloscope interface for interacting
    with the instrument.
    Refer to the Picoscope 9400 series SRXTO Oscilloscope Programmer's Guide
     (https://www.picotech.com/download/manuals/picoscope-9400-series-programmers-guide.pdf) for further details about
    using the lower-level methods to interact directly with the scope.
    .. code-block:: python

        scope = Picoscope9400(resource)
        scope.autoscale()
        ch1_data_array, ch1_preamble = scope.download_data(source="channel1", points=2000)
        # ...
        scope.shutdown()
    Known issues:

    - The digitize command will be completed before the operation is. May lead to
      VI_ERROR_TMO (timeout) occuring when sending commands immediately after digitize.
      Current fix: if deemed necessary, add delay between digitize and follow-up command
      to scope.
    """



    def __init__(self, adapter, **kwargs):
        if isinstance(adapter, str):
            adapter = COMAdapter(adapter)
        super(Picoscope9400, self).__init__(
            adapter, "Picotech Picscope9400 SXRTO Oscilloscope", **kwargs
        )
        self.header = False
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)
        self.ch3 = Channel(self, 3)
        self.ch4 = Channel(self, 4)

    header = Instrument.control(
        "Header?", "Header %s",
        """ A string parameter that sets whether commands return with a header.""",
        validator=strict_discrete_set,
        values=BOOLS,
        map_values=True
    )

    #################
    # Channel setup #
    #################

    def autoscale(self):
        """ Autoscale displayed channels. """
        self.write("*Autoscale")


    ##################
    # Timebase Setup #
    ##################

    timebase_mode = Instrument.control(
        "Instr:TimeBase:SampleModeSet?", "Instr:TimeBase:SampleModeSet %s",
        """ A string parameter that sets the current time base. Can be "realtime", "randomet", "roll" or "auto".""",
        validator=strict_discrete_set,
        values={"realtime": "REALTIME", "randomet": "RANDOMET", "roll": "ROLL", "auto": "AUTO"},
        map_values=True
    )

    timebase_primary_priority = Instrument.control(
        "TB:Priority:Primary?", "TB:Priority:Primary %s",
        """ A string parameter that sets the primary priority of the timebase. Options are 
        "recordlength", "samplerate", or "horizontalscale". Set the secondary priority with
         timebase_secondary_priority""",
        validator=strict_discrete_set,
        values={"recordlength": "RECLENGTH", "samplerate": "SMPLRATE","horizontalscale": "HORSCALE"},
        map_values=True
    )

    timebase_secondary_priority = Instrument.control(
        "TB:Priority:Secondary?", "TB:Priority:Secondary %s",
        """ A string parameter that sets the secondary priority of the timebase. Options are 
        "recordlength", "samplerate", or "horizontalscale". Set the primary priority with
         timebase_primary_priority""",
        validator=strict_discrete_set,
        values={"recordlength": "RECLENGTH", "samplerate": "SMPLRATE","horizontalscale": "HORSCALE"},
        map_values=True
    )

    timebase_scale = Instrument.control(
        "Instr:TimeBase:ScaleT?", "Instr:TimeBase:ScaleT %g",
        """ A float parameter that sets the horizontal scale (units per division) in seconds 
        for the main window. Range is 50e-12 to 1000 se for the 5 GHz scopes and 20e-12 to 1000 s for
         the 16 GHz scopes."""
    )

    timebase_samplerate = Instrument.control(
        "Instr:TimeBase:SmplRate?", "Instr:TimeBase:SmplRate %g",
        """ A float parameter that sets the sample rate in points per second. Lower limit is 125e-3.
         Upper limit is 1e12 for the 5 GHz model, 2.5e12 for the 16 GHz model."""
    )

    timebase_record_length = Instrument.control(
        "Instr:TimeBase:RecLen?", "Instr:TimeBase:RecLen %g",
        """ A float parameter that sets the number of points in a given waveform recording. 
        Can run from 50 to 250,000."""
    )


    timebase_delay = Instrument.control(
        "TB:Delay?", "TB:Delay",
        """ A float parameter that sets the time interval in seconds between the trigger 
        event and when the record is recorded. Can range from 0 to 4.28 s"""
    )




    ###############
    # Acquisition #
    ###############

    acquisition_mode = Instrument.control(
        "Acq:Mode?", "Acq:Mode %s",
        """ A string parameter that sets the acquisition mode. Options are "sample", "average", "envminmax",
         "envmin", "envmax". In realtime sampling mode additional options are: "peakdetect", "highres", "segmented".""",
        validator=strict_discrete_set,
        values={"sample": 'SAMPLE', "average":'AVERAGE', "envminmax":'ENVMINMAX',
         "envmin":'ENVMIN', "envmax":'ENVMAX', "peakdetect":'PEAKDETECT', "highres":'HIGHRES', "segmented":'SEGMENTED'},
        map_values=True
    )

    acquisition_navg = Instrument.control(
        "Acq:NAvg?", "Acq:NAvg %d",
        """ An integer parameter that sets the number of averages to take if averaging is enabled. Range is 1-4096.""",
        validator=strict_range,
        values=[1, 4096],
    )

    acquisition_nenv = Instrument.control(
        "Acq:NEnv?", "Acq:NEnv %d",
        """ An integer parameter that sets the number of traces to build an envelope if enveloping is enabled.
         Range is 2-8192. Enveloping constructucts waveforms based on the min or max of acquired traces according to
         how the envelope mode is specified""",
        validator=strict_range,
        values=[2, 8192],
    )

    acquisition_run_until = Instrument.control(
        "Acq:RunUntil?", "Acq:RunUntil %s",
        """ A string parameter that sets when acquisition will terminate: "stopbutton" or "nacq".""",
        validator=strict_discrete_set,
        values={"stopbutton": "STOPBTN", "nacq": "NACQ"},
        map_values=True
    )

    acquisition_nacq = Instrument.control(
        "Acq:NAcq?", "Acq:NAcq %d",
        """ An integer parameter that sets the number of signals to acquire before termination if 
        acquisition_run_until is nacq""",
        validator=strict_range,
        values=[1, 65535]
    )

    ###########
    # Trigger #
    ###########

    trigger_position = Instrument.control(
        "TB:TrigPos?", "TB:TrigPos %g",
        """ Float parameter the trigger location in the waveform as a percent of the wf. Range is 
        0 to 100%, 50% is in the center."
         """
    )

    trigger_source = Instrument.control(
        "Trig:Analog:Source?", "Trig:Analog:Source %s",
        """ String parameter that sets or queries the trigger source options are "CHn" where n = 1,2,3,4}
         """,
        validator=strict_discrete_set,
        values=['CH1', 'CH2', 'CH3', 'CH4']
    )

    trigger_type = Instrument.control(
        "Trig:Analog:Style?", "Trig:Analog:Style %s",
        """ A string parameter that sets trigger type. Can be "edge", "divider", 
        "clkrecovery", "intclock", or "extprescal".
         """,
        validator=strict_discrete_set,
        values={"edge": "EDGE", "divider":'DIVIDER', "clkrecovery": "CLKRECOVERY", "intclock":'INTCLOCK',
                "extprescale":'EXTPRESCAL'},
        map_values=True
    )

    def set_trigger_level(self, channel, level):
        self.write(f'Trig:Analog:Ch{channel}:Level {level}')

    def get_trigger_level(self, channel):
        return self.ask(f'Trig:Analog:Ch{channel}:Level?')

    def set_trigger_slope(self, channel, slopetype):
        """slopetype = [Pos, Neg, or BiSlope]"""
        self.write(f'Trig:Analog:Ch{channel}:Slope {slopetype}')

    def get_trigger_slope(self, channel):
        return self.ask(f'Trig:Analog:Ch{channel}:Slope?')

    trigger_mode = Instrument.control(
        "Trig:Mode?", "Trig:Mode %s",
        """ A string parameter that sets trigger mode. Can be 'free' or 'triggered'.
         """,
        validator=strict_discrete_set,
        values={"free": "FREE", "triggered": "TRIG"},
        map_values=True
    )


    def run(self):
        """ Starts repetitive acquisitions. This is the same as pressing the Run key on the front panel."""
        self.write("*RunControl Run")

    def stop(self):
        """  Stops the acquisition. This is the same as pressing the Stop key on the front panel."""
        self.write("*RunControl Stop")

    def single(self):
        """ Causes the instrument to acquire a single trigger of data.
        This is the same as pressing the Single key on the front panel. """
        self.write("*RunControl Single")

    scope_status = Instrument.measurement(
        '*RunControl?',
        """Return the status of the scope (Run, Stop, Single)"""
    )

    ############
    # Waveform #
    ############

    waveform_source = Instrument.control(
        "Wfm:Source?", "Wfm:Source %s",
        """ A string parameter that selects the analog channel, function, or reference waveform 
        to be used as the source for the waveform methods. Can be:
        'Ch1', "Ch2", "Ch3", "Ch4", 'F1', 'F2', 'F3','F4','M1', 'M2', 'M3', 'M4'.
        TODO implement Digital pin sources and the MATH sources""",
        validator=strict_discrete_set,
        values=['Ch1', "Ch2", "Ch3", "Ch4", 'F1', 'F2', 'F3','F4','M1', 'M2', 'M3', 'M4'],
    )

    waveform_points = Instrument.measurement(
        "Wfm:Preamb:Poin?",
        """ Returns the number of points in waveform_data """,
    )

    waveform_xinc = Instrument.measurement(
        "Wfm:Preamb:XInc?",
        """ Returns the x-axis increment of the waveform_data """,
    )

    waveform_xorigin = Instrument.measurement(
        "Wfm:Preamb:XOrg?",
        """ Returns the x-axis value of the first point of the waveform_data """,
    )

    waveform_xunit = Instrument.measurement(
        "Wfm:Preamb:XU?",
        """ Returns the x-axis physical units of the waveform_data """,
    )

    waveform_yunit = Instrument.measurement(
        "Wfm:Preamb:YU?",
        """ Returns the y-axis physical units of the waveform_data """,
    )

    @property
    def waveform_preamble(self):
        """ Get preamble information for the selected waveform source as a dict with the following keys:
            - "points": nb of data points transferred (int)
            - "xincrement": time difference between data points (float)
            - "xorigin": first data point in memory (float)
            - "xunit": x-axis units (str)
            - "yunit: y-axis units (str)"""
        return self._waveform_preamble()

    @property
    def waveform_data(self):
        """ Get the data from a previously specified channel."""
        # Other waveform formats raise UnicodeDecodeError
        header = self.header
        if header:
            self.header = False
        data = self.ask("Wfm:Data?")
        data = np.array([float(d) for d in data.split(',')])
        self.header = header
        return data


    def _waveform_preamble(self):
        """
        Reads waveform preamble and converts it to a more convenient dict of values.
        """
        vals = self.ask(":waveform:preamble?")
        # Get values to dict
        vals_dict = {'points': self.waveform_points,
                     'xincrement': self.waveform_xinc,
                     'xorigin': self.waveform_xorigin,
                     'xunit': self.waveform_xunit,
                     'yunit': self.waveform_yunit,
                     }
        return vals_dict

    def clear_status(self):
        """ Compatibility method. Does nothing. """
        pass
