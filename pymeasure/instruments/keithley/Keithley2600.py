#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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

from pymeasure.instruments import Instrument

import time

from .buffer import KeithleyBuffer


# Todo: Give a minimal code example: Set up instrument, Set up Buffer, Perform measurement

class Keithley2600(Instrument, KeithleyBuffer):
    """Represents the Keithley 2600 Series SourceMeters and provides a
    high-level interface for interacting with the instrument.

    The Keithley 2600 series operates with lua-like commands in Keithley's proprietory Test Script Program (TSP) language
    and does not support SCPI beyond basic commands (*IDN? and so on).

    Commands are sent directly to the instrument via self.write_command(). __start_on_call decides whether the received
    commands are executed immediately or after calling execute_script().
    All (pymeasure) functions that wait for a command should always be executed with __start_on_call = True, or else
    they will time-out.

    Keithley 2600 Instruments come with some factory (TSP) scripts already loaded on the instrument.
    External TSP scripts (written in Lua) can be loaded onto the instrument via load_TSP(filename).

    .. code-block:: python

        keithley = Keithley2600("GPIB::1")

        keithley.apply_current()                # Sets up to source current

        """

    def __init__(self, adapter, **kwargs):

        super().__init__(
            adapter,
            "Keithley2600 SourceMeter",
            includeSCPI=False,
            **kwargs
        )

        # TSP script commands can be directly sent and executed or appended to a string and send as one.
        # Having self.TSP_script also allows to use already implemented TSP scripts (still to be tested!)
        self.__start_on_call = True
        self.__start_on_call_change = False


################################
# TSP script related functions #
################################

    def start_on_call(self, value=True):
        """Set function for the private parameter __start_on_call that also acticates the flag __start_on_call_change.
        This way, write_command can fetch the first sent command after change of __start_on_call from True to False.
        :param value:   Boolean value that decides whether the Keithley should execute the commands on receival or wait until a script is loaded command by command."""
        # only change state, if necessary
        if value != __start_on_call:
            self.__start_on_call = value
            self.__start_on_call_change = True

    def write_command(self, new_command):
        """Writes the TSP command to the instrument. if start_on_call is False, the script is not executed upon receiving the command"""

        if not self.__start_on_call and self.__start_on_call_change:  # catch only first write after change of property __start_on_call from True to False
            self.write('loadscript')
            self.__start_on_call_change = False

        self.write(new_command)


    def execute_script(self):
        """Executes the TSP_script """
        if not start_on_call:
            self.write('endscript')
            self.write('run()')

    def load_TSP(self, filename):
        """Loads a TSP script (external file) as anonymous script onto the connected instrument.The script can be executed using self.execute_script
        :param filename:    The filename, including directory, of the TSP script file"""
        if self.__start_on_call == True:
            self.start_on_call(False)
        self.write_command('loadscript')
        for line in open(str(filename), mode='r'):
            self.write_command(line)

        # todo: include a way to use the loaded script as named and not anonymous script. I.e. save it on the instrument for later execution. This also requires a change in execute_script()

        log.info('Uploaded TSP script:' + filename)

