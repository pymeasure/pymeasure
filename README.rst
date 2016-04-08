.. image:: docs/images/PyMeasure.png

PyMeasure
#########

PyMeasure makes measurements easy to set up and run. The package is composed of two parts: (1) a repository of instruments classes that make communicating and taking data easy, and (2) a system for running experiment procedures and graphing their data live.

PyMeasure is currently under active development, so please report any issues you experience to our `Issues page`_.

.. image:: https://ci.appveyor.com/api/projects/status/hcj2n2a7l97wfbb8/branch/master?svg=true
    :target: https://ci.appveyor.com/project/cjermain/pymeasure

.. image:: https://travis-ci.org/ralph-group/pymeasure.svg?branch=master
    :target: https://travis-ci.org/ralph-group/pymeasure

Getting started
***************

Check out `the documentation`_ for a `tutorial on getting started`_.

There are a number of examples in the :code:`examples` directory that can help you get up and running.

Requirements
************

PyMeasure is a Python 3+ library, and does not support Python 2. This is a deliberate move to switch code over to the new conventions, and remove the extra work of back-porting functionality.

PyMeasure builds on the success of two key Python packages.

| `Numpy`_ - Numerical Python, which handles large data sets efficiently  
| `Pandas`_ - An extension of Numpy that simplifies data management
| 

There are a number of other packages that are required for specific functionality. 

For communicating with VISA instruments, the PyVISA package is required. PySerial is used for basic serial communication.

| `PyVISA`_ - VISA instrument communication library   
| `PySerial`_ - Serial communication library   
| 

The live-plotting and user-interfaces require either PyQt4 or PySide, in combination with PyQtGraph.

| `PyQt4`_ - Cross-platform Qt library for graphical user interfaces    
| `PySide`_ - Alternative to PyQt4, licensed appropriately for commercial use   
| `PyQtGraph`_ - Efficient live-plotting library   
| 

For listening in on the experimental procedure execution through TCP messaging, the PyZMQ and MsgPack-Numpy libraries are required. This is not necessary for general use.

| `PyZMQ`_ - Message communication library   
| `MsgPack Numpy`_ - Compresses messages and handles Numpy arrays   

Install:
********

Get the latest release from GitHub or install via the Python :code:`pip` installer:

.. code-block:: python
    
    pip install pymeasure



.. _the documentation: http://pymeasure.readthedocs.org/en/latest/
.. _tutorial on getting started: http://pymeasure.readthedocs.org/en/latest/getting_started.html
.. _Issues page: https://github.com/ralph-group/pymeasure/issues
.. _Numpy: https://github.com/numpy/numpy
.. _Pandas: https://github.com/pydata/pandas
.. _PyVISA: https://github.com/hgrecco/pyvisa
.. _PySerial: https://github.com/pyserial/pyserial
.. _PyQt4: https://www.riverbankcomputing.com/software/pyqt/download
.. _PySide: https://github.com/PySide/PySide
.. _PyQtGraph: https://github.com/pyqtgraph/pyqtgraph
.. _PyZMQ: https://github.com/zeromq/pyzmq
.. _MsgPack Numpy: https://github.com/lebedov/msgpack-numpy