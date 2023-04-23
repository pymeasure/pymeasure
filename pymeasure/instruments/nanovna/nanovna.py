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


class SerialAdapterWithEcho(SerialAdapter):

    echo_termination = '\r\n'
    # write_termination = '\r'
    # read_termination = '\r\nch> '

    def _read_echo(self, **kwargs):
        """Read function but includes scrubbing the echo from the reply.

        :param \\**kwargs: Keyword arguments for the connection itself.
        :returns str: ASCII response of the instrument with echo removed.
        """
        read = self._read_bytes(-1, break_on_termchar=True, **kwargs).decode()
        read = read.replace('ch> ', "").split(self.echo_termination)
        # echo = read[0]
        reply = read[1:-1]

        return ",".join(reply)  # TODO maybe don't return as a single string???


class NanoVNA(Instrument):
    """ Represents the NanoVNA interface for interacting with the instrument.

    .. code-block:: python

    """

    def __init__(self, adapter, name="NanoVNA", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            read_termination='\r\nch> ',
            write_termination='\r',
            **kwargs
        )

    def read(self):
        """
        Reads from the instrument including the correct termination characters
        """
        ret = self.adapter._read_echo()
        return ret

    def write(self, command):
        """
        Writes to the instrument including the device address

        :param command: command string to be sent to the instrument
        """
        super().write(command)

    def ask(self, command, query_delay=0):
        """Write a command to the instrument and return the read response.

        :param command: Command string to be sent to the instrument.
        :param query_delay: Delay between writing and reading in seconds.
        :returns: String returned by the device without read_termination.
        """
        self.write(command)
        self.wait_for(query_delay)
        return self.adapter._read_echo()

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
                                   # TODO - make this into a control,
                                   )

    power = Instrument.setting('power %d',
                               """ Sets the output power. """,
                               validator=strict_discrete_set,
                               values=[-1, 0, 1, 2, 3],
                               )

    sweep = Instrument.control('sweep',
                               'sweep %s',
                               """Sets the sweep details.  Input is a string
                               containing 3 integers separated by spaces.
                               First int is the start frequency (in Hz).
                               Second int is the strop frequency (in Hz).
                               Third int is the number of points in the sweep.
                               Example:  '13000000 16000000 101'  """,
                               )

    def get_all_cals(self):

        def _process(data_in):
            temp = _array(data_in.replace(" ", ",").split(","))
            temp = temp.astype(float)
            return temp[::2] + temp[1::2] * 1j

        cals = {}
        cals["cal_load"] = _process(unit.ask("data 2"))
        cals["cal_open"] = _process(unit.ask("data 3"))
        cals["cal_short"] = _process(unit.ask("data 4"))
        cals["cal_thru"] = _process(unit.ask("data 5"))
        cals["cal_isoln"] = _process(unit.ask("data 6"))

        return cals

    def perform_1port_cal(self):
        self.write('cal off')

        input('Connect open')
        self.write('cal open')

        input('Connect short')
        self.write('cal short')

        input('Connect load')
        self.write('cal load')

        self.write('cal done')
        self.write('cal on')

        print('Calibration completed.  ')


if __name__ == "__main__":
    _cr = '\r'
    _lf = '\n'
    _crlf = _cr + _lf
    _prompt = 'ch> '
    port = '/dev/ttyACM0'
    adapter = SerialAdapterWithEcho(port,
                                    timeout=1,
                                    write_termination=_cr,
                                    read_termination=_crlf + _prompt,
                                    )
    unit = NanoVNA(adapter)
