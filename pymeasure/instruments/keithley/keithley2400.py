#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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

from pymeasure.instruments import Instrument, RangeException
from pymeasure.adapters import PrologixAdapter
from pymeasure.instruments.validators import truncated_range

import visa
import numpy as np
import time
from io import BytesIO


class Keithley2400(Instrument):
    """This is the class for the Keithley 2000-series instruments"""

    source_voltage = Instrument.control(
        ":SOUR:VOLT?;", ":SOUR:VOLT:LEV %g;",
        """ A floating point property that represents the output voltage
        in Volts. This property can be set. """
    )
    source_current = Instrument.control(
        ":SOUR:CURR?;", ":SOUR:CURR:LEV %g;",
        """ A floating point property that represents the output current
        in Amps. This property can be set. """
    )
    voltage = Instrument.measurement(":READ?",
        """ Reads the voltage in Volts, if configured for this reading.
        """
    )
    current = Instrument.measurement(":READ?",
        """ Reads the current in Amps, if configured for this reading.
        """
    )
    resistance = Instrument.measurement(":READ?",
        """ Reads the resistance in Ohms, if configured for this reading.
        """
    )
    buffer_count = Instrument.measurement(":TRAC:POIN:ACT?",
        """ Reads the integer buffer count. """
    )
    voltage_range = Instrument.control(
        ":SOUR:VOLT:RANG?", ":SOUR:VOLT:RANG %0.2f",
        """ A floating point property that represents the voltage range
        in Volts, which can take values from -210 to 210 V. 
        This property can be set. """,
        validator=truncated_range,
        values=[-210, 210]
    )
    current_range = Instrument.control(
        ":SOUR:CURR:RANG?", ":SOUR:CURR:RANG %0.2f",
        """ A floating point property that represents the current range
        in Amps, which can take values between -1.05 and +1.05 A. 
        This property can be set. """,
        validator=truncated_range,
        values=[-1.05, 1.05]
    )
    resistance_range = Instrument.control(
        ":RES:RANG?", ":RES:RANG %e",
        """ A floating point property that represents the resistance range
        in Ohms, which can take values from 0 to 210 MOhms. 
        This property can be set. """,
        validator=truncated_range,
        values=[0, 210e6]
    )
    means = Instrument.measurement(
        ":CALC3:FORM MEAN;:CALC3:DATA?;",
        """ Reads the calculated means (averages) for voltage,
        current, and resistance from the buffer data  as a list
        """
    )
    maximums = Instrument.measurement(
        ":CALC3:FORM MAX;:CALC3:DATA?;",
        """ Returns the calculated maximums for voltage, current, and
        resistance from the buffer data as a list
        """
    )
    minimums = Instrument.measurement(
        ":CALC3:FORM MIN;:CALC3:DATA?;",
        """ Returns the calculated minimums for voltage, current, and
        resistance from the buffer data as a list
        """
    )
    standard_devs = Instrument.measurement(
        ":CALC3:FORM SDEV;:CALC3:DATA?;",
        """ Returns the calculated standard deviations for voltage,
        current, and resistance from the buffer data as a list
        """
    )

    def __init__(self, resourceName, **kwargs):
        super(Keithley2400, self).__init__(
            resourceName,
            "Keithley 2400 Sourcemeter",
            **kwargs
        )

        self.write("format:data ascii")
        # self.values_format = visa.ascii
        self.reset()
        self.source_mode = None

    def beep(self, frequency, duration):
        self.write(":SYST:BEEP %g, %g" % (frequency, duration))

    def triad(self, base_frequency, duration):
        import time
        self.beep(base_frequency, duration)
        time.sleep(duration)
        self.beep(base_frequency*5.0/4.0, duration)
        time.sleep(duration)
        self.beep(base_frequency*6.0/4.0, duration)

    def check_errors(self):
        import re
        err = int(re.search(r'\d+', self.values(":system:error?")).group())
        while err != 0:
            t = time.time()
            log.info("Keithley Encountered error: %d\n" % err)
            err = int(re.search(r'\d+', self.values(":system:error?")).group())
            if (time.time()-t)>10:
                log.warning('Timeout for Keithley error retrieval.')

    def reset(self):
        self.write("status:queue:clear;*RST;:stat:pres;:*CLS;")

    def ramp_to_current(self, target_current, steps=30, pause=20e-3):
        currents = np.linspace(
            self.source_current,
            target_current,
            steps
        )
        for current in currents:
            self.source_current = current
            time.sleep(pause)

    def ramp_to_voltage(self, target_voltage, steps=30, pause=20e-3):
        voltages = np.linspace(
            self.getSourceVoltage(),
            target_voltage,
            steps
        )
        for voltage in voltages:
            self.source_voltage = voltage
            time.sleep(pause)

    def set_trigger_bus(self):
        self.write(":ARM:COUN 1;:ARM:SOUR BUS;:TRIG:SOUR BUS;")

    def set_trigger_counts(self, arm, trigger):
        """ Sets the number of counts for both the sweeps (arm) and the
        points in those sweeps (trigger), where the total number of
        points can not exceed 2500
        """
        if arm * trigger > 2500 or arm * trigger < 0:
            raise RangeException("Keithley 2400 has a combined maximum "
                                 "of 2500 counts")
        if arm < trigger:
            self.write(":ARM:COUN %d;:TRIG:COUN %d" % (arm, trigger))
        else:
            self.write(":TRIG:COUN %d;:ARM:COUN %d" % (trigger, arm))

    def set_continous(self):
        """ Sets the Keithley to continously read samples
        and turns off any buffer or output triggering
        """
        self.disable_buffer()
        self.disable_output_trigger()
        self.set_immediate_trigger()

    def set_immediate_trigger(self):
        """ Sets up the measurement to be taken with the internal
        trigger at the maximum sampling rate
        """
        self.write(":ARM:SOUR IMM;:TRIG:SOUR IMM;")

    def set_timed_arm(self, interval):
        """ Sets up the measurement to be taken with the internal
        trigger at a variable sampling rate defined by the interval
        in seconds between sampling points
        """
        if interval > 99999.99 or interval < 0.001:
            raise RangeException("Keithley 2400 can only be time"
                                 " triggered between 1 mS and 1 Ms")
        self.write(":ARM:SOUR TIM;:ARM:TIM %.3f" % interval)

    def set_external_trigger(self, line=1):
        """ Sets up the measurments to be taken on the specified
        line of an external trigger
        """
        cmd = ":ARM:SOUR TLIN;:TRIG:SOUR TLIN;"
        cmd += ":ARM:ILIN %d;:TRIG:ILIN %d;" % (line, line)
        self.write(cmd)

    def set_output_trigger(self, line=1, after='DEL'):
        """ Sets up an output trigger on the specified trigger link
        line number, with the option of supplyiny the part of the
        measurement after which the trigger should be generated
        (default to Delay, which is right before the measurement)
        """
        self.write(":TRIG:OUTP %s;:TRIG:OLIN %d;" % (after, line))

    def disable_output_trigger(self):
        """ Disables the output trigger for the Trigger layer
        """
        self.write(":TRIG:OUTP NONE")

    def set_buffer(self, points=64, delay=0):
        # TODO: Check if :STAT:PRES is needed (was in Colin's old code
        self.write(":*CLS;*SRE 1;:STAT:MEAS:ENAB 512;")
        self.write(":TRACE:CLEAR;"
                   ":TRAC:POIN %d;:TRIG:COUN %d;:TRIG:delay %f;" % (
                        points, points, 1.0e-3*delay))
        self.write(":TRAC:FEED SENSE;:TRAC:FEED:CONT NEXT;")
        self.check_errors()

    def is_buffer_full(self):
        """ Returns True if the buffer is full of measurements """
        return int(self.ask("*STB?;")) == 65

    def wait_for_buffer(self, has_aborted=lambda: False,
                        time_out=60, time_step=0.01):
        """ Blocks waiting for a full buffer or an abort event with timing
        set in units of seconds
        """
        # self.connection.wait_for_srq()
        i = 0
        while not self.is_buffer_full() and i < (time_out / time_step):
            time.sleep(time_step)
            i += 1
            if has_aborted():
                return False
        if not self.isBufferFull():
            raise Exception("Timeout waiting for Keithley 2400 buffer to fill")

    def get_buffer(self):
        return np.loadtxt(
            BytesIO(self.ask(":TRAC:DATA?")),
            dtype=np.float32,
            delimiter=','
        )

    def start_buffer(self):
        self.write(":INIT")

    def reset_buffer(self):
        self.ask("status:measurement?")
        self.write("trace:clear; feed:control next")

    def stop_buffer(self):
        """ Aborts the arming and triggering sequence and uses
        a Selected Device Clear (SDC) if possible
        """
        if type(self.connection) is PrologixAdapter:
            self.write("++clr")
        else:
            self.write(":ABOR")

    def disable_buffer(self):
        """ Disables the connection between measurements and the
        buffer, but does not abort the measurement process
        """
        self.write(":TRAC:FEED:CONT NEV")

    @property
    def mean_voltage(self):
        """ Returns the mean voltage from the buffer """
        return self.means[0]

    @property
    def max_voltage(self):
        """ Returns the maximum voltage from the buffer """
        return self.maximums[0]

    @property
    def min_voltage(self):
        """ Returns the minimum voltage from the buffer """
        return self.minimums[0]

    @property
    def std_voltage(self):
        """ Returns the voltage standard deviation from the buffer """
        return self.standard_devs[0]

    @property
    def mean_current(self):
        """ Returns the mean current from the buffer """
        return self.means[1]

    @property
    def max_current(self):
        """ Returns the maximum current from the buffer """
        return self.maximums[1]

    @property
    def min_current(self):
        """ Returns the minimum current from the buffer """
        return self.mininums[1]

    @property
    def std_current(self):
        """ Returns the current standard deviation from the buffer """
        return self.standard_devs[1]

    @property
    def mean_resistance(self):
        """ Returns the mean resistance from the buffer """
        return self.means[2]

    @property
    def max_resistance(self):
        """ Returns the maximum resistance from the buffer """
        return self.maximums()[2]

    @property
    def min_resistance(self):
        """ Returns the minimum resistance from the buffer """
        return self.minimums[2]

    @property
    def std_resistance(self):
        """ Returns the resistance standard deviation from the buffer """
        return self.standard_devs[2]

    @property
    def wires(self):
        val = int(self.values(':system:rsense?'))
        return (4 if val == 1 else 2)

    @wires.setter
    def wires(self, wires):
        wires = int(wires)
        if (wires == 2):
            self.write(":SYSTem:RSENse 0")
        elif (wires == 4):
            self.write(":SYSTem:RSENse 1")

    def measure_resistance(self, nplc=1, resistance=1000.0, auto_range=True):
        """ Sets up to measure resistance
        """
        log.info("<i>%s</i> is measuring resistance." % self.name)
        self.write(":sens:func \"res\";"
                   ":sens:res:mode man;"
                   ":sens:res:nplc %f;:form:elem res;" % nplc)
        if auto_range:
            self.write(":sens:res:rang:auto 1;")
        else:
            self.write(":sens:res:rang:auto 0;:sens:res:rang %g" % resistance)
        self.check_errors()

    def measure_voltage(self, nplc=1, voltage=1000.0, auto_range=True):
        """ Sets up to measure voltage
        """
        log.info("<i>%s</i> is measuring voltage." % self.name)
        self.write(":sens:func \"volt\";"
                   ":sens:volt:nplc %f;:form:elem volt;" % nplc)
        if auto_range:
            self.write(":sens:volt:rang:auto 1;")
        else:
            self.write(":sens:volt:rang:auto 0;:sens:volt:rang %g" % voltage)
        self.check_errors()

    def measure_current(self, nplc=1, current=1000.0, auto_range=True):
        log.info("<i>%s</i> is measuring current." % self.name)
        self.write(":sens:func \"curr\";"
                   ":sens:curr:nplc %f;:form:elem curr;" % nplc)
        if auto_range:
            self.write(":sens:curr:rang:auto 1;")
        else:
            self.write(":sens:curr:rang:auto 0;:sens:curr:rang %g" % current)
        self.check_errors()

    def config_current_source(self, source_current=0.00e-3,
                              complicance_voltage=0.1, current_range=1.0e-3,
                              auto_range=True):
        """ Set up to source current
        """
        log.info("<i>%s</i> is sourcing current." % self.name)
        self.source_mode = "Current"
        if auto_range:
            self.write(":sour:func curr;"
                       ":sour:curr:rang:auto 1;"
                       ":sour:curr:lev %g;" % source_current)
        else:
            self.write(":sour:func curr;"
                       ":sour:curr:rang:auto 0;"
                       ":sour:curr:rang %g;:sour:curr:lev %g;" % (
                            current_range, source_current))
        self.write(":sens:volt:prot %g;" % complicance_voltage)
        self.check_errors()

    def config_voltage_source(self, source_voltage=0.00e-3,
                              compliance_current=0.1, current_range=2.0,
                              voltage_range=2.0, auto_range=True):
        """ Set up to source voltage
        """
        log.info("<i>%s</i> is sourcing voltage." % self.name)
        self.source_mode = "Voltage"
        if auto_range:
            self.write("sour:func volt;"
                       ":sour:volt:rang:auto 1;"
                       ":sour:volt:lev %g;" % source_voltage)
        else:
            self.write("sour:func volt;"
                       ":sour:volt:rang:auto 0;"
                       ":sour:volt:rang %g;:sour:volt:lev %g;" % (
                            voltage_range, source_voltage))
        self.write(":sens:curr:prot %g;" % compliance_current)
        self.check_errors()

    def status(self):
        return self.ask("status:queue?;")

    @property
    def output(self):
        return self.values("output?") == 1

    @output.setter
    def output(self, value):
        if value:
            self.write("output on;")
        else:
            self.write("output off;")

    def RvsI(self, startI, stopI, stepI, compliance, delay=10.0e-3, backward=False):
        num = int(float(stopI-startI)/float(stepI)) + 1
        currRange = 1.2*max(abs(stopI),abs(startI))
        # self.write(":SOUR:CURR 0.0")
        self.write(":SENS:VOLT:PROT %g" % compliance)
        self.write(":SOUR:DEL %g" % delay)
        self.write(":SOUR:CURR:RANG %g" % currRange )
        self.write(":SOUR:SWE:RANG FIX")
        self.write(":SOUR:CURR:MODE SWE")
        self.write(":SOUR:SWE:SPAC LIN")
        self.write(":SOUR:CURR:STAR %g" % startI)
        self.write(":SOUR:CURR:STOP %g" % stopI)
        self.write(":SOUR:CURR:STEP %g" % stepI)
        self.write(":TRIG:COUN %d" % num)
        if backward:
            currents = np.linspace(stopI, startI, num)
            self.write(":SOUR:SWE:DIR DOWN")
        else:
            currents = np.linspace(startI, stopI, num)
            self.write(":SOUR:SWE:DIR UP")
        self.connection.timeout = 30.0
        self.outputOn()
        data = self.values(":READ?") 

        self.check_errors()
        return zip(currents,data)

    def RvsIaboutZero(self, minI, maxI, stepI, compliance, delay=10.0e-3):
        data = []
        data.extend(self.RvsI(minI, maxI, stepI, compliance=compliance, delay=delay))
        data.extend(self.RvsI(minI, maxI, stepI, compliance=compliance, delay=delay, backward=True))
        self.outputOff()    
        data.extend(self.RvsI(-minI, -maxI, -stepI, compliance=compliance, delay=delay))
        data.extend(self.RvsI(-minI, -maxI, -stepI, compliance=compliance, delay=delay, backward=True))
        self.outputOff()
        return data 

    def use_rear_terminals(self):
        """ Uses the rear terminals instead of the front """
        self.write(":ROUT:TERM REAR")

    def use_front_terminals(self):
        """ Uses the front terminals instead of the rear """
        self.write(":ROUT:TERM FRON")

    def shutdown(self):
        log.info("Shutting down <i>%s</i>." % self.name)
        if self.source_mode == "Current":
            self.ramp_source_current(0.0)
        else:
            self.ramp_source_voltage(0.0)
        self.wires = 2
        self.stopBuffer()
        self.outputOff()
