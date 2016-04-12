Dependencies
============

PyMeasure is a Python 3+ library, and does not support Python 2. This is a deliberate move to switch code over to the new conventions, and remove the extra work of back-porting functionality.

Core dependencies
*****************

PyMeasure builds on the success of two key Python packages.

| `Numpy`_ - Numerical Python, which handles large data sets efficiently  
| `Pandas`_ - An extension of Numpy that simplifies data management
| 

Optional dependencies
*********************

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

.. _Numpy: https://github.com/numpy/numpy
.. _Pandas: https://github.com/pydata/pandas
.. _PyVISA: https://github.com/hgrecco/pyvisa
.. _PySerial: https://github.com/pyserial/pyserial
.. _PyQt4: https://www.riverbankcomputing.com/software/pyqt/download
.. _PySide: https://github.com/PySide/PySide
.. _PyQtGraph: https://github.com/pyqtgraph/pyqtgraph
.. _PyZMQ: https://github.com/zeromq/pyzmq
.. _MsgPack Numpy: https://github.com/lebedov/msgpack-numpy