#####################
# general functions #
#####################
    def reset(self, smux = 'smua'):
            """Resets the SMU
            :param smux: SMU to be reset"""
            self.write_command(f'{smux}.reset()')

    def set_output(self, smux='smua', state='ON'):
        """Turn the output on or off. State of the output can also be changed with :code enable_source or :code disable_source"""
        #Turn it into  allcaps
        state.upper()
        if state == "ON" or state == "OFF":
            self.write_command(f'{smux}.source.output = OUTPUT_{state}')

    def enable_source(self, smux='smua'):
        self.write_command(f'{smua}.source.output = OUTPUT_ON')

    def disable_source(self, smux='smua'):
        self.write_command(f'{smua}.source.output = OUTPUT_OFF')

    def set_autorange(self, measurefunction, smux='smua', state='ON'):
        """Sets the auto-range value of the smu channel
        :param smux:    SMU channel to be used
        :param state:   auto-range channel to be set. can be OFF: Disabled, ON: Enabled or FOLLOW_LIMIT: Measure range automatically set to the limit range
        :param measurefunction: The measurement function for which the autorange property is changed."""
        voltages = {'voltage','voltages','v','V'}
        currents = {'current''currents','i','I'}
        measurefunction.lower()

        if measurefunction in voltages:
            measurefunction = 'v'
        else:
            if measurefunction in currents:
                measurefunction = 'i'

        self.write_command(f'{smux}.measure.autorange{measurefunction} = AUTORANGE_{state}')

    def set_delay(self, mdelay, smux = 'smua'):
        """This attribute allows for additional delay (settling time) before taking a measurement.
        If more than one measurement per sourced value is performed, the measurement delay is only inserted before the first measurement.
        :param mdelay: the time in seconds after sourcing before the first measurement is performed.
        :param smux: The channel of the SMU that is used"""
        self.write_command(f'{smux}.measure.delay = {mdelay}')

    def set_output_fcn(self, keyword, smux='smua'):
        """Set the source function to be used .
        :param smux:    SMU to be used. Commonly smua
        :param keyword: Defines whether the source function is set to voltage or current"""""
        if keyword == 'voltage':
             self.write_command(f'{smux}.source.func = {smux}.OUTPUT_DCVOLTS')
        else:
                if keyword == 'current':
                    self.write_command(f'{smux}.source.func = {smux}.OUTPUT_DCAMPS')

    def set_integration_time(self, itime, UF=50, smux = 'smua'):
        """Sets the integration time for all measurements in multiple of power line cycles.
        :param itime    Desired integration time in ms
        :param UF       Utility Frequency. Most common for Europe, Asia, South America & Afrika: 50Hz, North America: 60Hz -> check which one applies"""
        nplc = itime * UF
        self.write_command(f'{smux}.measure.nplc = {nplc}')

    def shutdown(self):
        """Brings the instrument to a safe and stable state"""
        self.set_output(state='OFF')
        log.info("Output set to OFF")

    ##########
    # screen #
    ##########

    def clear_screen(self):
        """Clears the screen of the connected device"""
        self.write_command('display.clear()')

    def set_screentext(self, textstring):
        """Sets the text on the screen of the device.
        :param textstring:  Text that is displayed on screen. The following formating characters can be used:
                            $N Newline, starts text on the next line; if the cursor is already on line 2, text will be ignored
                            after the $N is received
                            $R Sets text to normal intensity, nonblinking
                            $B Sets text to blink
                            $D Sets text to dim intensity
                            $F Sets the text to background blink
                            $$ Escape sequence to display a single dollar symbol ($)
                            """
        self.clear_screen()

        self.write_command(f'display.settext("{textstring}")')

        #self.write_command('display.settext("Normal $BBlinking$N")')

    def set_screen_func(self, smux='smua', function='V', acdc = 'DC'):
        """
        Sets the screen to show the defined measurefunction
        :param smux:        smu used for measurement
        :param function:    function to be displayed
        :param acdc:        ac or dc measurement
        """
        #TODO: TEST THIS FUNCTION BEFORE USAGE!!!

        function.upper()
        acdc.upper()
        if function in ['V', 'VOLTS']:
            print(f'display.{smux}.measure.func = display.MEASURE_{acdc}VOLTS')
            self.write_command(f'display.{smux}.measure.func = display.MEASURE_{acdc}VOLTS')
        else:
            if function in ['A', 'AMPERE','I']:
                self.write_command(f'display.{smux}.measure.func = display.MEASURE_{acdc}AMPS')

        self.smu_screen(smux=smux)

    def smu_screen(self, smux='SMUA'):
        """Displays the source-measure and compliance display for the selected SMU
        :param smux:    String defining, the smu which parameters are displayed
        """
        smux.upper()
        self.write_command(f'display.screen = display.{smux}')

    def get_screen_text(self):
        self.write_command('text = display.gettext()')
        screentext = self.ask('print(text)')
        return screentext
