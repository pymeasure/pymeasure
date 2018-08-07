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

from time import sleep, time

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_range


class OxfordITC503(Instrument):
    """Represents the Oxford Intelligent Temperature Controller 503
    """

    control_mode = Instrument.setting(
        "$C%d",
        """ A string property that sets the ITC in LOCAL or REMOTE and LOCKES,
        or UNLOCKES, the LOC/REM button. Allowed values are:
        LL: LOCAL & LOCKED
        RL: REMOTE & LOCKED
        LU: LOCAL & UNLOCKED
        RU: REMOTE & UNLOCKED""",
        validator=strict_discrete_set,
        values={"LL": 0, "RL": 1, "LU": 2, "RU": 3},
        map_values=True,
    )

    heater_gas_mode = Instrument.setting(
        "$A%d",
        """ A string property that sets the heater and gas flow control to
        AUTO or MANUAL. Allowed values are:
        MANUAL: HEATER MANUAL, GAS MANUAL
        AM: HEATER AUTO, GAS MANUAL
        MA: HEATER MANUAL, GAS AUTO
        AUTO: HEATER AUTO, GAS AUTO""",
        validator=strict_discrete_set,
        values={"MANUAL": 0, "AM": 1, "MA": 2, "AUTO": 3},
        map_values=True,
    )

    temperature_setpoint = Instrument.control(
        "R0", "$T%f",
        """ A floating point property that controls the temperature set-point of
        the ITC in kelvin. """,
        get_process=lambda v: float(v[1:]),
        validator=truncated_range,
        values=[0, 301]
    )

    temperature_1 = Instrument.measurement(
        "R1",
        """ Reads the temperature of the sensor 1 in Kelvin. """,
        get_process=lambda v: float(v[1:]),
    )

    temperature_2 = Instrument.measurement(
        "R2",
        """ Reads the temperature of the sensor 2 in Kelvin. """,
        get_process=lambda v: float(v[1:]),
    )

    temperature_2 = Instrument.measurement(
        "R3",
        """ Reads the temperature of the sensor 3 in Kelvin. """,
        get_process=lambda v: float(v[1:]),
    )

    def __init__(self, resourceName, **kwargs):
        super(OxfordITC503, self).__init__(
            resourceName,
            "Oxford ITC503",
            includeSCPI=False,
            send_end=True,
            read_termination="\r",
            **kwargs
        )

    def wait_for_temperature(self, sensor=1, error=0.01, timeout=3600,
                             check_interval=0.5, stability_interval=10,
                             thermalize_interval=300):

        sensor_name = 'temperature_{:d}'.format(sensor)

        initial = getattr(self, sensor_name)
        setpoint = self.temperature_setpoint

        def within_error():
            return abs(getattr(self, sensor_name) - setpoint) < error

        number_of_intervals = int(stability_interval / check_interval)
        attempt = 0

        t0 = time()
        while True:

            stable_over_intervals = [within_error()]
            for idx in range(number_of_intervals):
                sleep(check_interval)
                stable_over_intervals.append(within_error())

            print(stable_over_intervals)

            if all(stable_over_intervals):
                break

            if (time() - t0) > timeout:
                raise TimeoutError(
                    "Timeout expired while waiting for the Oxford ITC305 to \
                    reach the setpoint temperature"
                )

            attempt += 1

        if attempt == 0:
            return

        sleep(thermalize_interval)

        log.info("Setpoint temperature {:.2f} K reached in {:.0f} s, \
            starting from {:.2f} K".format(initial, time() - t0, setpoint))
