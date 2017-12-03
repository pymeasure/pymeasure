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
import re

from pymeasure.adapters.adapter import Adapter

class FakeScpiAdapter(Adapter):
    """
    A more advanced fake adapter for debugging purposes, that implements basic
    SCPI commands and acts as a simple key-value store or dictionary. This
    adapter can be used to test measurement scripts independent of the
    physical equipment or device under test.

    Set commands like ``"FREQ 100"`` store the value 100 for the key ``FREQ``,
    while a query like ``"FREQ?"`` will retrieve the stored value.

    It is also possible to set handlers to respond to queries and set commands,
    in order to use custom logic (e.g. to return a sequence of measurements
    for a test scenario).

    Limitations:

    - Abbreviated and unabbreviated commands are considered distinct. (But how
      would you use these inconsistently in an automation library?!)
    - Commands that set parts of data structures won't work. For example, if
      a command ``"DISP 1,5"`` sets channel 1 to option 5, and later
      ``"DISP 2,4"`` sets channel 2 to option 4, this adapter will only remember
      (2,4). (However, if a query with argument ``"DISP? 2"`` is sent, then
      this adapter will reply "4".) You can use handlers to get around this.
    - Integers in formats other than decimal will not be interpreted as
      numerical, but only as strings. (TODO: Implement other IEEE 488.2 integer
      formats).

    Example usage:

    .. literalinclude:: /api/example-FakeScpiAdapter.py
        :language: python

    :param default_value: Default value to return for queries to keys that have
        not been set. If None, then queries for unset keys will throw a
        KeyError.

    :param kwargs: Keyword arguments of the form ``CMDD=value``, where CMDD is
        the SCPI command mnemonic (key) and ``value`` is the initial value for
        queries to that key (i.e. ``"CMDD?"``) or, if a callable, the handler
        to set for that SCPI command mnemonic (key).
    """

    re_digit = re.compile('\d')

    def __init__(self, default_value=None, **kwargs):
        self._store = {}
        self._handlers = {}
        self._buffer = ""
        self.default_value = default_value
        for name, value in kwargs.items():
            if callable(value):
                self.set_handler(name, value)
            else:
                self.set_value(name, value)


    def set_value(self, key, value):
        """
        Set a value to a key. Used to preset values programmatically
        to set up test cases. If a handler is set to the same key, that handler
        will always take priority.

        :param str key: Key to set.
        :param value: Value to set. Normally a string, int or float, or tuple
            thereof.
        """
        self._store[key] = value


    def get_value(self, key):
        """
        Get the stored value for a key. Used to programmatically retrieve
        values set by SCPI commands, e.g., in custom handlers.

        :param str key: Key to retrieve.
        :return: Data for this key, as stored internally (numeric type when
            possible, else string, or a list thereof).
        """
        return self._store[key]


    def set_handler(self, key, handler):
        """
        Set a handler for a specific key. Handles both queries and commands
        using this key. The handler should be a callable with the signature:

        .. code-block:: python

            def handler(args: tuple(str), query: bool) -> str

        where both parameters are optional. ``args`` may be a tuple of int,
        float and strings corresponding to the SCPI command arguments, or None.
        ``query`` is True if the command is a query (of the form ``CMDD?``).
        The return value will be set as the response and may be ``None``.

        ``args`` arguments will be int if the original string could be converted
        otherwise float if possible, otherwise string.

        To remove a handler, pass ``None``.
        """
        if callable(handler):
            self._handlers[key] = handler
        elif handler is None:
            del self._handlers[key]
        else:
            raise TypeError("Invalid handler")


    def read(self):
        """
        Read simulated incoming data.
        """
        ret = self._buffer
        self._buffer = ""
        return ret


    def write(self, value):
        """
        Write a command to the simulated instrument.
        """
        for command in value.split(';'):
            self._handle_single_command(command)


    def _handle_single_command(self, command):
        """
        Handle a single command. This is used in case multiple commands are
        written separated by semicolons.

        :rtype:str
        :return: Response string (or empty string if none)
        """
        if '?' in command: # query commands
            command_parts = command.split('?', 1)
            key = command_parts[0].strip()
            args = self._parse_args(command_parts[1])

            if key in self._handlers:
                self.respond(self._handlers[key](args=args, query=True))
            else: # handle with store
                if key not in self._store:
                    if self.default_value is not None:
                        self.respond(self.default_value)
                    else:
                        raise KeyError('No stored values for "%s"' % command)
                elif len(args) == 0:
                    self.respond(self._store[key])
                else:
                    stored = self._store[key]
                    if len(stored) > len(args) and args == stored[0:len(args)]:
                        self.respond(stored[len(args):])
                    else:
                        raise KeyError('No matching parameters for "%s"' % command)

        else: # set commands
            # insert space before 1st arg - some equipment accepts numerical args w/o space
            first_digit_match = self.re_digit.search(command)
            if first_digit_match is not None:
                first_digit_index = first_digit_match.start()
                command = command[:first_digit_index] + ' ' + command[first_digit_index:]

            # split command and args
            command_parts = command.strip().split(' ', 1)
            key = command_parts[0].strip()
            if len(command_parts) > 1:
                args = self._parse_args(command_parts[1])
            else:
                args = tuple()

            if key in self._handlers:
                self.respond(self._handlers[key](args=args, query=False))
            elif args: # only if args specified
                self.set_value(key, args)
            # else noop



    def _parse_args(self, args_raw):
            args_str = tuple(arg.strip() for arg in args_raw.split(','))
            args = []
            for arg_str in args_str:
                try:
                    args.append(int(arg_str))
                except ValueError:
                    try:
                        args.append(float(arg_str))
                    except ValueError:
                        args.append(arg_str)
            return tuple(arg for arg in args)


    def respond(self, resp):
        """
        Set a response to send from the instrument. Response value can be
        a string, tuple, or object (objects will be converted via ``str()``).
        """
        if resp is None:
            return
        if isinstance(resp, str):
            self._buffer += resp
        else:
            try:
                self._buffer += ','.join(str(v) for v in resp) # lists, tuples, etc. - not str
            except TypeError:
                self._buffer += str(resp)
        self._buffer += '\n'


    def __repr__(self):
        return "<FakeScpiStorageAdapter>"
