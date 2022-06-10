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
                 "unknown (MB)": "MB",
                 "unknown (GB)": "GB",
                 "unknown (24)": "24",
                 "no gauge": "NG",
                 "no connection": "NC"}


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
        self._re_response = re.compile(fr"@{self.address:03d}ACK(.*)")
        # set address in commands via dynamic properties
        for prop in ["serial", "pressure1", "pressure2", "pressure3",
                     "pressure4", "pressure5", "pressure6", "all_pressures",
                     "combined_pressure1", "combined_pressure2",
                     "sensor_typeA", "sensor_typeB", "sensor_typeC", "unit"]:
            setattr(self, f"{prop}_command_process", self.command_process)

    def extract_reply(self, reply):
        """ preprocess_reply function which tries to extract <Response> from
        '@<aaa>ACK<Response>;FF'. If <Response> can not be identified the orignal string
        is returned.
        :param reply: reply string
        :returns: string with only the response, or the original string
        """
        r = self._re_response.search(reply)
        if r:
            return r.groups()[0]
        else:
            return reply

    def check_errors(self):
        reply = self.extract_reply(self.read())
        if not reply.startswith("ACK"):
            raise ValueError(f"invalid reply in check_errors {reply}")

    def command_process(self, cmd):
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
