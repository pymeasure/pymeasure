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

import logging
import time
from warnings import warn

import numpy as np

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.errors import RangeException
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from .buffer import KeithleyBuffer

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley6221(KeithleyBuffer, SCPIMixin, Instrument):
    """ Represents the Keithley 6221 AC and DC current source and provides a
    high-level interface for interacting with the instrument.

    .. code-block:: python

        keithley = Keithley6221("GPIB::1")
        keithley.clear()

        # Use the keithley as an AC source
        keithley.waveform_function = "square"   # Set a square waveform
        keithley.waveform_amplitude = 0.05      # Set the amplitude in Amps
        keithley.waveform_offset = 0            # Set zero offset
        keithley.source_compliance = 10         # Set compliance (limit) in V
        keithley.waveform_dutycycle = 50        # Set duty cycle of wave in %
        keithley.waveform_frequency = 347       # Set the frequency in Hz
        keithley.waveform_ranging = "best"      # Set optimal output ranging
        keithley.waveform_duration_cycles = 100 # Set duration of the waveform

        # Link end of waveform to Service Request status bit
        keithley.operation_event_enabled = 128  # OSB listens to end of wave
        keithley.srq_event_enabled = 128        # SRQ listens to OSB

        keithley.waveform_arm()                 # Arm (load) the waveform

        keithley.waveform_start()               # Start the waveform

        keithley.adapter.wait_for_srq()         # Wait for the pulse to finish

        keithley.waveform_abort()               # Disarm (unload) the waveform

        keithley.shutdown()                     # Disables output

    """

    def __init__(self, adapter, name="Keithley 6221 SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs)

    ##########
    # OUTPUT #
    ##########

    source_enabled = Instrument.control(
        "OUTPut?", "OUTPut %d",
        """A boolean property that controls whether the source is enabled, takes
        values True or False. The convenience methods :meth:`~.Keithley6221.enable_source` and
        :meth:`~.Keithley6221.disable_source` can also be used.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    source_delay = Instrument.control(
        ":SOUR:DEL?", ":SOUR:DEL %g",
        """ A floating point property that sets a manual delay for the source
        after the output is turned on before a measurement is taken. When this
        property is set, the auto delay is turned off. Valid values are
        between 1e-3 [seconds] and 999999.999 [seconds].""",
        validator=truncated_range,
        values=[1e-3, 999999.999],
    )

    output_low_grounded = Instrument.control(
        ":OUTP:LTE?", "OUTP:LTE %d",
        """ A boolean property that controls whether the low output of the triax
        connection is connected to earth ground (True) or is floating (False). """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    ##########
    # SOURCE #
    ##########

    source_current = Instrument.control(
        ":SOUR:CURR?", ":SOUR:CURR %g",
        """ A floating point property that controls the source current
        in Amps. """,
        validator=truncated_range,
        values=[-0.105, 0.105]
    )
    source_compliance = Instrument.control(
        ":SOUR:CURR:COMP?", ":SOUR:CURR:COMP %g",
        """A floating point property that controls the compliance of the current
        source in Volts. valid values are in range 0.1 [V] to 105 [V].""",
        validator=truncated_range,
        values=[0.1, 105])
    source_range = Instrument.control(
        ":SOUR:CURR:RANG?", ":SOUR:CURR:RANG:AUTO 0;:SOUR:CURR:RANG %g",
        """ A floating point property that controls the source current
        range in Amps, which can take values between -0.105 A and +0.105 A.
        Auto-range is disabled when this property is set. """,
        validator=truncated_range,
        values=[-0.105, 0.105]
    )
    source_auto_range = Instrument.control(
        ":SOUR:CURR:RANG:AUTO?", ":SOUR:CURR:RANG:AUTO %d",
        """ A boolean property that controls the auto range of the current source.
        Valid values are True or False. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    ##################
    # WAVE FUNCTIONS #
    ##################

    waveform_function = Instrument.control(
        ":SOUR:WAVE:FUNC?", ":SOUR:WAVE:FUNC %s",
        """ A string property that controls the selected wave function. Valid
        values are "sine", "ramp", "square", "arbitrary1", "arbitrary2",
        "arbitrary3" and "arbitrary4". """,
        values={
            "sine": "SIN",
            "ramp": "RAMP",
            "square": "SQU",
            "arbitrary1": "ARB1",
            "arbitrary2": "ARB2",
            "arbitrary3": "ARB3",
            "arbitrary4": "ARB4",
        },
        map_values=True
    )

    waveform_frequency = Instrument.control(
        ":SOUR:WAVE:FREQ?", ":SOUR:WAVE:FREQ %g",
        """A floating point property that controls the frequency of the
        waveform in Hertz. Valid values are in range 1e-3 to 1e5. """,
        validator=truncated_range,
        values=[1e-3, 1e5]
    )
    waveform_amplitude = Instrument.control(
        ":SOUR:WAVE:AMPL?", ":SOUR:WAVE:AMPL %g",
        """A floating point property that controls the (peak) amplitude of the
        waveform in Amps. Valid values are in range 2e-12 to 0.105. """,
        validator=truncated_range,
        values=[2e-12, 0.105]
    )
    waveform_offset = Instrument.control(
        ":SOUR:WAVE:OFFS?", ":SOUR:WAVE:OFFS %g",
        """A floating point property that controls the offset of the waveform
        in Amps. Valid values are in range -0.105 to 0.105. """,
        validator=truncated_range,
        values=[-0.105, 0.105]
    )
    waveform_dutycycle = Instrument.control(
        ":SOUR:WAVE:DCYC?", ":SOUR:WAVE:DCYC %g",
        """A floating point property that controls the duty-cycle of the
        waveform in percent for the square and ramp waves. Valid values are in
        range 0 to 100. """,
        validator=truncated_range,
        values=[0, 100]
    )
    waveform_duration_time = Instrument.control(
        ":SOUR:WAVE:DUR:TIME?", ":SOUR:WAVE:DUR:TIME %g",
        """A floating point property that controls the duration of the
        waveform in seconds. Valid values are in range 100e-9 to 999999.999.
        """,
        validator=truncated_range,
        values=[100e-9, 999999.999]
    )
    waveform_duration_cycles = Instrument.control(
        ":SOUR:WAVE:DUR:CYCL?", ":SOUR:WAVE:DUR:CYCL %g",
        """A floating point property that controls the duration of the
        waveform in cycles. Valid values are in range 1e-3 to 99999999900.
        """,
        validator=truncated_range,
        values=[1e-3, 99999999900]
    )

    def waveform_duration_set_infinity(self):
        """ Set the waveform duration to infinity.
        """
        self.write(":SOUR:WAVE:DUR:TIME INF")

    waveform_ranging = Instrument.control(
        ":SOUR:WAVE:RANG?", ":SOUR:WAVE:RANG %s",
        """ A string property that controls the source ranging of the
        waveform. Valid values are "best" and "fixed". """,
        values={"best": "BEST", "fixed": "FIX"},
        map_values=True,
    )
    waveform_use_phasemarker = Instrument.control(
        ":SOUR:WAVE:PMAR:STAT?", ":SOUR:WAVE:PMAR:STAT %s",
        """ A boolean property that controls whether the phase marker option
        is turned on or of. Valid values True (on) or False (off). Other
        settings for the phase marker have not yet been implemented.""",
        values={True: 1, False: 0},
        map_values=True,
    )
    waveform_phasemarker_phase = Instrument.control(
        ":SOUR:WAVE:PMAR?", ":SOUR:WAVE:PMAR %g",
        """ A numerical property that controls the phase of the phase marker.""",
        validator=truncated_range,
        values=[-180, 180],
    )
    waveform_phasemarker_line = Instrument.control(
        ":SOUR:WAVE:PMAR:OLIN?", ":SOUR:WAVE:PMAR:OLIN %d",
        """ A numerical property that controls the line of the phase marker.""",
        validator=truncated_range,
        values=[1, 6],
    )

    def waveform_arm(self):
        """ Arm the current waveform function. """
        self.write(":SOUR:WAVE:ARM")

    def waveform_start(self):
        """ Start the waveform output. Must already be armed """
        self.write(":SOUR:WAVE:INIT")

    def waveform_abort(self):
        """ Abort the waveform output and disarm the waveform function. """
        self.write(":SOUR:WAVE:ABOR")

    def define_arbitary_waveform(self, datapoints, location=1):
        """ Define the data points for the arbitrary waveform and copy the
        defined waveform into the given storage location.

        :param datapoints: a list (or numpy array) of the data points; all
            values have to be between -1 and 1; 100 points maximum.
        :param location: integer storage location to store the waveform in.
            Value must be in range 1 to 4.
        """

        # Check validity of parameters
        if not isinstance(datapoints, (list, np.ndarray)):
            raise ValueError("datapoints must be a list or numpy array")
        elif len(datapoints) > 100:
            raise ValueError("datapoints cannot be longer than 100 points")
        elif not all([x >= -1 and x <= 1 for x in datapoints]):
            raise ValueError("all data points must be between -1 and 1")

        if location not in [1, 2, 3, 4]:
            raise ValueError("location must be in [1, 2, 3, 4]")

        # Make list of strings
        datapoints = [str(x) for x in datapoints]
        data = ", ".join(datapoints)

        # Write the data points to the Keithley 6221
        self.write(":SOUR:WAVE:ARB:DATA %s" % data)

        # Copy the written data to the specified location
        self.write(":SOUR:WAVE:ARB:COPY %d" % location)

        # Select the newly made arbitrary waveform as waveform function
        self.waveform_function = "arbitrary%d" % location

    def enable_source(self):
        """ Enables the source of current or voltage depending on the
        configuration of the instrument. """
        self.write("OUTPUT ON")

    def disable_source(self):
        """ Disables the source of current or voltage depending on the
        configuration of the instrument. """
        self.write("OUTPUT OFF")

    def beep(self, frequency, duration):
        """ Sounds a system beep.

        :param frequency: A frequency in Hz between 65 Hz and 2 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.write(f":SYST:BEEP {frequency:g}, {duration:g}")

    def triad(self, base_frequency, duration):
        """ Sounds a musical triad using the system beep.

        :param base_frequency: A frequency in Hz between 65 Hz and 1.3 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.beep(base_frequency, duration)
        time.sleep(duration)
        self.beep(base_frequency * 5.0 / 4.0, duration)
        time.sleep(duration)
        self.beep(base_frequency * 6.0 / 4.0, duration)

    display_enabled = Instrument.control(
        ":DISP:ENAB?", ":DISP:ENAB %d",
        """ A boolean property that controls whether or not the display of the
        sourcemeter is enabled. Valid values are True and False. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    @property
    def error(self):
        warn("Deprecated to use `error`, use `next_error` instead.", FutureWarning)
        return self.next_error

    def reset(self):
        """ Resets the instrument and clears the queue.  """
        self.write("status:queue:clear;*RST;:stat:pres;:*CLS;")

    def trigger(self):
        """ Executes a bus trigger, which can be used when
        :meth:`~.trigger_on_bus` is configured.
        """
        return self.write("*TRG")

    def trigger_immediately(self):
        """ Configures measurements to be taken with the internal
        trigger at the maximum sampling rate.
        """
        self.write(":ARM:SOUR IMM;:TRIG:SOUR IMM;")

    def trigger_on_bus(self):
        """ Configures the trigger to detect events based on the bus
        trigger, which can be activated by :meth:`~.trigger`.
        """
        self.write(":ARM:SOUR BUS;:TRIG:SOUR BUS;")

    def set_timed_arm(self, interval):
        """ Sets up the measurement to be taken with the internal
        trigger at a variable sampling rate defined by the interval
        in seconds between sampling points
        """
        if interval > 99999.99 or interval < 0.001:
            raise RangeException("Keithley 6221 can only be time"
                                 " triggered between 1 mS and 1 Ms")
        self.write(":ARM:SOUR TIM;:ARM:TIM %.3f" % interval)

    def trigger_on_external(self, line=1):
        """ Configures the measurement trigger to be taken from a
        specific line of an external trigger

        :param line: A trigger line from 1 to 4
        """
        cmd = ":ARM:SOUR TLIN;:TRIG:SOUR TLIN;"
        cmd += ":ARM:ILIN %d;:TRIG:ILIN %d;" % (line, line)
        self.write(cmd)

    def output_trigger_on_external(self, line=1, after='DEL'):
        """ Configures the output trigger on the specified trigger link
        line number, with the option of supplying the part of the
        measurement after which the trigger should be generated
        (default to delay, which is right before the measurement)

        :param line: A trigger line from 1 to 4
        :param after: An event string that determines when to trigger
        """
        self.write(":TRIG:OUTP %s;:TRIG:OLIN %d;" % (after, line))

    def disable_output_trigger(self):
        """ Disables the output trigger for the Trigger layer
        """
        self.write(":TRIG:OUTP NONE")

    def shutdown(self):
        """ Disables the output. """
        log.info("Shutting down %s." % self.name)
        self.disable_source()
        super().shutdown()

    ###############
    # Status bits #
    ###############

    measurement_event_enabled = Instrument.control(
        ":STAT:MEAS:ENAB?", ":STAT:MEAS:ENAB %d",
        """ An integer value that controls which measurement events are
        registered in the Measurement Summary Bit (MSB) status bit. Refer to
        the Model 6220/6221 Reference Manual for more information about
        programming the status bits.
        """,
        cast=int,
        validator=truncated_range,
        values=[0, 65535],
    )

    operation_event_enabled = Instrument.control(
        ":STAT:OPER:ENAB?", ":STAT:OPER:ENAB %d",
        """ An integer value that controls which operation events are
        registered in the Operation Summary Bit (OSB) status bit. Refer to
        the Model 6220/6221 Reference Manual for more information about
        programming the status bits.
        """,
        cast=int,
        validator=truncated_range,
        values=[0, 65535],
    )

    questionable_event_enabled = Instrument.control(
        ":STAT:QUES:ENAB?", ":STAT:QUES:ENAB %d",
        """ An integer value that controls which questionable events are
        registered in the Questionable Summary Bit (QSB) status bit. Refer to
        the Model 6220/6221 Reference Manual for more information about
        programming the status bits.
        """,
        cast=int,
        validator=truncated_range,
        values=[0, 65535],
    )

    standard_event_enabled = Instrument.control(
        "ESE?", "ESE %d",
        """ An integer value that controls which standard events are
        registered in the Event Summary Bit (ESB) status bit. Refer to
        the Model 6220/6221 Reference Manual for more information about
        programming the status bits.
        """,
        cast=int,
        validator=truncated_range,
        values=[0, 65535],
    )

    srq_event_enabled = Instrument.control(
        "*SRE?", "*SRE %d",
        """ An integer value that controls which event registers trigger the
        Service Request (SRQ) status bit. Refer to the Model 6220/6221
        Reference Manual for more information about programming the status
        bits.
        """,
        cast=int,
        validator=truncated_range,
        values=[0, 255],
    )

    measurement_events = Instrument.measurement(
        ":STAT:MEAS?",
        """ An integer value that reads which measurement events have been
        registered in the Measurement event registers. Refer to the Model
        6220/6221 Reference Manual for more information about programming
        the status bits. Reading this value clears the register.
        """,
        cast=int,
    )

    operation_events = Instrument.measurement(
        ":STAT:OPER?",
        """ An integer value that reads which operation events have been
        registered in the Operation event registers. Refer to the Model
        6220/6221 Reference Manual for more information about programming
        the status bits. Reading this value clears the register.
        """,
        cast=int,
    )

    questionable_events = Instrument.measurement(
        ":STAT:QUES?",
        """ An integer value that reads which questionable events have been
        registered in the Questionable event registers. Refer to the Model
        6220/6221 Reference Manual for more information about programming
        the status bits. Reading this value clears the register.
        """,
        cast=int,
    )

    standard_events = Instrument.measurement(
        "*ESR?",
        """ An integer value that reads which standard events have been
        registered in the Standard event registers. Refer to the Model
        6220/6221 Reference Manual for more information about programming
        the status bits. Reading this value clears the register.
        """,
        cast=int,
    )
