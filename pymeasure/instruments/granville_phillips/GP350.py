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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from pymeasure.instruments import Instrument, Channel


class GP_PressureChannel(Channel):
    """Channel of the GP350 vacuum sensor for pressure measurement.
    Each channel corresponds to a filament or display output of the sensor."""
    pressure = Instrument.measurement(
        "#RD{ch}",
        "Measure the current pressure in mbar (float).",
        preprocess_reply=lambda reply: reply.lstrip("* ").strip(),
        get_process=lambda r: float("nan") if float(r) >= 9.90e9 else float(r),
    )


class GP350(Instrument):
    """Representation of the GP350 Vacuum Sensor.
    Provides access to multiple pressure channels corresponding to filaments
    and display outputs. Each channel can be queried for its current pressure in mbar.
    Parameters
    ----------
    adapter : Adapter
        Communication adapter (e.g., SerialAdapter, VISAAdapter).
    name : str, optional
        Name of the instrument, default is "GP350 Vacuum Sensor".
    kwargs
        Additional keyword arguments passed to the Instrument base class."""
    def __init__(self, adapter, name="GP350 Vacuum Sensor", **kwargs):
        super().__init__(adapter, name, includeSCPI=False, **kwargs)
    filament_1 = Instrument.ChannelCreator(GP_PressureChannel, "1")
    filament_2 = Instrument.ChannelCreator(GP_PressureChannel, "2")
    display_A = Instrument.ChannelCreator(GP_PressureChannel, "A")
    display_B = Instrument.ChannelCreator(GP_PressureChannel, "B") can you format it so that it gets to the docstring test in pymeasure