###########
# buffer  #
###########

    def clear_buffer(self, smux = 'smua', id = '1'):
        """Clears the dedicaded reading buffer
        :param smux:    The SMU which buffer should be cleared.
        :param id:      The id of the buffer to be cleared. Each smu has two dedicaded reading buffers. use id ='all' to clear all reading buffers
        """
        if id != 'all':
            self.write_command(f'{smux}.nvbuffer{id}.clear()')
        else:
            for i in range(1, 2):
                self.write_command(f'{smux}.nvbuffer{i}.clear()')

    def set_buffer_ascii(self, precision = 6):
        """This function set the data format to ASCII with the given precision
        :param precision:   Precision used for all data received fromt he buffer"""

        self.write_command(f'format.data = format.ASCII\n format.asciiprecision = {precision}')

    def setup_buffer(self, smux = 'smua', id = '1', precision = 6):
        """Convenience function to clear buffer and set it to ascii in one function.
        :param smux:    The SMU which buffer should be cleared.
        :param id:      The id of the buffer to be cleared. Each smu has two dedicaded reading buffers. use id ='all' to clear all reading buffers
        :param precision:   Precision used for all data received fromt he buffer
        """
        self.clear_buffer(smux, id)
        self.set_buffer_ascii(precision)


    def get_buffer_data(self, smux='smua', buffer='nvbuffer1'):
        """Returns the Data from a buffer as numpy array
        :param buffer:  The instrument buffer to be read."""


        sourced = self.ask(f'printbuffer(1, {smux}.{buffer}.n,{smux}.{buffer}.sourcevalues)')
        measured = self.ask(f'printbuffer(1, {smux}.{buffer}.n,{smux}.{buffer}.readings)')
        timestamps = self.ask(f'printbuffer(1, {smux}.{buffer}.n,{smux}.{buffer}.timestamps)')
        return {'sourced':sourced,'measured': measured,'timestamps':timestamps}

#######
# SRQ #
#######
    def setup_srq(self):
        """Sets up the instrument to issue an SRQ on a positive transition of the user-bit 0"""
        # ToDo: Add support for  multiple user-bits

        self.write_command("status.reset()")
        self.write_command("status.operation.user.condition = 0")
        self.write_command("status.operation.user.enable = status.operation.user.BIT0")
        self.write_command("status.operation.user.ptr = status.operation.user.BIT0")
        self.write_command("status.operation.enable = status.operation.USER")  # bit12
        self.write_command("status.request_enable = status.OSB")  # bit7

    def raise_srq(self):
        """Performs a positive transistion of user-bit 0, raising the SRQ if setup_srq has been set before"""
        self.write_command("status.operation.user.condition = status.operation.user.BIT0")


    def wait_for_srq(self):
        self.adapter.wait_for_srq(timeout=60000)
        print('srq received')



