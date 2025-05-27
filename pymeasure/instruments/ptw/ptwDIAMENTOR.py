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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (strict_discrete_set,
                                              strict_range)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ptwDIAMENTOR(Instrument):
    """A class representing the PTW DIAMENTOR DAP dosemeters."""

    def __init__(self, adapter,
                 name="PTW DIAMENTOR DAP dosemeter",
                 baud_rate=9600,
                 **kwargs):
        super().__init__(
            adapter,
            name,
            baud_rate=baud_rate,
            includeSCPI=False,
            timeout=2000,
            **kwargs
        )

    def read(self):
        """Read the device response and check for errors.

        :return: str

        :raises: *ValueError* for error response or *ConnectionError* for an unknown error
        """
        got = super().read()

        if got.startswith("E"):

            errors = {
                "E1": "Syntax error, unknown command",
                "E4": "Charge overflow",
                "E5": "Max. input current exceeded.",
                "E6": "Chamber voltage is out of range.",
                "E7": "Parameter is write protected.",
                "E9": "Parameter is out of range.",
                "E23": "EEPROM reading/writing error",
                "E24": "DIAMENTOR is not calibrated electrically.",
                "E25": "Input-Buffer-Overrun",
                "E26": "Firmware malfunction"
                }

            if got in errors.keys():
                error_text = f"{got}, {errors[got]}"
                raise ValueError(error_text)
            else:
                raise ConnectionError(f"Unknown read error. Received: {got}")

        else:
            return got

    def check_set_errors(self):
        """Check for errors after sending a command."""

        try:
            self.read()
        except Exception as exc:
            log.exception("Sending a command failed.", exc_info=exc)
            raise
        else:
            return []

###########
# Methods #
###########

    def reset(self):
        """Reset the dose and charge measurement values."""
        self.ask("RES")

    def execute_selftest(self):
        """Execute the DIAMENTOR selftest.

        :raises: *ValueError* if selftest fails
        """
        self.ask("TST")

##############
# Properties #
##############

    baudrate = Instrument.control(
        "BR", "BR%d",
        """Control the baudrate.

        :type: int, strictly in ``9600``, ``19200``, ``38400``, ``57600``, ``115200``

        The baudrate is changed after sending the respone.
        """,
        map_values=True,
        validator=strict_discrete_set,
        values={9600: 0,
                19200: 1,
                38400: 2,
                57600: 3,
                115200: 4,
                },
        check_set_errors=True,
        get_process=lambda v: int(v[2])
        )

    constancy_check_passed = Instrument.measurement(
        "G",
        """Get the DIAMENTOR electrical constancy check result (bool).""",
        map_values=True,
        values={True: "P", False: "F"},
        get_process=lambda v: v[1]
        )

    is_calibrated = Instrument.measurement(
        "CRC",
        """Get the calibration status (bool).""",
        get_process_list=lambda v: not int(v[1])
        )

    is_eeprom_ok = Instrument.measurement(
        "CRC",
        """Get the EEPROM CRC ok status (bool).""",
        get_process_list=lambda v: not int(v[0][3])
        )

    pressure = Instrument.control(
        "PRE", "PRE%04d",
        """Control the atmospheric pressure in hPa.

        :type: int, strictly from ``500`` to ``1500``, default: ``1013``

        It is used for the air density correction.
        """,
        validator=strict_range,
        values=[500, 1500],
        check_set_errors=True,
        get_process=lambda v: int(v[3:]),
        cast=int
        )

    id = Instrument.measurement(
        "PTW",
        """Get the firmware version (str) ("CRS x.xx")""",
        )

    measurement = Instrument.measurement(
        "M",
        """Get the measurement result.

        :return: dict

        :dict keys: ``dap``,
                    ``dap_rate``,
                    ``time``

        The result consists of the dose-area-product (DAP) and the  dose-area-product rate.
        The units of ``dap`` and ``dap_rate`` depend on the :attr:`dap_unit` property.
        Time is in seconds.
        """,
        get_process_list=lambda v: {"dap": float(v[0][1:]),
                                    "dap_rate": float(v[1]),
                                    "time": 60*int(v[2]) + int(v[3])
                                    }
        )

    serial_number = Instrument.measurement(
        "SER",
        """Get the serial number (int).""",
        get_process=lambda v: int(v[3:])
        )

    temperature = Instrument.control(
        "TMPA", "TMPA%02d",
        """Control the chamber temperature in degree Celsius.

        :type: int, strictly from ``0`` to ``70``, default: ``20``

        It is used for the air density correction.
        """,
        validator=strict_range,
        values=[0, 70],
        check_set_errors=True,
        get_process=lambda v: int(v[4:]),
        cast=int
        )

    dap_unit = Instrument.control(
        "U", "U%d",
        """Control the dose-area-product (DAP) unit.

        :type: str, strictly in ``cGycm2``, ``Gycm2``, ``uGym2``, ``Rcm2``

        - ``cGycm2`` selects cGy*cm²
        - ``Gycm2`` selects Gy*cm²
        - ``uGym2`` selects µGy*m²
        - ``Rcm2`` selects R*cm²
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={"cGycm2": 1,
                "Gycm2": 2,
                "uGym2": 3,
                "Rcm2": 4,
                },
        check_set_errors=True,
        get_process=lambda v: int(v[1:])
        )

    calibration_factor = Instrument.control(
        "KA", "KA%s",
        """Control the calibration factor of the measurement chamber in µGy*m²/s.

        :type: float, strictly from ``1E8`` to ``9.999E12``, default: ``1.0E9``

        The unit of the calibration factor is always µGy*m²/s.
        It is independent from the selected :attr:`dap_unit`.

        .. warning::
            Changing the calibration factor can lead to wrong measurements!

            The calibration factor of the last calibration can be found on
            a label on the case or in the calibration certificate
            of the DIAMENTOR chamber.
        """,
        validator=strict_range,
        values=[1E8, 9.999E12],
        check_set_errors=True,
        set_process=lambda v: f"{v:.4E}".replace('+', ''),  # remove '+' from scientific notation
        get_process=lambda v: float(v[2:])
        )

    correction_factor = Instrument.control(
        "KFA", "KFA%.3f",
        """Control the correction factor of the chamber.

        :type: float, strictly from ``0`` to ``9.999``, default: ``1.0``
        """,
        validator=strict_range,
        values=[0, 9.999],
        check_set_errors=True,
        get_process=lambda v: float(v[3:])
        )
