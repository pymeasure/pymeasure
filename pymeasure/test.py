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

from contextlib import contextmanager

from pymeasure.adapters.protocol import ProtocolAdapter


@contextmanager
def expected_protocol(instrument_cls, comm_pairs):
    """Context manager that checks sent/received instrument commands without a device connected.

    Given an instrument class and a list of command-response pairs, this context
    manager confirms that the code in the context manager block produces the expected
    messages.

    Terminators are excluded from the protocol definition, as those are typically a detail of the
     communication method (i.e. Adapter), and not the protocol.

    Parameters
    ----------
    instrument_cls : `~pymeasure.Instrument`
        `~pymeasure.Instrument` subclass to instantiate
    comm_pairs : list[2-tuples[str]]
        List of command-response pairs, i.e. 2-tuples like `('VOLT?', '3.14')`.
        A tuple of length 1, e.g. `('MYCMD',)`, represents a command without expected response.
        To represent a response-only communication, use `None` for the command part,
         e.g. `(None, 'RESP1')`.
    """
    protocol = ProtocolAdapter(comm_pairs)
    instr = instrument_cls(protocol, name="Virtual instrument")
    yield instr
    assert protocol._index == len(comm_pairs), "Not all messages exchanged."
    assert protocol._write_buffer == b"", "Non empty write buffer."
    assert protocol._read_buffer == b"", "Non empty read buffer."

    # TODO: Make this skeleton implementation produce reasonable tests
    # TODO: Assert correct state of comm_pairs after yield
    # TODO: Enable user query for responses
    # TODO: Add explanatory documentation with examples in :doc:`adding-instruments`
