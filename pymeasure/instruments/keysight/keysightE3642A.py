#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pymeasure.instruments import SCPIMixin, Instrument
from pymeasure.adapters.prologix import PrologixAdapter
from pymeasure.instruments.validators import strict_discrete_set


class KeysightE3642A(SCPIMixin, Instrument):
    def __init__(self, adapter, name="Keysight E3642A", **kwargs):
        super().__init__(
            adapter, name,
            **kwargs
        )

    output_state_enabled = Instrument.control(
        "OUTPUT:STATE?",
        "OUTPUT:STATE %d",
        """Control if output state is enabled""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    voltage = Instrument.control(
        "VOLT?",
        "VOLT %f",
        """Control the output voltage""",
    )

    current = Instrument.control(
        "CURR?",
        "CURR %f",
        """Control the output current""",
    )


if __name__ == "__main__":
    adapter = PrologixAdapter('ASRL3::INSTR')
    adapter.connection.read_termination = '\r\n'
    adapter.address = 5
    adapter.auto = True

    ps = KeysightE3642A(adapter)
    ps.output_state_enabled = True
    print(ps.output_state_enabled)
    ps.voltage = 5.31
    ps.current = 0.2



