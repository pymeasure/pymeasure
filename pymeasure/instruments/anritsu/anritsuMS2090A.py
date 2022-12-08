#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set,
    truncated_discrete_set,
    truncated_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AnritsuMS2090A(Instrument):
    """Anritsu MS2090A Handheld Spectrum Analyzer."""

    def __init__(self, adapter, **kwargs):
        """Constructor."""
        self.analysis_mode = None
        super().__init__(
            adapter, name="Anritsu MS2090A Handheld Spectrum Analyzer", **kwargs)

    ####################################
    #              GPS                 #
    ####################################

    gps_full = Instrument.measurement(
        "FETCh:GPS:FULL?",
        '''
        Thiscommandreturnsthetimestamp,latitude,longitude,altitude,andsatellitecountof the device. The response is a comma-delimited ASCII response of one of the following forms: NO FIX or GOOD FIX,<timestamp>,<latitude>,<longitude>,<altitude>,<satellites>
        If no GPS fix is currently available, the first response form (NO FIX) is returned.
        If the GPS does have a fix, the second response form (GOOD FIX) is returned.
        <timestamp> is in ISO8601 format. The timestamp provides the 24-hour time, and will include the year/date and/or UTC offset if the hardware supports it. If no UTC offset is provided, the time is in UTC time.
        <latitude> and <longitude> are specified in decimal degrees.
        <altitude> specifies the current altitude relative to mean sea level, in meters.
        <satellites> specifies an integer count of the number of satellites currently used in the fix.
        '''
    )

    gps_all = Instrument.measurement(
        "FETCh:GPS:ALL?",
        '''
        This command returns the fix timestamp, latitude, longitude, altitude and information on the satellites used for the last fix and the GNSS systems they are from. The response is in JSON format in the one of the following forms: {"fix":"GPS OFF"}
        or {"fix":"GOOD FIX","timestamp":<timestamp>,"latitude":<latitude>,"longitude":<longitude>,"altitude": <altitude>, "satellitesUsed":<satellitesUsed>,"satellites":[ {"name":"GPS","count":x}, {"name":"Galileo","count":x}, {"name":"GLONASS","count":x}, {"name":"BeiDou","count":x}]} <timestamp> is in ISO8601 format. The timestamp provides the 24-hour time, and will include the year/date and/or UTC offset if the hardware supports it. If no UTC offset is provided, the time is in UTC time.
        <latitude> and <longitude> are specified in decimal degrees.
        <altitude> specifies the current altitude relative to mean sea level, in meters.
        All satellite systems will be present with a count of 0 if they are not used in the fix.
        '''
    )

    gps = Instrument.measurement(
        ":FETCh:GPS?",
        '''
        This command returns the timestamp, latitude, and longitude of the device. The response is a comma-delimited ASCII response of one of the following forms: NO FIX or GOOD FIX,<timestamp>,<latitude>,<longitude>
        If no GPS fix is currently available, the first response form (NO FIX) is returned.
        If the GPS does have a fix, the second response form (GOOD FIX) is returned.
        <timestamp> is in ISO8601 format. The timestamp provides the 24-hour time, and will include the year/date and/or UTC offset if the hardware supports it. If no UTC offset is provided, the time is in UTC time.
        <latitude> and <longitude> are specified in decimal degrees.
        '''
    )

    gps_last = Instrument.measurement(
        ":FETCh:GPS:LAST?",
        '''
        This command returns the timestamp, latitude, longitude, and altitude of the last fixed GPS result. The response is a comma-delimited ASCII response of one of the following forms: NO FIX or GOOD FIX,<timestamp>,<latitude>,<longitude>,<altitude> If a GPS fix has never been acquired, the first response form (NO FIX) is returned.
        If a GPS fix was previously acquired, the second response form (GOOD FIX) is returned.
        <timestamp> is in ISO8601 format. The timestamp provides the 24-hour time, and will include the year/date and/or UTC offset if the hardware supports it. If no UTC offset is provided, the time is in UTC time.
        <latitude> and <longitude> are specified in decimal degrees.
        <altitude> specifies the current altitude relative to mean sea level, in meters.
        ''',
    )

    ####################################
    # Spectrum Parameters - Wavelength #
    ####################################

    frequency_center = Instrument.control(
        "FREQuency:CENTer?", "FREQuency:CENTer %g Hz",
        "Sets the center frequency in Hz",
        validator=truncated_range,
        values=[-99999999995, 299999999995],
    )

    frequency_offset = Instrument.control(
        "FREQuency:OFFSet?", "FREQuency:OFFSet %g Hz",
        "Sets the frequency offset in Hz",
        validator=truncated_range,
        values=[-10000000000, 10000000000],
    )

    frequency_span = Instrument.control(
        "FREQuency:SPAN?", "FREQuency:SPAN %g Hz",
        "Sets the frequency span in Hz",
        validator=truncated_range,
        values=[10, 400000000000],
    )

    frequency_span_full = Instrument.control(
        "","FREQuency:SPAN:FULL",
        "Sets the frequency span to full span"
    )

    frequency_span_last = Instrument.control(
        "","FREQuency:SPAN:LAST"
        "Sets the frequency span to the previous span value."
    )

    frequency_start = Instrument.control(
        "FREQuency:STARt?", "FREQuency:STARt %g Hz",
        "Sets the start frequency in Hz",
        validator=truncated_range,
        values=[-100000000000, 299999999990],
    )

    frequency_step = Instrument.control(
        ":FREQuency:STEP?", ":FREQuency:STEP %g Hz",
        "Set or query the step size to gradually increase or decrease frequency values in Hz",
        validator=truncated_range,
        values=[0.1, 1000000000],
    )

    frequency_stop = Instrument.control(
        "FREQuency:STOP?", "FREQuency:STOP %g Hz",
        "Sets the start frequency in Hz",
        validator=truncated_range,
        values=[-99999999990, 300000000000],
    )

    ##########################
    #  Data Memory Commands  #
    ##########################

    data_memory_select = Instrument.control(
        "TTP?", "TTP %s",
        "Memory Data Select.",
        validator=strict_discrete_set,
        values=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    )

    def repeat_sweep(self, n=20, delay=0.5):
        """Perform a single sweep and wait for completion."""
        log.debug("Performing a repeat Spectrum Sweep")
        self.clear()
        self.write('SRT')
        self.wait_for_sweep(n=n, delay=delay)
