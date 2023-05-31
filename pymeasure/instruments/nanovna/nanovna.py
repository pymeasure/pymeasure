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

from numpy import array as _array
from pymeasure.adapters import SerialAdapter
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set


class NanoVNA(Instrument):
    """ Represents the NanoVNA interface for interacting with the instrument.

    .. code-block:: python

    """

    def __init__(self, adapter, name="NanoVNA", **kwargs):
        # kwargs.setdefault('read_termination', '\r\nch> ')
        # kwargs.setdefault('write_termination', '\r')
        self.write_termination = '\r'
        self.read_termination = '\r\nch> '
        self.echo_termination = '\r\n'
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            # read_termination='\r\nch> ',
            # write_termination='\r',
            **kwargs
        )

    def read(self):
        """
        Reads from the instrument including the correct termination characters
        """
        # ret = self.adapter._read_echo()
        # return ret

        read = self.adapter._read_bytes(-1, break_on_termchar=True).decode()
        read = read.replace('ch> ', "").split(self.echo_termination)
        # echo = read[0]
        reply = read[1:-1]

        return ",".join(reply)  # TODO maybe don't return as a single string???

    def write(self, command):
        """
        Writes to the instrument including the device address

        :param command: command string to be sent to the instrument
        """
        # super().write(command)
        self.adapter._write(command + self.write_termination)

    def ask(self, command, query_delay=0):
        """Write a command to the instrument and return the read response.

        :param command: Command string to be sent to the instrument.
        :param query_delay: Delay between writing and reading in seconds.
        :returns: String returned by the device without read_termination.
        """
        self.write(command)
        self.wait_for(query_delay)
        return self.read()

    help = Instrument.measurement(
        'help',
        """Returns list of available commands. """)

    info = Instrument.measurement(
        'info',
        """Returns device information. """)

    pause = Instrument.measurement(
        'pause',
        """Pauses acquisition. Returns nothing. """)

    resume = Instrument.measurement(
        'resume',
        """Resume acquisition.  Returns nothing. """)

    cal_on = Instrument.measurement(
        "cal on",
        """ Enables existing calibration. """)

    cal_off = Instrument.measurement(
        "cal off",
        """ Disables existing calibration. """)

    frequencies = Instrument.measurement("frequencies",
                                         docs=""" Returns frequencies as a list
                                         of floats. """,
                                         get_process=_array,
                                         )

    def _process_complex_data(data_in):
        """ Processes a list of strings containing complex pairs

        :param data_in: list of strings containing complex pairs
        :returns: Numpy array of complex numbers.
        """
        temp = _array(",".join(data_in).replace(" ", ",").split(","))
        temp = temp.astype(float)
        return temp[::2] + temp[1::2] * 1j

    data_S11 = Instrument.measurement("data 0",
                                      docs=""" Returns a complex numpy array
                                      containing the S11 measurement. """,
                                      get_process=_process_complex_data,
                                      )

    data_S21 = Instrument.measurement("data 1",
                                      docs=""" Returns a complex numpy array
                                      containing the S21 measurement. """,
                                      get_process=_process_complex_data,
                                      )

    cal_load = Instrument.measurement("data 2",
                                      docs=""" Returns a complex numpy array
                                      containing the load cal measurement. """,
                                      get_process=_process_complex_data,
                                      )

    cal_open = Instrument.measurement("data 3",
                                      docs=""" Returns a complex numpy array
                                      containing the open cal measurement. """,
                                      get_process=_process_complex_data,
                                      )

    cal_short = Instrument.measurement("data 4",
                                       docs=""" Returns a complex numpy array
                                       containing the short cal
                                       measurement. """,
                                       get_process=_process_complex_data,
                                       )

    cal_thru = Instrument.measurement("data 5",
                                      docs=""" Returns a complex numpy array
                                      containing the thru cal measurement. """,
                                      get_process=_process_complex_data,
                                      )

    cal_isoln = Instrument.measurement("data 6",
                                       docs=""" Returns a complex numpy array
                                       containing the isolation cal
                                       measurement. """,
                                       get_process=_process_complex_data,
                                       )

    trace = Instrument.measurement("trace",
                                   docs=""" Gets the trace settings. """,
                                   # TODO - make this into a control eventually
                                   )

    power = Instrument.setting('power %d',
                               """ Sets the output power. """,
                               validator=strict_discrete_set,
                               values=[-1, 0, 1, 2, 3],
                               # TODO add maps
                               )

    sweep = Instrument.control('sweep',
                               'sweep %i %i %i',
                               """Set the sweep details.  Input and output is
                               a tuple containing 3 integers.
                               First int is the start frequency (in Hz).
                               Second int is the strop frequency (in Hz).
                               Third int is the number of points in the sweep.
                               """,
                               get_process=lambda x:
                               tuple(_array(x.split()).astype(int)),
                               )

    def get_port1_cals(self):
        """ Acuires all the three port 1 calibration measurements and returns
        them as a dict.

        :returns cals: Dictionary containing cal measurements.
        """

        def _process(data_in):
            """ Subfunction to process complex numbers into numpy arrays.

            :param data_in: Str containing complex data
            :returns: Complex numpy array
            """
            # temp = _array(data_in.split())
            temp = _array(data_in.replace(" ", ",").split(","))
            temp = temp.astype(float)
            return temp[::2] + temp[1::2] * 1j

        cals = {}
        cals["cal_load"] = _process(self.ask("data 2"))
        cals["cal_open"] = _process(self.ask("data 3"))
        cals["cal_short"] = _process(self.ask("data 4"))
        # cals["cal_thru"] = _process(unit.ask("data 5"))
        # cals["cal_isoln"] = _process(unit.ask("data 6"))

        return cals

    def perform_1port_cal(self):
        """ Performs 1-port calibration on port 1. """
        self.write('cal off')

        input('Connect open to port 1')
        self.write('cal open')

        input('Connect short to port 1')
        self.write('cal short')

        input('Connect load to port 1')
        self.write('cal load')

        self.write('cal done')
        self.write('cal on')

        print('Calibration completed.  ')


if __name__ == "__main__":
    port = r'/dev/ttyACM0'

    case = 2
    if case == 1:
        adapter = SerialAdapter(port)
        unit = NanoVNA(adapter)
        print(unit.info)
    elif case == 2:
        adapter = SerialAdapter(port, timeout=1)
        unit = NanoVNA(adapter)
        print(unit.info)
    elif case == 3:
        unit = NanoVNA(port)
        print(unit.info)
