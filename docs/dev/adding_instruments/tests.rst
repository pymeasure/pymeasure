.. _tests:

Writing tests
=============

Tests are very useful for writing good code.
We have a number of tests checking the correctness of the pymeasure implementation.
Those tests (located in the :code:`tests` directory) are run automatically on our CI server, but you can also run them locally using :code:`pytest`.

When adding instruments, your primary concern will be tests for the *instrument driver* you implement.
We distinguish two groups of tests for instruments: the first group does not rely on a connected instrument.
These tests verify that the implemented instrument driver exchanges the correct messages with a device (for example according to a device manual).
We call those "protocol tests".
The second group tests the code with a device connected.

Implement device tests by adding files in the :code:`tests/instruments/...` directory tree, mirroring the structure of the instrument implementations.
There are other instrument tests already available that can serve as inspiration.


.. _protocol_tests:

Protocol tests
**************

In order to verify the expected working of the device code, it is good to test every part of the written code. The :func:`~pymeasure.test.expected_protocol` context manager (using a :class:`~pymeasure.adapters.ProtocolAdapter` internally) simulates the communication with a device and verifies that the sent/received messages triggered by the code inside the :code:`with` statement match the expectation.

.. code-block:: python

    import pytest

    from pymeasure.test import expected_protocol

    from pymeasure.instruments.extreme5000 import Extreme5000

    def test_voltage():
        """Verify the communication of the voltage getter."""
        with expected_protocol(
            Extreme5000,
            [(":VOLT 0.345", None),
             (":VOLT?", "0.3000")],
        ) as inst:
            inst.voltage = 0.345
            assert inst.voltage == 0.3

In the above example, the imports import the pytest package, the expected_protocol and the instrument class to be tested.

The first parameter, Extreme5000, is the class to be tested.

When setting the voltage, the driver sends a message (:code:`":VOLT 0.345"`), but does not expect a response (:code:`None`). Getting the voltage sends a query (:code:`":VOLT?"`) and expects a string response (:code:`"0.3000"`).
Therefore, we expect two pairs of send/receive exchange.
The list of those pairs is the second argument, the expected message protocol.

The context manager returns an instance of the class (:code:`inst`), which is then used to trigger the behaviour corresponding to the message protocol (e.g. by using its properties).

If the communication of the driver does not correspond to the expected messages, an Exception is raised.

.. note::
    The expected messages are **without** the termination characters, as they depend on the connection type and are handled by the normal adapter (e.g. :class:`VISAAdapter`).

Some protocol tests in the test suite can serve as examples:

* Testing a simple instrument: :code:`tests/instruments/keithley/test_keithley2000.py`
* Testing a multi-channel instrument: :code:`tests/instruments/tektronix/test_afg3152.py`
* Testing instruments using frame-based communication: :code:`tests/instruments/hcp/tc038.py`

Test generator
--------------

In order to facilitate writing tests, if you already have working code and a device at hand, we have a :class:`~pymeasure.generator.Generator` for tests.
You can control your instrument with the TestGenerator as a middle man.
It logs the method calls, the device communication and the return values, if any, and writes tests according to these log entries.

.. testsetup:: generator

    import io
    from pymeasure.adapters.protocol import ProtocolAdapter

    adapter = ProtocolAdapter(comm_pairs=[
        (b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),  # init
        (b'\x0201010INF6\x03', b'\x020101OKUT150333 V01.R001111222233334444\x03'),  # info
        (b'\x0201010WWRD0120,01,00C8\x03', b'\x020101OK\x03'),  # setpoint = 20
        (b'\x0201010WRDD0120,01\x03', b'\x020101OK00C8\x03'),  # setpoint == 20
        (b'\x0201010WWRD0120,01,0258\x03', b'\x020101OK\x03'),  # setpoint = 60
    ])

    class FakeIO(io.StringIO):
        def close(self):
            pass

        def really_close(self):
            super().close()

    file = FakeIO()

.. testcode:: generator

    from pymeasure.generator import Generator
    from pymeasure.instruments.hcp import TC038

    generator = Generator()
    inst = generator.instantiate(TC038, adapter, 'hcp', adapter_kwargs={'baud_rate': 9600})

As a first step, this code imports the Generator and generates a middle man instrument.
The :meth:`instantiate` method creates an instrument instance and logs the communication at startup.
The Generator creates a special adapter for the communication with the device.
It cannot inspect the instrument's :meth:`__init__`, however.
Therefore you have to specify the **all** connection settings via the :code:`adapter_kwargs` dictionary, even those, which are defined in :meth:`__init__`.
These adapter arguments are not written to tests.
If you have arguments for the instrument itself, e.g. a RS485 address, you may give it as a keyword argument.
These additional keyword arguments are included in the tests.

