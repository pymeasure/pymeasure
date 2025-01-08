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

from .adapter import Adapter


class TelnetAdapter(Adapter):
    """ Adapter class for using the Python telnetlib package to allow
    communication to instruments

    This Adapter has been removed from service as the underlying library is missing!

    .. deprecated:: 0.11.2
        The Python telnetlib module is deprecated since Python 3.11 and will be removed
        in Python 3.13 release.
        As a result, TelnetAdapter is deprecated, use VISAAdapter instead.
        The VISAAdapter supports TCPIP socket connections. When using the VISAAdapter,
        the `resource_name` argument should be `TCPIP[board]::<host>::<port>::SOCKET`.
        see here, <https://pyvisa.readthedocs.io/en/latest/introduction/names.html>
    """

    def __init__(self, host, port=0, query_delay=0, preprocess_reply=None,
                 **kwargs):
        raise NotImplementedError(
            "The TelnetAdapter has been removed, as the telnetlib module is deprecated. "
            "Use the VISAAdapter instead. The VISAAdapter supports TCPIP socket connections. "
            "When using the VISAAdapter, the `resource_name` argument should be "
            "`TCPIP[board]::<host>::<port>::SOCKET`. "
            "see here, <https://pyvisa.readthedocs.io/en/latest/introduction/names.html>")

    def __repr__(self):
        return "<TelnetAdapter()>"
