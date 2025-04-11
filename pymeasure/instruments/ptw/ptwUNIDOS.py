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
import json

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (strict_discrete_set,
                                              truncated_range)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ptwUNIDOS(Instrument):
    '''A class representing the PTW UNIDOS dosemeter.'''

    def __init__(self, adapter, name="PTW UNIDOS dosemeter",
                 timeout=20000,
                 read_termination='\r\n',
                 encoding='utf8',
                 **kwargs):
        super().__init__(
            adapter,
            name,
            read_termination=read_termination,
            includeSCPI=False,
            timeout=timeout,
            encoding=encoding,
            **kwargs
        )

    def read(self):
        '''Read the response and check for errors.'''

        got = super().read()

        if got.startswith('E'):
            error_code = got.replace(';', '').strip()

            errors = {
                'E01': 'Syntax error, unknown command',
                'E02': 'Command not allowed in this context',
                'E03': 'Command not allowed at this moment',
                'E08': 'Parameter error: value invalid/out of range or \
wrong format of the parameter',
                'E12': 'Abort by user',
                'E16': 'Command to long',
                'E17': 'Maximum number of parameters exceeded',
                'E18': 'Empty parameter field',
                'E19': 'Wrong number of parameters',
                'E20': 'No user rights, no write permission',
                'E21': 'Required parameter not found (eg. detector)',
                'E24': 'Memory error: data could not be stored',
                'E28': 'Unknown parameter',
                'E29': 'Wrong parameter type',
                'E33': 'Measurement module defect',
                'E51': 'Undefined command',
                'E52': 'Wrong parameter type of the HTTP response',
                'E54': 'HTTP request denied',
                'E58': 'Wrong valueof the HTTP response',
                'E96': 'Timeout'
                }

            if error_code in errors.keys():
                error_text = f"{error_code}, {errors[error_code]}"
                raise ValueError(error_text)
            else:
                raise ConnectionError(f"Unknown read error. Received: {got}")

        else:
            command, sep, response = got.partition(';')  # command is removed from response
            return response.replace(';', ',')

    def check_set_errors(self):
        '''Check for errors after sending a command.'''

        try:
            self.read()
        except Exception as exc:
            log.exception("Sending a command failed.", exc_info=exc)
            raise
        else:
            return []

    def errorflags_to_text(self, flags):
        '''Convert the error flags to the error message.
        Several errors can occur in parallel.'''

        err_txt = ['Overload at current measurement',
                   'Overload at charge measurement',
                   'HV-Error at current measurement',
                   'HV-Error at charge measurement',
                   'Low signal at current measurement',
                   'Low signal at charge measurement',
                   'Low auto signal',
                   None,
                   'Radiation safety warning at current measurement',
                   'Radiation safety warning at charge measurement',
                   'PTW internal',
                   'Uncalibrated']

        err_msg = []
        err_code = int(flags, 0)

        for n in range(len(err_txt)):
            if err_code & (2**n):
                err_msg.append(err_txt[n])

        return err_msg

###########
# Methods #
###########

    def clear(self):
        '''Clear the complete device history.

        Write permission is required.'''
        self.ask("CHR")

    def hold(self):
        '''Set the measurment to HOLD state.

        Write permission is required.'''
        self.ask("HLD")

    def intervall(self, intervall=None):
        '''Execute an intervall measurement.

        Write permission is required.'''
        if intervall is not None:
            self.integration_time = intervall
        self.ask("INT")

    def measure(self):
        '''Start the dose or charge measurement.

        Write permission is required.'''
        self.ask("STA")

    def reset(self):
        '''Reset the dose and charge measurement values.

        Write permission is required.'''
        self.ask("RES")

    def selftest(self):
        '''Execute the electrometer selftest.

        The function returns before the end of the selftest.
        End and result of the self test have to be requested by
        the :selftest_result: property.
        Write permission is required.'''
        self.ask("AST")

    def zero(self):
        '''Execute the zero correction measurement.

        The function returns before the end of the zero correction
        measurement. End and result of the zero correction measurement
        have to be requested by the :zero_result: property.
        Write permission is required.'''
        self.ask('NUL')

