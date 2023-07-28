#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

import io
import logging

from pymeasure.adapters import VISAAdapter
from pymeasure.instruments import Channel

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def write_generic_test(file, header_text, cls_name, comm_text,
                       test,
                       inkwargs=None):
    """Write a generic test.

    :param fileLike file: File to write to.
    :param list[str] header_text: Text of the header (parametrization, test name etc.)
    :param str cls_name: Name of the instrument class.
    :param list[str] comm_text: List of str of communication pairs
    :param str test: Test to assert for.
    :param dict[str, Any] inkwargs: Dictionary of instrument instantiation kwargs.
    """
    if inkwargs is None:
        args_text = "",
    else:
        args_text = [f'            {key}={repr(value)},\n' for key, value in inkwargs.items()]
    inst = " as inst" if "inst" in test else ""
    # file.writelines([
    #     "\n",
    #     "\n",
    #     *header_text,
    #     "    with expected_protocol(\n",
    #     f"            {cls_name},\n",
    #     *comm_text,
    #     *args_text,
    #     f"    ){inst}:\n",
    #     f"        {test}\n"
    # ])

    file.write(
        f"""

{''.join(header_text)}\
    with expected_protocol(
            {cls_name},
{''.join(comm_text)}\
{''.join(args_text)}\
    ){inst}:
        {test}
"""
    )


def write_test(file,
               test_name,
               cls_name,
               comm_pairs,
               test,
               inkwargs=None,
               ):
    """Write a single test.

    :param file: File to write to.
    :param str test_name: Name of the test.
    :param str cls_name: Name of the instrument class.
    :param list[tuple[bytes | None, bytes | None]] comm_pairs_list: List of communication pairs.
    :param str test: Test to assert for.
    :param dict[str, Any] inkwargs: Dictionary of instrument instantiation kwargs.
    """
    write_generic_test(
        file=file,
        header_text=[f"def test_{test_name.replace('.', '_')}():\n"],
        cls_name=cls_name,
        comm_text=[f"            {comm_pairs},\n".replace("), (", "),\n             (")],
        test=test,
        inkwargs=inkwargs,
    )


def write_parametrized_test(file,
                            test_name,
                            cls_name,
                            comm_pairs_list,
                            values_list,
                            test,
                            inkwargs=None,
                            ):
    """Write a parametrized test for properties.

    :param file: File to write to.
    :param str test_name: Name of the test.
    :param str cls_name: Name of the instrument class.
    :param list[list[tuple[bytes | None, bytes | None]]] comm_pairs_list: List of communication
        pairs list for each test.
    :param list[Any] values_list: List of expected values.
    :param str test: Test to assert for. :code:`'value'` is the expected parametrized value.
    :param dict inkwargs: Dictionary of instrument instantiation kwargs.
    """
    params = [f"    ({cp},\n     {v}),\n".replace(
        "), (", "),\n      (") for cp, v in zip(comm_pairs_list, values_list)]
    header_text = ['@pytest.mark.parametrize("comm_pairs, value", (\n',
                   *params,
                   "))\n",
                   f"def test_{test_name.replace('.', '_')}(comm_pairs, value):\n",
                   ]
    write_generic_test(file=file,
                       header_text=header_text,
                       cls_name=cls_name,
                       comm_text=["            comm_pairs,\n"],
                       test=test,
                       inkwargs=inkwargs,
                       )


def write_parametrized_method_test(file,
                                   test_name,
                                   cls_name,
                                   comm_pairs_list,
                                   args_list,
                                   kwargs_list,
                                   values_list,
                                   test,
                                   inkwargs=None,
                                   ):
    """Write a parametrized test for a method, taking in account additional arguments.

    :param file: File to write to.
    :param str name: Name of the test.
    :param str cls_name: Name of the instrument class.
    :param list[list[tuple[bytes | None, bytes | None]]] comm_pairs_list: List of communication
        pairs list for each test.
    :param list[tuple[Any, ...]] args_list: List of arguments lists for the method.
    :param list[dict[str, Any]] kwargs_list: List of keyword dictionaries for the method.
    :param list[Any] values_list: List of expected values.
    :param str test: Test to assert for. :code:`'value'` is the expected parametrized value.
    :param dict inkwargs: Dictionary of instrument instantiation kwargs.
    """
    z = zip(comm_pairs_list, args_list, kwargs_list, values_list)
    params = [f"    ({cp},\n     {a}, {k}, {v}),\n".replace(
        "), (", "),\n      (") for cp, a, k, v in z]
    header_text = ['@pytest.mark.parametrize("comm_pairs, args, kwargs, value", (\n',
                   *params,
                   "))\n",
                   f"def test_{test_name.replace('.', '_')}(comm_pairs, args, kwargs, value):\n",
                   ]
    write_generic_test(
        file=file,
        cls_name=cls_name,
        header_text=header_text,
        comm_text=["            comm_pairs,\n"],
        test=test,
        inkwargs=inkwargs
    )


