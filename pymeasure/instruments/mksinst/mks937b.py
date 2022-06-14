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

import re

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from .adapters import MKSVISAAdapter


_sensor_types = {"Cold Cathode": "CC",
                 "Hot Cathode": "HC",
                 "Pirani": "PR",
                 "Convection Pirani": "CP",
                 "Capacitance Manometer": "CM",
                 "unknown (MB)": "MB",  # manual does not specify
                 "unknown (GB)": "GB",  # manual does not specify
                 "unknown (24)": "24",  # manual does not specify
                 "no gauge": "NG",
                 "no connection": "NC"}

_ion_gauge_status = {"Wait": "W",
                     "Off": "O",
                     "Protect": "P",
                     "Degas": "D",
                     "Control": "C",
                     "Rear panel Ctrl off": "R",
                     "HC filament fault": "H",
                     "No gauge": "N",
                     "Good": "G",
                     "NOT_IONGAUGE": "NAK152",
                     }


class MKS937B(Instrument):
    """ MKS 937B vacuum gauge controller

    :param adapter: pyvisa resource name of the instrument or an instance of
                    MKSSerialAdapter, or MKSVISAAdapter.
    :param address: device address included in every message to the instrument
                    (default=253)
    :param kwargs: Any valid key-word argument for Instrument
    """

    def __init__(self, adapter, address=253, **kwargs):
        kwargs.setdefault("preprocess_reply", self.extract_reply)
        if isinstance(adapter, str):
            adapter = MKSVISAAdapter(adapter, **kwargs)
        super().__init__(
            adapter,
            "MKS 937B vacuum gauge controller",
            includeSCPI=False,
            **kwargs
        )
        self.address = address
        # compiled regular expression for finding numerical values in reply strings
        self._re_fullresponse = re.compile(fr"@{self.address:03d}(.*)")
        self._re_response_value = re.compile(fr"@{self.address:03d}ACK(.*)")
        # set address in commands via dynamic properties
        for prop in ["serial", "pressure1", "pressure2", "pressure3",
                     "pressure4", "pressure5", "pressure6", "all_pressures",
                     "combined_pressure1", "combined_pressure2",
                     "sensor_typeA", "sensor_typeB", "sensor_typeC",
                     "ion_gauge_status1", "ion_gauge_status3",
                     "ion_gauge_status5", "unit",
                     "power_status1", "power_status2", "power_status3",
                     "power_status4", "power_status5", "power_status6",
                     ]:
            setattr(self, f"{prop}_command_process", self.command_process)

    def extract_reply(self, reply):
        """ preprocess_reply function which tries to extract <Response> from
        '@<aaa>ACK<Response>;FF'. If <Response> can not be identified the orignal string
        is returned.
        :param reply: reply string
        :returns: string with only the response, or the original string
        """
        rvalue = self._re_response_value.search(reply)
        if rvalue:
            return rvalue.groups()[0]
        else:
            full_reply = self._re_fullresponse.search(reply)
            if full_reply:
                return full_reply.groups()[0]
        return reply

    def check_errors(self):
        """
        check reply string for acknowledgement string
        """
        ret = self.read()
        reply = self._re_fullresponse.search(ret)
        if reply:
            if reply.groups()[0].startswith('ACK'):
                return
        # no valid acknowledgement message found
        raise ValueError(f"invalid reply '{ret}' found in check_errors")

    def command_process(self, cmd):
        """
        create command string by adding device address
        """
        return f"@{self.address:03d}{cmd}"

    serial = Instrument.measurement(
        "SN?", """ Serial number of the instrument """,
        cast=str,
        dynamic=True,
    )

    pressure1 = Instrument.measurement(
        "PR1?", """ Pressure on channel 1 in selected units """,
        dynamic=True,
    )

    pressure2 = Instrument.measurement(
        "PR2?", """ Pressure on channel 2 in selected units """,
        dynamic=True,
    )

    pressure3 = Instrument.measurement(
        "PR3?", """ Pressure on channel 3 in selected units """,
        dynamic=True,
    )

    pressure4 = Instrument.measurement(
        "PR4?", """ Pressure on channel 4 in selected units """,
        dynamic=True,
    )

    pressure5 = Instrument.measurement(
        "PR5?", """ Pressure on channel 5 in selected units """,
        dynamic=True,
    )

    pressure6 = Instrument.measurement(
        "PR6?", """ Pressure on channel 6 in selected units """,
        dynamic=True,
    )

    all_pressures = Instrument.measurement(
        "PRZ?", """ Read pressures on all channels in selected units """,
        dynamic=True,
    )

    combined_pressure1 = Instrument.measurement(
        "PC1?", """ Read pressure on channel 1 and its combination sensor """,
        dynamic=True,
    )

    combined_pressure2 = Instrument.measurement(
        "PC2?", """ Read pressure on channel 2 and its combination sensor """,
        dynamic=True,
    )

    sensor_typeA = Instrument.measurement(
        "STA?", """ show sensor types connected to module A """,
        map_values=True,
        values=_sensor_types,
        dynamic=True,
    )

    sensor_typeB = Instrument.measurement(
        "STB?", """ show sensor types connected to module B """,
        map_values=True,
        values=_sensor_types,
        dynamic=True,
    )

    sensor_typeC = Instrument.measurement(
        "STC?", """ show sensor types connected to module C """,
        map_values=True,
        values=_sensor_types,
        dynamic=True,
    )

    ion_gauge_status1 = Instrument.measurement(
        "T1?",
        """Ion gauge status of channel 1""",
        map_values=True,
        values=_ion_gauge_status,
        dynamic=True,
    )

    ion_gauge_status3 = Instrument.measurement(
        "T3?",
        """Ion gauge status of channel 3""",
        map_values=True,
        values=_ion_gauge_status,
        dynamic=True,
    )

    ion_gauge_status5 = Instrument.measurement(
        "T5?",
        """Ion gauge status of channel 5""",
        map_values=True,
        values=_ion_gauge_status,
        dynamic=True,
    )

    unit = Instrument.control(
        "U?", "U!%s",
        """Pressure unit used for all pressure readings from the instrument""",
        validator=strict_discrete_set,
        map_values=True,
        values={"Torr": "TORR",
                "mBar": "mBAR",
                "Pascal": "PASCAL",
                "Micron": "MICRON",
                },
        check_set_errors=True,
        dynamic=True,
    )

    power_status1 = Instrument.control(
        "CP1?", "CP1!%s",
        """Power status of channel 1""",
        validator=strict_discrete_set,
        values=["ON", "OFF"],
        check_set_errors=True,
        dynamic=True,
    )

    power_status2 = Instrument.control(
        "CP2?", "CP2!%s",
        """Power status of channel 2""",
        validator=strict_discrete_set,
        values=["ON", "OFF"],
        check_set_errors=True,
        dynamic=True,
    )

    power_status3 = Instrument.control(
        "CP3?", "CP3!%s",
        """Power status of channel 3""",
        validator=strict_discrete_set,
        values=["ON", "OFF"],
        check_set_errors=True,
        dynamic=True,
    )

    power_status4 = Instrument.control(
        "CP4?", "CP4!%s",
        """Power status of channel 4""",
        validator=strict_discrete_set,
        values=["ON", "OFF"],
        check_set_errors=True,
        dynamic=True,
    )

    power_status5 = Instrument.control(
        "CP5?", "CP5!%s",
        """Power status of channel 5""",
        validator=strict_discrete_set,
        values=["ON", "OFF"],
        check_set_errors=True,
        dynamic=True,
    )

    power_status6 = Instrument.control(
        "CP6?", "CP6!%s",
        """Power status of channel 6""",
        validator=strict_discrete_set,
        values=["ON", "OFF"],
        check_set_errors=True,
        dynamic=True,
    )