##############
# Properties #
##############

    autostart_level = Instrument.control(
        "ASL", "ASL;%s",
        '''Control the threshold level of autostart measurements.

        String strictly in ['LOW', 'MEDIUM', 'HIGH']''',
        validator=strict_discrete_set,
        values=['LOW', 'MEDIUM', 'HIGH'],
        check_set_errors=True
        )

    id = Instrument.measurement(
        "PTW",
        '''Get the dosemeter ID.

        Returns a list [name, type number, firmware version, hardware revision]'''
        )

    integration_time = Instrument.control(
        "IT", "IT;%s",
        '''Control the time of the interval measurement in seconds.

        Integer strictly from 1 to 3599999''',
        validator=truncated_range,
        values=[1, 3599999],
        check_set_errors=True,
        cast=int
        )

    mac_address = Instrument.measurement(
        "MAC",
        '''Get the dosemeter MAC address.'''
        )

    meas_result = Instrument.measurement(
        "MV",
        '''Get the measurement results.

        Returns a dictionary [status, charge/dose value, current/doserate value,
        timebase for doserate, measurement time, detector voltage, error flags]''',
        get_process=lambda v: {'status': v[0],
                               'charge': float(str(v[1]) + str(v[2])),
                               'dose': float(str(v[1]) + str(v[2])),
                               'current': float(str(v[5]) + str(v[6])),
                               'doserate': float(str(v[5]) + str(v[6])),
                               'timebase': v[9],   # timebase for doserate
                               'time': v[10],  # measurement time
                               'voltage': v[12],  # detector voltage
                               'error': v[14]}  # error flags 0x0 ... 0xffff
        )

    range = Instrument.control(
        "RGE", "RGE;%s",
        '''Control the measurement range.

        String strictly in ['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH']''',
        validator=strict_discrete_set,
        values=['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH'],
        check_set_errors=True
        )

    range_max = Instrument.measurement(
        "MVM",
        '''Get the max value of the current measurement range.

        Returns a dictionary {range, current, doserate, timebase}''',
        get_process=lambda v: {'range': v[0],
                               'current': float(str(v[1]) + str(v[2])),
                               'doserate': float(str(v[1]) + str(v[2])),
                               'timebase': v[5]},  # timebase for doserate
        )

    range_res = Instrument.measurement(
        "MVR",
        '''Get the resolution of the current measurement range.

        Returns a dictionary [range, charge/dose value, current/doserate value,
        timebase for doserate]''',
        get_process=lambda v: {'range': v[0],
                               'charge': float(str(v[1]) + str(v[2])),
                               'dose': float(str(v[1]) + str(v[2])),
                               'current': float(str(v[5]) + str(v[6])),
                               'doserate': float(str(v[5]) + str(v[6])),
                               'timebase': v[9]},  # timebase for doserate
        )

    selftest_result = Instrument.measurement(
        "ASS",
        '''Get the dosemeter selftest status and result.

        Returns a list [status, remaining time, total time,
        LOW result, MEDIUM result, HIGH result]''',
        get_process=lambda v: {'status': v[0],
                               'time_remaining': v[1],
                               'time_total': v[2],
                               'LOW': float(str(v[4]) + str(v[5])),
                               'MEDIUM': float(str(v[9]) + str(v[10])),
                               'HIGH': float(str(v[14]) + str(v[15]))}
        )

    serial_number = Instrument.measurement(
        "SER",
        '''Get the dosemeter serial number.''',
        cast=int
        )

    status = Instrument.measurement(
        "S",
        '''Get the measurement status.

        Returns a string: RES, MEAS, HOLD, INT, INTHLD, ZERO,
        AUTO, AUTO_MEAS, AUTO_HOLD, EOM, WAIT,
        INIT, ERROR, SELF_TEST or TST'''
        )

    tfi = Instrument.measurement(
        "TFI",
        '''Get the telegram failure information.

        Information about the last failed command with HTTP request.'''
        )

    use_autostart = Instrument.control(
        "ASE", "ASE;%s",
        '''Control the measurement autostart function (boolean).''',
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'true', False: 'false'},
        check_set_errors=True
        )

    use_autoreset = Instrument.control(
        "ASR", "ASR;%s",
        '''Control the measurement auto reset function (boolean).''',
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'true', False: 'false'},
        check_set_errors=True
        )

    use_electrical_units = Instrument.control(
        "UEL", "UEL;%s",
        '''Control whether electrical units are used (boolean).''',
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'true', False: 'false'},
        check_set_errors=True
        )

    voltage = Instrument.control(
        "HV", "HV;%d",
        '''Control the detector voltage in Volts (float strictly from -400 to 400).

        The Limits of the detector are applied.''',
        validator=truncated_range,
        values=[-400, 400],
        check_set_errors=True
        )

    write_enabled = Instrument.control(
        "TOK;1", "TOK%s",
        '''Control the write permission (boolean).

        The result of the request/release has to be checked afterwards.
        If the request fails check that the UNIDOS is in viewer mode
        (closed lock symbol on the display).''',
        validator=strict_discrete_set,
        values=[True, False],
        set_process=lambda v: '' if (v) else f";{int(v)}",  # 'TOK' = request write permission
                                                            # 'TOK;0' = release write permision
                                                            # 'TOK;1' = get status
        get_process=lambda v: True if (v[1] == 'true') else False,
        check_set_errors=True
        )

    zero_result = Instrument.measurement(
        "NUS",
        '''Get the status and result of the zero correction measurement.

        Returns a list [status, time remaining, total time]''',
        get_process=lambda v: {'status': v[0],
                               'time_remaining': v[1],
                               'time_total': v[2]}
        )

###################################
# JSON configuration structure    #
# only read access is implemented #
###################################

    def read_detector(self, guid='ALL'):
        '''Read the properties of the requested detector.

        If guid is not given, all detectors are returned.
        Returns a dictionary or a list of dictionaries.'''
        if guid.upper() in ['', 'ALL']:
            d_rec = self.ask("RDA")
        else:
            guid, comma, d_rec = self.ask(f"RDR;{guid}").partition(',')

        return json.loads(d_rec)  # str -> dict

    meas_history = Instrument.measurement(
        "RHR",
        '''Get the measurement history.

        Returns a list of dictionaries.''',
        get_process=lambda v: json.loads(','.join(v)) if v != '[]' else []
        )

    meas_parameters = Instrument.measurement(
        "RMR",
        '''Get the measurement parameters.

        Returns a dictionary.''',
        get_process=lambda v: json.loads(','.join(v))  # list -> str -> dict
        )

    system_settings = Instrument.measurement(
        "RSR",
        '''Get the system settings.

        Returns a dictionary.''',
        get_process=lambda v: json.loads(','.join(v))  # list -> str -> dict
        )

    system_info = Instrument.measurement(
        "RIR",
        '''Get the system information.

        Returns a dictionary.''',
        get_process=lambda v: json.loads(','.join(v))  # list -> str -> dict
        )

    wlan_config = Instrument.measurement(
        "RAC",
        '''Get the WLAN access point configuration.

        Returns a dictionary.''',
        get_process=lambda v: json.loads(','.join(v))  # list -> str -> dict
        )

    lan_config = Instrument.measurement(
        "REC",
        '''Get the ethernet configuration.

        Returns a dictionary.''',
        get_process=lambda v: json.loads(','.join(v))  # list -> str -> dict
        )