###########
# voltage #
###########

    def auto_sweep(self, start, stop, stime, points, smux='smua', keyword='lin', source='V'):
        """ This method uses the Keithley factory TSP scripts to execute linear or logarithmic sweeps.
        Autozero (the internal function to avoid zero drift) is disabled for the sweep to ensure it does not cause timing issues.
        All measured values are written to the internal buffer and read out after the measurement - i.e. data is shown only after a complete cycle.
        :param start:   Start value of the sweep parameter
        :param stop:    End value of the sweep parameter
        :param stime:   Settling time - i.e. time after sourcing before first measurement
        :param points:  Number of measurement points. Should be (max-min)/stepwidth
        :param smux.:   SMU to be used
        :param keyword: Sweeping method. Can be either 'lin' for linear or 'log' for logarithmic
        :param source:  Sourced quantity (i.e. 'V' or 'I')
        """

        self.setup_srq()

        if source == 'V':
            if keyword == 'lin':
                self.write_command(f'SweepVLinMeasureI({smux}, {start}, {stop}, {stime}, {points})')
            elif keyword == 'log':
                self.write_command(f'SweepVLogMeasureI({smux}, {start}, {stop}, {stime}, {points})')
            else:
                print("Invalid choice of keyword in sweep(source='V')")
        elif source == 'I':
            if keyword == 'lin':
                self.write_command(f'SweepILinMeasureV({smux}, {start}, {stop}, {stime}, {points})')
            elif keyword == 'log':
                self.write_command(f'SweepILogMeasureV({smux}, {start}, {stop}, {stime}, {points})')
            else:
                print("Invalid choice of keyword in sweep(source='I')")
                self.set_screentext("Invalid choice of keyword in sweep(source='I')")
        else:
            print("Invalid choice of method in sweep()")
            self.set_screentext("Invalid choice of method in sweep()")

        self.write_command('waitcomplete()')
        self.raise_srq()

    def sweep(self, start, stop, stime, points, smux='smua', keyword='lin', source='V', autorange=True):
        """Executes a linear or logarithmic sweeep manually - i.e. returns the buffer value after each data point is measured
        """

        if keyword == 'lin':

            if source == 'V':
                self.enable_source()
                if autorange:
                    self.set_autorange('i')
                for voltage in setpoints:
                    self.set_voltage(voltage)
                    # todo: get buffer data and write it to an array, dict
                    # datapoints[voltage] = self.get_buffer_data()
                    # todo: return data


###########
#   beep  #
###########

    def beep(self, frequency, duration):
       """Sounds a system beep.
       :param frequency: the frequency of the beep
       :param duration: the duration of the beep"""
       self.write_command(f'beeper.beep({duration}, {frequency})')

    def triad(self, base_frequency=440, duration=0.3):
        """ Sounds a musical triad using the system beep. Can for instance be used to indicate a finished measurement.

        :param base_frequency: Frequency of the base tone in Hz (between 65 Hz and 1.3 MHz)
        :param duration: A time in seconds per beep (between 0 and 7.9 seconds)
        """
        self.beep(base_frequency, duration)
        time.sleep(duration)
        self.beep(base_frequency*5.0/4.0, duration)
        time.sleep(duration)
        self.beep(base_frequency*6.0/4.0, duration)
        #todo: change function so sleep gets executed within the instrument and not on PC

###############
# Current (A) #
###############
    def set_current(self, current, smux='smua'):
        """Sets the current
        :param smux:    SMU to be used. Commonly smua
        :param current: current that is to be set"""
        self.write_command(f'{smux}.source.levelv = {current}') #todo: Use validator for current

###############
# Voltage (V) #
###############
    def set_voltage(self, voltage, smux='smua'):
            """Sets the voltage
            :param smux:    SMU to be used. Commonly smua
            :param voltage: voltage that is to be set"""
            self.write_command(f'{smux}.source.levelv = {voltage}')  # todo: Use validator for voltage

    def read_voltage(self, datapoints, smux='smua', buffer='nvbuffer1'):
            """Measures the voltage and saves data to internal buffer, then returns ....
            :param smux:        SMU to be used. Commonly smua
            :param buffer:      The Keithley 26XX series offers two dedicated buffers per SMU channel. This parameter defines which one is used to buffer measurement data
            :param datapoints:  number of measurements performed"""
            # clear buffer
            self.write_command(f'{smux}.{buffer}.clear() smua.nvbuffer1.appendmode = 1')
            # set number of points and fill buffer
            self.write_command(f'{smux}.measure.count = {datapoints}')
            self.write_command(f'{smux}.measure.v({smux}.{buffer}')


            #todo: write measure_voltage method that reads the buffer