def parse_stream(stream):
    """
    Parse the data stream.

    It is expected, that a message is always written in one write, while
    reading may extend over several reads, e.g. reading bytes.

    :return list[tuple[bytes | None, bytes | None]]: List of communication pairs
    """
    comm = []
    lines = stream.readlines()
    write = None
    read = None
    mode = None
    for line in lines:
        if line.startswith(b"WRITE:"):
            # Store the last comm_pair unless there is none.
            if write is not None or read is not None:
                comm.append((write, read))
                read = None
            write = line[6:-1]
            mode = "W"
        elif line.startswith(b"READ:"):
            if read is not None:
                read += line[5:-1]
            else:
                read = line[5:-1]
            mode = "R"
        else:
            # newline due to "\n" character in communication
            if mode == "W":
                write += b"\n" + line[:-1]
            elif mode == "R":
                read += b"\n" + line[:-1]
            else:
                raise ValueError("Very first line does not contain 'WRITE' or 'READ'!")
    if read is not None or write is not None:
        comm.append((write, read))
    return comm


class ByteFormatter(logging.Formatter):
    """Logging formatter with bytes values for the test generation."""

    @staticmethod
    def make_bytes(value):
        if isinstance(value, (bytes, bytearray)):
            return value
        if isinstance(value, str):
            return value.encode()
        raise ValueError(f"value '{value}' is neither str nor bytes.")

    def format(self, record):
        return b"".join((record.msg.replace(r"%s", "").encode(),
                         *[self.make_bytes(arg) for arg in record.args]))  # type: ignore


class ByteStreamHandler(logging.StreamHandler):
    """Logging handler using bytes streams."""

    terminator = b"\n"  # type: ignore

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formatter = ByteFormatter()


class TestInstrument:
    """A man-in-the-middle instrument, which logs property access and method calls.

    :param instrument: The real instrument, given by the generator.
    :param generator: The generator which writes the tests.
    :param name: Name in case of a channel with trailing period, for example :code:`"ch_1."`.
    """

    def __init__(self, instrument, generator, name=""):
        self._inst = instrument
        self._generator = generator
        self._name = name

    def __getattr__(self, name):
        if name.startswith("_"):
            # return private and special attributes to prevent recursion
            return super().__getattribute__(name)
        elif name == "adapter":
            # transparently return the instrument's adapter without writing tests
            return self._inst.adapter
        else:
            # transparently get the attribute from the instrument and write an appropriate test
            value = getattr(self._inst, name)
            if callable(value):
                # the attribute is a callable, we have to return a special method which writes the
                # test while returning the value
                def test_method(*args, **kwargs):
                    return self._generator._test_method(value, self._name + name, *args, **kwargs)
                return test_method
            elif isinstance(value, Channel):
                # the attribute is not a property or method, but a Channel, return a TestInstrument
                return TestInstrument(value, self._generator, f"{self._name}{name}.")
            else:
                # the attribute is a plain property, return the value and write a test
                self._generator._store_property_getter_test(self._name + name, value)
                return value

    def __setattr__(self, name, value):
        if name.startswith("_"):
            # set private and special attributes to prevent recursion
            super().__setattr__(name, value)
        else:
            # set an attribute transparently while writing a test
            setattr(self._inst, name, value)
            self._generator._store_property_setter_test(self._name + name, value)

    def __dir__(self):
        # To get autocompletion support for instrument members.
        return super().__dir__() + dir(self._inst)