Now we can use :code:`inst` as if it were created the normal way, i.e. :code:`inst = TC038(adapter)`, where ``adapter`` is some resource string.
Having gotten and set some properties, and called some methods, we can write the tests to a file.

.. testcode:: generator

    inst.information  # returns the 'information' property, e.g. 'UT150333 V01.R001111222233334444'
    inst.setpoint = 20
    assert inst.setpoint == 20
    inst.setpoint = 60

    generator.write_file(file)

The following data will be written to :code:`file`:

.. testcode:: generator
    :hide:

    print(file.getvalue()[:-1])  # to strip the last newline char.
    file.really_close()

.. testoutput:: generator

    import pytest

    from pymeasure.test import expected_protocol
    from pymeasure.instruments.hcp import TC038


    def test_init():
        with expected_protocol(
                TC038,
                [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03')],
        ):
            pass  # Verify the expected communication.


    def test_information_getter():
        with expected_protocol(
                TC038,
                [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
                 (b'\x0201010INF6\x03', b'\x020101OKUT150333 V01.R001111222233334444\x03')],
        ) as inst:
            assert inst.information == 'UT150333 V01.R001111222233334444'


    @pytest.mark.parametrize("comm_pairs, value", (
        ([(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
          (b'\x0201010WWRD0120,01,00C8\x03', b'\x020101OK\x03')],
         20),
        ([(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
          (b'\x0201010WWRD0120,01,0258\x03', b'\x020101OK\x03')],
         60),
    ))
    def test_setpoint_setter(comm_pairs, value):
        with expected_protocol(
                TC038,
                comm_pairs,
        ) as inst:
            inst.setpoint = value


    def test_setpoint_getter():
        with expected_protocol(
                TC038,
                [(b'\x0201010WRS01D0002\x03', b'\x020101OK\x03'),
                 (b'\x0201010WRDD0120,01\x03', b'\x020101OK00C8\x03')],
        ) as inst:
            assert inst.setpoint == 20.0


.. _device_tests:

Device tests
************

It can be useful as well to test the code against an actual device. The necessary device setup instructions (for example: connect a probe to the test output) should be written in the header of the test file or test methods. There should be the connection configuration (for example serial port), too.
In order to distinguish the test module from protocol tests, the filename should be :code:`test_instrumentName_with_device.py`, if the device is called :code:`instrumentName`.

To make it easier for others to run these tests using their own instruments, we recommend to use :code:`pytest.fixture` to create an instance of the instrument class.
It is important to use the specific argument name :code:`connected_device_address` and define the scope of the fixture to only establish a single connection to the device.
This ensures two things:
First, it makes it possible to specify the address of the device to be used for the test using the :code:`--device-address` command line argument.
Second, tests using this fixture, i.e. tests that rely on a device to be connected to the computer are skipped by default when running pytest.
This is done to avoid that tests that require a device are run when none is connected.
It is important that all tests that require a connection to a device either use the :code:`connected_device_address` fixture or a fixture derived from it as an argument.

A simple example of a fixture that returns a connected instrument instance looks like this:

.. code-block:: python

    @pytest.fixture(scope="module")
    def extreme5000(connected_device_address):
        instr = Extreme5000(connected_device_address)
        # ensure the device is in a defined state, e.g. by resetting it.
        return instr

Note that this fixture uses :code:`connected_device_address` as an input argument and will thus be skipped by automatic test runs. 
This fixture can then be used in a test functions like this:

.. code-block:: python

    def test_voltage(extreme5000):
        extreme5000.voltage = 0.345
        assert extreme5000.voltage == 0.3

Again, by specifying the fixture's name, in this case :code:`extreme5000`, invoking :code:`pytest` will skip these tests by default.

It is also possible to define derived fixtures, for example to put the device into a specific state. Such a fixture would look like this:

.. code-block:: python

    @pytest.fixture
    def auto_scaled_extreme5000(extreme5000):
        extreme5000.auto_scale()
        return extreme5000

In this case, do not specify the fixture's scope, so it is called again for every test function using it.

To run the test, specify the address of the device to be used via the :code:`--device-address` command line argument and limit pytest to the relevant tests.
You can filter tests with the :code:`-k` option or you can specify the filename.
For example, if your tests are in a file called :code:`test_extreme5000_with_device.py`, invoke pytest with :code:`pytest -k extreme5000 --device-address TCPIP::192.168.0.123::INSTR"`.

There might also be tests where manual intervention is necessary. In this case, skip the test by prepending the test function with a :code:`@pytest.mark.skip(reason="A human needs to press a button.")` decorator.
