.. _advanced_communication_protocols:

Advanced communication protocols
================================

Some devices require a more advanced communication protocol, e.g. due to checksums or device addresses. In most cases, it is sufficient to subclass :meth:`Instrument.write <pymeasure.instruments.Instrument.write>` and :meth:`Instrument.read <pymeasure.instruments.Instrument.read>`.


.. testsetup::

    # Behind the scene, replace Instrument with FakeInstrument to enable
    # doctesting simple usage cases (default doctest group)
    from pymeasure.instruments.fakes import FakeInstrument as Instrument

.. testsetup:: with-protocol-tests

    # If we want to run protocol tests on doctest code, we need to use a
    # separate doctest "group" and a different set of imports.
    # See https://www.sphinx-doc.org/en/master/usage/extensions/doctest.html
    from pymeasure.instruments import Instrument, Channel
    from pymeasure.test import expected_protocol


Instrument's inner workings
***************************

In order to adjust an instrument for more complicated protocols, it is key to understand the different parts.

The :class:`~pymeasure.adapters.Adapter` exposes :meth:`~pymeasure.adapters.Adapter.write` and :meth:`~pymeasure.adapters.Adapter.read` for strings, :meth:`~pymeasure.adapters.Adapter.write_bytes` and :meth:`~pymeasure.adapters.Adapter.read_bytes` for bytes messages. These are the most basic methods, which log all the traffic going through them. For the actual communication, they call private methods of the Adapter in use, e.g. :meth:`VISAAdapter._read <pymeasure.adapters.VISAAdapter._read>`.
For binary data, like waveforms, the adapter provides also :meth:`~pymeasure.adapters.Adapter.write_binary_values` and :meth:`~pymeasure.adapters.Adapter.read_binary_values`, which use the aforementioned methods.
You do not need to call all these methods directly, instead, you should use the methods of :class:`~pymeasure.instruments.Instrument` with the same name. They call the Adapter for you and keep the code tidy.

Now to :class:`~pymeasure.instruments.Instrument`. The most important methods are :meth:`~pymeasure.instruments.Instrument.write` and :meth:`~pymeasure.instruments.Instrument.read`, as they are the most basic building blocks for the communication. The pymeasure properties (:meth:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>` and its derivatives :meth:`Instrument.measurement <pymeasure.instruments.common_base.CommonBase.measurement>` and :meth:`Instrument.setting <pymeasure.instruments.common_base.CommonBase.setting>`) and probably most of your methods and properties will call them. In any instrument, :meth:`write` should write a general string command to the device in such a way, that it understands it. Similarly, :meth:`read` should return a string in a general fashion in order to process it further.

The getter of :meth:`Instrument.control <pymeasure.instruments.common_base.CommonBase.control>` does not call them directly, but via a chain of methods. It calls :meth:`~pymeasure.instruments.Instrument.values` which in turn calls :meth:`~pymeasure.instruments.Instrument.ask` and processes the returned string into understandable values. :meth:`~pymeasure.instruments.Instrument.ask` sends the readout command via :meth:`write`, waits some time if necessary via :meth:`wait_for`, and reads the device response via :meth:`read`.

Similarly, :meth:`Instrument.binary_values <pymeasure.instruments.Instrument.binary_values>` sends a command via :meth:`write`, waits with :meth:`wait_till_read`, but reads the response via :meth:`Adapter.read_binary_values <pymeasure.adapters.Adapter.read_binary_values>`.


Adding a device address and adding delay
****************************************

Let's look at a simple example for a device, which requires its address as the first three characters and returns the same style. This is straightforward, as :meth:`write` just prepends the device address to the command, and :meth:`read` has to strip it again doing some error checking. Similarly, a checksum could be added.
Additionally, the device needs some time after it received a command, before it responds, therefore :meth:`wait_for` waits always a certain time span.

.. testcode:: with-protocol-tests

    class ExtremeCommunication(Instrument):
        """Control the ExtremeCommunication instrument.

        :param address: The device address for the communication.
        :param query_delay: Wait time after writing and before reading in seconds.
        """
        def __init__(self, adapter, name="ExtremeCommunication", address=0, query_delay=0.1):
            super().__init__(adapter, name)
            self.address = f"{address:03}"
            self.query_delay = query_delay
    
        def write(self, command):
            """Add the device address in front of every command before sending it."""
            super().write(self.address + command)
    
        def wait_for(self, query_delay=0):
            """Wait for some time.

            :param query_delay: override the global query_delay.
            """
            super().wait_for(query_delay or self.query_delay)
    
        def read(self):
            """Read from the device and check the response.

            Assert that the response starts with the device address.
            """
            got = super().read()
            if got.startswith(self.address):
                return got[3:]
            else:
                raise ConnectionError(f"Expected message address '{self.address}', but read '{got[3:]}' for wrong address '{got[:3]}'.")
    
        voltage = Instrument.measurement(
            ":VOLT:?", """Measure the voltage in Volts.""")

.. testcode:: with-protocol-tests
    :hide:

    with expected_protocol(ExtremeCommunication, [("012:VOLT:?", "01215.5")], address=12
        ) as inst:
        assert inst.voltage == 15.5

If the device is initialized with :code:`address=12`, a request for the voltage would send :code:`"012:VOLT:?"` to the device and expect a response beginning with :code:`"012"`.


Bytes communication
*******************

Some devices do not expect ASCII strings but raw bytes. In those cases, you can call the :meth:`write_bytes` and :meth:`read_bytes` in your :meth:`write` and :meth:`read` methods. The following example shows an instrument, which has registers to be written and read via bytes sent.

.. testcode:: with-protocol-tests

    class ExtremeBytes(Instrument):
        """Control the ExtremeBytes instrument with byte-based communication."""
        def __init__(self, adapter, name="ExtremeBytes"):
            super().__init__(adapter, name)
    
        def write(self, command):
            """Write to the device according to the comma separated command.
    
            :param command: R or W for read or write, hexadecimal address, and data.
            """
            function, address, data = command.split(",")
            b = [0x03] if function == "R" else [0x10]
            b.extend(int(address, 16).to_bytes(2, byteorder="big"))
            b.extend(int(data).to_bytes(length=8, byteorder="big", signed=True))
            self.write_bytes(bytes(b))
    
        def read(self):
            """Read the response and return the data as a string, if applicable."""
            response = self.read_bytes(2)  # return type and payload
            if response[0] == 0x00:
                raise ConnectionError(f"Device error of type {response[1]} occurred.")
            if response[0] == 0x03:
                # read that many bytes and return them as an integer
                data = self.read_bytes(response[1])
                return str(int.from_bytes(data, byteorder="big", signed=True))
            if response[0] == 0x10 and response[1] != 0x00:
                raise ConnectionError(f"Writing to the device failed with error {response[1]}")
    
        voltage = Instrument.control(
            "R,0x106,1", "W,0x106,%i",
            """Control the output voltage in mV.""",
        )

.. testcode:: with-protocol-tests
    :hide:

    with expected_protocol(ExtremeBytes, [(b"\x03\x01\x06\x00\x00\x00\x00\x00\x00\x00\x01", b"\x03\x01\x0f")]) as inst:
        assert inst.voltage == 15
