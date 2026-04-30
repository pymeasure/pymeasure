Related Projects
================

PyMeasure is part of a broader ecosystem of laboratory automation tools:

- `LECO Protocol <https://github.com/pymeasure/leco-protocol>`_: Open standard for laboratory equipment communication using modern protocols
- `pyleco <https://github.com/pymeasure/pyleco>`_: Python library implementing LECO for distributed instrument control systems
- `Python Lab Automation Landscape <https://github.com/pymeasure/python-lab-automation-landscape>`_: Curated collection of Python tools for laboratory automation and instrumentation

These projects provide complementary capabilities to PyMeasure for building robust laboratory automation systems.

PyLECO in Detail
----------------

`PyLECO <https://github.com/pymeasure/pyleco>`_ is the Python reference implementation of the **Laboratory Experiment COntrol (LECO) protocol**.
It enables distributed instrument control by allowing multiple programs running on different computers to communicate and coordinate measurements.

Key concepts of PyLECO:

**Network Topology**
  A LECO network requires at least one *Coordinator* (server) that routes messages among connected *Components*.
  Each Component has a unique name consisting of its Coordinator's namespace and its own name (e.g. ``N1.component1``).
  Multiple Coordinators can be linked to form a network spanning several computers.

**Two Communication Protocols**
  - The *control protocol* routes messages between any two Components, enabling remote procedure calls (RPC) based on JSON-RPC.
  - The *data protocol* broadcasts data (e.g. measurement values or log entries) to all interested subscribers.

**Actors and Directors**
  An *Actor* wraps a PyMeasure instrument driver and listens for incoming RPC commands, controlling the device accordingly.
  A *Director* (e.g. ``TransparentDirector``) provides a transparent proxy: reading or writing ``director.device.voltage`` automatically sends the corresponding RPC to the remote Actor, which executes it on the real instrument.
  This allows instrument control from a separate process or machine without modifying the driver.

**Management Utilities**
  The *Starter* can launch and stop multiple Actor tasks in separate threads, simplifying the startup of complex setups.
  The *DataLogger* collects data broadcast via the data protocol for later analysis.

**Integration with PyMeasure**
  PyLECO works seamlessly with PyMeasure instrument drivers.
  Any PyMeasure driver can be controlled remotely by wrapping it in an ``Actor`` and accessing it through a ``TransparentDirector``.
  See the ``examples`` directory in the PyLECO repository for a ready-to-use actor template and measurement script.

**Installation**
  Install PyLECO with ``pip install pyleco`` or ``conda install conda-forge::pyleco``.
  A tutorial is available in the `GETTING_STARTED guide <https://github.com/pymeasure/pyleco/blob/main/GETTING_STARTED.md>`_.
