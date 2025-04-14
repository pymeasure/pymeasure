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
    '''A class representing the PTW UNIDOS Tango/Romeo dosemeters.'''

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
        '''Overwrites the :meth:`Instrument.read <pymeasure.instruments.Instrument.read>` to
        replace semicolon by comma and check the response for errors.
        '''

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
        '''Convert the error flags to the error message(s).

        :param str flags:
        '''

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
        '''Clear the complete measurement history.

        .. note:: Write permission is required.
        '''
        self.ask("CHR")

    def hold(self):
        '''Set the measurment to HOLD state.

        .. note:: Write permission is required.
        '''
        self.ask("HLD")

    def intervall(self, intervall=None):
        '''Execute an intervall measurement.

        :param int intervall: optional, measurement intervall in seconds

        If *intervall* is not specified a measurement with the current setting of the
        :attr:`integration_time` is executed.

        .. note:: Write permission is required.
        '''
        if intervall is not None:
            self.integration_time = intervall
        self.ask("INT")

    def measure(self):
        '''Start the dose or charge measurement.

        .. note:: Write permission is required.
        '''
        self.ask("STA")

    def reset(self):
        '''Reset the dose and charge measurement values.

        .. note:: Write permission is required.
        '''
        self.ask("RES")

    def selftest(self):
        '''Execute the electrometer selftest.

        The function returns before the end of the selftest.
        End and result of the self test have to be requested by
        the :attr:`selftest_result` property.

        .. note:: Write permission is required.
        '''
        self.ask("AST")

    def zero(self):
        '''Execute a zero correction measurement.

        The function returns before the end of the zero correction
        measurement. The end of the zero correction measurement
        has to be requested by the :attr:`zero_status` property.

        .. note:: Write permission is required.
        '''
        self.ask('NUL')

