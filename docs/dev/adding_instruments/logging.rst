.. _logging-instrument-communication:

Logging instrument communication
================================

Adapters log outgoing commands and incoming replies at Python's :code:`logging.DEBUG` level.
These messages can help you compare the communication with an instrument's programming manual when developing or debugging a driver.
They describe calls through the adapter, rather than capturing all traffic on the underlying connection.

Use :code:`instrument.adapter.log` to configure the logger used by your instrument.
Do not assume that it is named :code:`"Adapter"`: for example, :class:`~pymeasure.adapters.VISAAdapter` uses :code:`"pymeasure.adapters.visa.Adapter"`.
Adapters can share a logger, so configuring it can also affect other instruments using that logger.

Log to the console and a file
-----------------------------

The following example runs without hardware using :class:`~pymeasure.adapters.FakeAdapter`.
It echoes the command back as a reply; it does not simulate an instrument's identification response.
In your application, use your existing instrument instance in place of the example instrument.

.. testsetup::

    import os
    import tempfile

    original_directory = os.getcwd()
    temporary_directory = tempfile.TemporaryDirectory()
    os.chdir(temporary_directory.name)

.. testcode::

    import logging
    import sys

    from pymeasure.adapters import FakeAdapter
    from pymeasure.instruments import Instrument

    instrument = Instrument(FakeAdapter(), "Logging example")
    adapter_logger = instrument.adapter.log
    previous_level = adapter_logger.level
    previous_propagate = adapter_logger.propagate

    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler("communication.log", encoding="utf-8")
    handlers = (console_handler, file_handler)
    formatter = logging.Formatter("%(name)s %(levelname)s %(message)s")

    for handler in handlers:
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        adapter_logger.addHandler(handler)
    adapter_logger.setLevel(logging.DEBUG)
    adapter_logger.propagate = False

    try:
        reply = instrument.ask("*IDN?")
    finally:
        for handler in handlers:
            adapter_logger.removeHandler(handler)
            handler.close()
        adapter_logger.setLevel(previous_level)
        adapter_logger.propagate = previous_propagate

Both standard output and :code:`communication.log` receive:

.. testoutput::

    Adapter DEBUG WRITE:*IDN?
    Adapter DEBUG READ:*IDN?

.. testcode::
    :hide:

    from pathlib import Path

    assert reply == "*IDN?"
    assert Path("communication.log").read_text(encoding="utf-8").splitlines() == [
        "Adapter DEBUG WRITE:*IDN?",
        "Adapter DEBUG READ:*IDN?",
    ]
    assert all(handler not in adapter_logger.handlers for handler in handlers)
    assert adapter_logger.level == previous_level
    assert adapter_logger.propagate == previous_propagate

.. testcleanup::

    os.chdir(original_directory)
    temporary_directory.cleanup()

The file handler appends to the file by default.
The :code:`finally` block closes the handlers and restores the logger configuration even if communication raises an exception.
It leaves any previously installed handlers in place.

Troubleshooting
---------------

* Set both the logger and the handlers to :code:`logging.DEBUG`.
  A handler cannot display a message that the logger has already filtered out.
* :code:`logging.StreamHandler()` defaults to standard error; pass :code:`sys.stdout` to log to standard output as shown above.
* If messages appear twice, check whether handlers are attached both to the adapter logger and to its ancestors, such as the root logger.
  The example disables propagation while its handlers are attached to avoid that duplication.
  Also avoid repeatedly adding handlers without removing them, for example when rerunning a notebook cell.
* To capture commands sent during instrument initialization, configure the adapter's logger before constructing the instrument and pass that adapter instance to the instrument constructor.

For more logging options, see the `Python logging tutorial <https://docs.python.org/3/howto/logging.html>`__.
To turn an expected command/reply exchange into a repeatable test without hardware, see :ref:`tests`.
