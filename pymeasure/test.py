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

from contextlib import contextmanager

from pymeasure.adapters.protocol import ProtocolAdapter


@contextmanager
def expected_protocol(instrument_cls, comm_pairs,
                      connection_attributes=None, connection_methods=None,
                      **kwargs):
    """Context manager that checks sent/received instrument commands without a
    device connected.

    Given an instrument class and a list of command-response pairs, this
    context manager confirms that the code in the context manager block
    produces the expected messages.

    Terminators are excluded from the protocol definition, as those are
    typically a detail of the communication method (i.e. Adapter), and not the
    protocol itself.

    :param pymeasure.Instrument instrument_cls:
        :class:`~pymeasure.instruments.Instrument` subclass to instantiate.
    :param list[2-tuples[str]] comm_pairs:
        List of command-response pairs, i.e. 2-tuples like `('VOLT?', '3.14')`.
        'None' indicates that a pair member (command or response) does not
        exist, e.g. `(None, 'RESP1')`. Commands and responses are without
        termination characters.
    :param connection_attributes: Dictionary of connection attributes and their values.
    :param connection_methods: Dictionary of method names of the connection and their return values.
    :param \\**kwargs:
        Keyword arguments for the instantiation of the instrument.
    """
    protocol = ProtocolAdapter(comm_pairs, connection_attributes=connection_attributes,
                               connection_methods=connection_methods)
    instr = instrument_cls(protocol, **kwargs)
    yield instr
    assert protocol._index == len(comm_pairs), (
        "Unprocessed protocol definitions remain: "
        f"{comm_pairs[protocol._index:]}.")
    assert protocol._write_buffer is None, (
        f"Non-empty write buffer remains: '{protocol._write_buffer}'.")
    assert protocol._read_buffer is None, (
        f"Non-empty read buffer remains: '{protocol._read_buffer}'.")