class Generator:
    """
    Generates tests from the communication with an instrument.

    Example usage:

    .. code::

        g = Generator()
        inst = g.instantiate(TC038, "COM5", 'hcp', adapter_kwargs={'baud_rate': 9600})
        inst.information  # returns the 'information' property and adds it to the tests
        inst.setpoint = 20
        inst.setpoint == 20  # should be True
        g.write_file("test_tc038.py")  # write the tests to a file
    """

    def __init__(self):
        self._stream = io.BytesIO()
        self._index = 0
        self._init_comm_pairs = []  # Initializiation comm_pairs
        # Dictionaries for parametrized tests
        self._getters = {}
        self._setters = {}
        self._calls = {}

    def write_init_test(self, file):
        """Write the header and init test."""
        file.write(self._header)
        write_test(file, "init", self._class, self._init_comm_pairs,
                   "pass  # Verify the expected communication.",
                   self._inkwargs,
                   )

    def write_getter_test(self, file, property, parameters):
        """Write a getter test."""
        if len(parameters[0]) == 1:
            v = parameters[1][0]
            comparison = "is" if isinstance(v, bool) or v is None else "=="
            write_test(file,
                       test_name=property.replace(".", "_") + "_getter",
                       cls_name=self._class,
                       comm_pairs=parameters[0][0],
                       test=f"assert inst.{property} {comparison} {v}",
                       inkwargs=self._inkwargs,
                       )
        else:
            write_parametrized_test(file,
                                    test_name=property.replace(".", "_") + "_getter",
                                    cls_name=self._class,
                                    comm_pairs_list=parameters[0],
                                    values_list=parameters[1],
                                    test=f"assert inst.{property} == value",
                                    inkwargs=self._inkwargs,
                                    )

    def write_setter_test(self, file, property, parameters):
        """Write a setter test."""
        if len(parameters[0]) == 1:
            v = parameters[1][0]
            write_test(file,
                       test_name=property.replace(".", "_") + "_setter",
                       cls_name=self._class,
                       comm_pairs=parameters[0][0],
                       test=f"inst.{property} = {v}",
                       # inkwargs=self._inkwargs,  TODO
                       )
        else:
            write_parametrized_test(file,
                                    test_name=property.replace(".", "_") + "_setter",
                                    cls_name=self._class,
                                    comm_pairs_list=parameters[0],
                                    values_list=parameters[-1],
                                    test=f"inst.{property} = value",
                                    inkwargs=self._inkwargs,
                                    )

    def write_method_test(self, file, method, parameters):
        """Write a test for a method."""
        if len(parameters[0]) == 1:
            v = parameters[-1][0]
            comparison = "is" if isinstance(v, bool) or v is None else "=="
            arg_string = f"*{parameters[1][0]}, " if parameters[1][0] else ""
            kwarg_string = f"**{parameters[2][0]}" if parameters[2][0] else ""
            write_test(file,
                       test_name=method.replace(".", "_"),
                       cls_name=self._class,
                       comm_pairs=parameters[0][0],
                       test=f"assert inst.{method}({arg_string}{kwarg_string}) {comparison} {v}",
                       inkwargs=self._inkwargs,
                       )
        else:
            write_parametrized_method_test(file,
                                           test_name=method.replace(".", "_"),
                                           cls_name=self._class,
                                           comm_pairs_list=parameters[0],
                                           args_list=parameters[1],
                                           kwargs_list=parameters[2],
                                           values_list=parameters[-1],
                                           test=f"assert inst.{method}(*args, **kwargs) == value",
                                           inkwargs=self._inkwargs,
                                           )

    def write_property_tests(self, file):
        """Write tests for properties in alphabetic order.

        If getter and setter exist, the setter is the first test.
        """
        # Get a sorted list of all properties, without repeating them
        property_names = sorted(set(self._getters.keys() | set(self._setters.keys())))
        for property in property_names:
            if property in self._setters:
                self.write_setter_test(file, property, self._setters[property])
            if property in self._getters:
                # new condition (not elif), as properties can be in setters and in getters tests.
                self.write_getter_test(file, property, self._getters[property])

    def write_method_tests(self, file):
        """Write all parametrized method tests in alphabetic order."""
        for method in sorted(self._calls.keys()):
            self.write_method_test(file, method, self._calls[method])

    def write_file(self, filename="tests.py"):
        """Write the tests into the file.

        :param filename: Name to save the tests to, may contain the path, e.g. "/tests/test_abc.py".
        """
        file = filename if isinstance(filename, io.StringIO) else open(filename, "w")
        self.write_init_test(file)
        self.write_property_tests(file)
        self.write_method_tests(file)
        file.close()

    def parse_stream(self):
        """Parse the stream not yet read."""
        self._stream.seek(self._index)
        comm = parse_stream(self._stream)
        self._index = self._stream.tell()
        return self._init_comm_pairs + comm

    def instantiate(self, instrument_class, adapter, manufacturer, adapter_kwargs=None, **kwargs):
        """
        Instantiate the instrument and store the instantiation communication.

        ..note::

            You have to give all keyword arguments necessary for adapter instantiation in
            `adapter_kwargs`, even those, which are defined somewhere in the instrument's
            ``__init__`` method, be it as a default value, be it directly in the
            ``Instrument.__init__()`` call.

        :param instrument_class: Class of the instrument to test.
        :param adapter: Adapter (instance or str) for the instrument instantiation.
        :param manufacturer: Module from which to import the instrument, e.g. 'hcp' if
            instrument_class is 'pymeasure.hcp.tc038'.
        :param adapter_kwargs: Keyword arguments for the adapter instantiation (see note above).
        :param \\**kwargs: Keyword arguments for the instrument instantiation.
        :return: A man-in-the-middle instrument, which can be used like a normal instrument.
        """
        self._class = instrument_class.__name__
        log.info(f"Instantiate {self._class}.")
        self._header = (
            "import pytest\n\n"
            "from pymeasure.test import expected_protocol\n"
            f"from pymeasure.instruments.{manufacturer} import {self._class}\n")
        if isinstance(adapter, (int, str)):
            if adapter_kwargs is None:
                adapter_kwargs = {}
            try:
                adapter = VISAAdapter(adapter, **adapter_kwargs)
            except ImportError:
                raise Exception("Invalid Adapter provided for Instrument since"
                                " PyVISA is not present")
        adapter.log.addHandler(ByteStreamHandler(self._stream))
        adapter.log.setLevel(logging.DEBUG)
        self.inst = instrument_class(adapter, **kwargs)
        self._init_comm_pairs = self.parse_stream()  # communication of instantiation.
        self._inkwargs = kwargs  # instantiation kwargs
        self.test_inst = TestInstrument(self.inst, self)
        return self.test_inst

    def _store_property_getter_test(self, property, value):
        """Store the property getter test with returned `value`."""
        comm = self.parse_stream()
        if property not in self._getters:
            self._getters[property] = [], []
        c, v = self._getters[property]
        c.append(comm)
        v.append(f"\'{value}\'" if isinstance(value, str) else value)
        return value

    def test_property_getter(self, property):
        """Test getting the `property` of the instrument, adding it to the list."""
        log.info(f"Test property {property} getter.")
        value = getattr(self.inst, property)
        self._store_property_getter_test(property, value)
        return value

    def _store_property_setter_test(self, property, value):
        """Store the property setter test with `value`."""
        comm = self.parse_stream()
        if property not in self._setters:
            self._setters[property] = [], []
        c, v = self._setters[property]
        c.append(comm)
        v.append(f"\'{value}\'" if isinstance(value, str) else value)

    def test_property_setter(self, property, value):
        """Test setting the `property` of the instrument to `value`, adding it to the list."""
        log.info(f"Test property {property} setter.")
        setattr(self.inst, property, value)
        self._store_property_setter_test(property, value)

    def _test_method(self, method, method_name, *args, **kwargs):
        """Test calling `method` with the full `method_name` and `args` and `kwargs`."""
        value = method(*args, **kwargs)
        comm = self.parse_stream()
        if method_name not in self._calls:
            self._calls[method_name] = [], [], [], []
        c, a, k, v = self._calls[method_name]
        c.append(comm)
        a.append(args)
        k.append(kwargs)
        v.append(f"\'{value}\'" if isinstance(value, str) else value)
        return value

    def test_method(self, method_name, *args, **kwargs):
        """Test calling the `method_name` of the instruments with `args` and `kwargs`."""
        log.info(f"Test method {method_name}.")
        method = getattr(self.inst, method_name)
        return self._test_method(method, method_name, *args, **kwargs)

    # batch tests
    def test_property_setter_batch(self, property, values):
        """Test setting `property` to each element in `values`."""
        for value in values:
            self.test_property_setter(property, value)