##############
# Properties #
##############

    autostart_level = Instrument.control(
        "ASL", "ASL;%s",
        '''Control the threshold level of autostart measurements.

        :type: str, strictly in ``LOW``, ``MEDIUM``, ``HIGH``
        ''',
        validator=strict_discrete_set,
        values=['LOW', 'MEDIUM', 'HIGH'],
        check_set_errors=True
        )

    id = Instrument.measurement(
        "PTW",
        '''Get the dosemeter ID.

        :type: list of str

        .. [name, type number, firmware version, hardware revision]
        '''
        )

    integration_time = Instrument.control(
        "IT", "IT;%s",
        '''Control the time of the interval measurement in seconds.

        :type: int, strictly from ``1`` to ``3599999``
        ''',
        validator=truncated_range,
        values=[1, 3599999],
        check_set_errors=True,
        cast=int
        )

    mac_address = Instrument.measurement(
        "MAC",
        '''Get the dosemeter MAC address.

        :type: str
        '''
        )

    meas_result = Instrument.measurement(
        "MV",
        '''Get the measurement results.

        :type: dict
        :dict keys: ``status``,
                    ``charge``,
                    ``dose``,
                    ``current``,
                    ``doserate``,
                    ``timebase``,
                    ``time``,
                    ``voltage``,
                    ``error``
        ''',
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

        :type: str, strictly in ``VERY_LOW``, ``LOW``, ``MEDIUM``, ``HIGH``
        ''',
        validator=strict_discrete_set,
        values=['VERY_LOW', 'LOW', 'MEDIUM', 'HIGH'],
        check_set_errors=True
        )

    range_max = Instrument.measurement(
        "MVM",
        '''Get the max value of the current measurement range.

        :type: dict
        :dict keys: ``range``,
                    ``current``,
                    ``doserate``,
                    ``timebase``
        ''',
        get_process=lambda v: {'range': v[0],
                               'current': float(str(v[1]) + str(v[2])),
                               'doserate': float(str(v[1]) + str(v[2])),
                               'timebase': v[5]},  # timebase for doserate
        )

    range_res = Instrument.measurement(
        "MVR",
        '''Get the resolution of the measurement range.

        :type: dict
        :dict keys: ``range``,
                    ``charge``,
                    ``dose``,
                    ``current``,
                    ``doserate``,
                    ``timebase``
        ''',
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

        :return: dict
        :dict keys: ``status``,
                    ``time_remaining``,
                    ``time_total``,
                    ``low``,
                    ``medium``,
                    ``high``
        ''',
        get_process=lambda v: {'status': v[0],
                               'time_remaining': v[1],
                               'time_total': v[2],
                               'low': float(str(v[4]) + str(v[5])),
                               'medium': float(str(v[9]) + str(v[10])),
                               'high': float(str(v[14]) + str(v[15]))}
        )

    serial_number = Instrument.measurement(
        "SER",
        '''Get the dosemeter serial number.

        :type: int
        ''',
        cast=int
        )

    status = Instrument.measurement(
        "S",
        '''Get the measurement status.

        :type: str

        The status string has of one of the following values: ``RES``,
        ``MEAS``, ``HOLD``, ``INT``, ``INTHLD``, ``ZERO``, ``AUTO``,
        ``AUTO_MEAS``, ``AUTO_HOLD``, ``EOM``, ``WAIT``, ``INIT``,
        ``ERROR``, ``SELF_TEST`` or ``TST``
        '''
        )

    tfi = Instrument.measurement(
        "TFI",
        '''Get the telegram failure information.

        :type: str

        The property provides information about the last failed command with HTTP request.
        '''
        )

    use_autostart = Instrument.control(
        "ASE", "ASE;%s",
        '''Control the measurement autostart function.

        :type: bool
        ''',
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'true', False: 'false'},
        check_set_errors=True
        )

    use_autoreset = Instrument.control(
        "ASR", "ASR;%s",
        '''Control the measurement auto reset function.

        :type: bool
        ''',
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'true', False: 'false'},
        check_set_errors=True
        )

    use_electrical_units = Instrument.control(
        "UEL", "UEL;%s",
        '''Control whether electrical units are used.

        :type: bool
        ''',
        validator=strict_discrete_set,
        map_values=True,
        values={True: 'true', False: 'false'},
        check_set_errors=True
        )

    voltage = Instrument.control(
        "HV", "HV;%d",
        '''Control the detector voltage in Volts.

        :type: int,  strictly from ``-400`` to ``400`` and within detector limits

        The Limits of the detector are applied.
        ''',
        validator=truncated_range,
        values=[-400, 400],
        check_set_errors=True,
        cast=int
        )

    write_enabled = Instrument.control(
        "TOK;1", "TOK%s",
        '''Control the write permission.

        :type: bool

        The result of the request/release has to be checked afterwards.

        .. important:: The UNIDOS has to be in viewer mode (closed lock symbol on the display).
        ''',
        validator=strict_discrete_set,
        values=[True, False],
        set_process=lambda v: '' if (v) else f";{int(v)}",  # 'TOK' = request write permission
                                                            # 'TOK;0' = release write permision
                                                            # 'TOK;1' = get status
        get_process=lambda v: True if (v[1] == 'true') else False,
        check_set_errors=True
        )

    zero_status = Instrument.measurement(
        "NUS",
        '''Get the status of the zero correction measurement.

        :type: dict
        :dict keys:  ``status``,
                     ``time_remaining``,
                     ``time_total``
        ''',
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

        :param str guid: optional, id of the detector. A list of all
            detectors is returned if ommitted.

        :type: dict or list of dict
        :dict keys: ``calibrationFactor``,
                    ``calibrationFactorUnit``,
                    ``calibrationLab``,
                    ``calibrationProcedure``,
                    ``calibrationTemp``,
                    ``calibrationType``,
                    ``calibrationUser``,
                    ``comment``,
                    ``guid``,
                    ``manufacturer``,
                    ``maxHv``,
                    ``measuredQuantity``,
                    ``minHv``,
                    ``name``,
                    ``nominalHv``,
                    ``polarity``,
                    ``radiationQuality``,
                    ``range``,
                    ``serialNumber``,
                    ``testDate``,
                    ``testLimits``,
                    ``testResult``,
                    ``testTarget``,
                    ``timebase``,
                    ``type``,
                    ``typeNumber``
        '''

        if guid.upper() in ['', 'ALL']:
            d_rec = self.ask("RDA")
        else:
            guid, comma, d_rec = self.ask(f"RDR;{guid}").partition(',')

        return json.loads(d_rec)  # str -> dict

    lan_config = Instrument.measurement(
        "REC",
        '''Get the ethernet configuration.

        :type: dict
        :dict keys: ``dns``,
                    ``ipv4``,
                    ``ipv6``
        ''',
        get_process=lambda v: json.loads(','.join(v))  # list -> str -> dict
        )

    meas_history = Instrument.measurement(
        "RHR",
        '''Get the measurement history.

        :type: list of dict
        :dict keys: ``date``,
                    ``detector``,
                    ``dose``,
                    ``flags``,
                    ``id``,
                    ``kTotal``
        ''',
        get_process=lambda v: json.loads(','.join(v)) if v != '[]' else []
        )

    meas_parameters = Instrument.measurement(
        "RMR",
        '''Get the measurement parameters.

        :type: dict
        :dict keys: ``correction``,
                    ``detectorGuid``,
                    ``highResolution``,
                    ``hv``,
                    ``integrationTime``,
                    ``isElectrical``,
                    ``limitDose``,
                    ``limitDoseEnabled``,
                    ``limitDoseRate``,
                    ``limitDoseRateEnabled``,
                    ``range``,
                    ``triggerAuto``,
                    ``triggerReset``,
                    ``triggerSensitivity``
        ''',
        get_process=lambda v: json.loads(','.join(v))  # list -> str -> dict
        )

    system_info = Instrument.measurement(
        "RIR",
        '''Get the system information.

        :type: dict
        :dict keys: ``calibrationDate``,
                    ``debugBuild``,
                    ``features``,
                    ``hardwareVersion``,
                    ``hostname``,
                    ``lastTest``,
                    ``macAddress``,
                    ``nextCalibration``,
                    ``serialNumber``,
                    ``softwareVersion``,
                    ``testTemperature``,
                    ``typeNumber``
        ''',
        get_process=lambda v: json.loads(','.join(v))  # list -> str -> dict
        )

    system_settings = Instrument.measurement(
        "RSR",
        '''Get the system settings.

        :type: dict
        :dict keys: ``brightness``,
                    ``date``,
                    ``keyboardSound``,
                    ``locale``,
                    ``mark``,
                    ``startAsMaster``,
                    ``time``,
                    ``timezone``,
                    ``volume``
        ''',
        get_process=lambda v: json.loads(','.join(v))  # list -> str -> dict
        )

    wlan_config = Instrument.measurement(
        "RAC",
        '''Get the WLAN access point configuration.

        :type: dict
        :dict keys: ``enabled``,
                    ``ssid``
        ''',
        get_process=lambda v: json.loads(','.join(v))  # list -> str -> dict
        )
