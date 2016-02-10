<img alt="PyMeasure package" src="docs/images/PyMeasure.png" width="315" />

# PyMeasure #

PyMeasure makes measurements easy to set up and run. The package is composed of two parts: (1) a repository of instruments classes that make communicating and taking data easy, and (2) a system for running experiment procedures and graphing their data live.

PyMeasure is currently under active development, so please report any issues you experience to our [Issues page](https://github.com/ralph-group/pymeasure/issues).

### Getting started ###

Check out [the documentation]() for a [tutorial on getting started]().

There are a number of examples in the `examples` directory that can help you get up and running.

### Requirements ###

PyMeasure is designed only for Python 3. This is a deliberate move to switch code over to the new conventions, and remove the extra work of back-porting functionality.

PyMeasure builds on the success of two key Python packages.

[Numpy](https://github.com/numpy/numpy) - Numerical Python, which handles large data sets efficiently  
[Pandas](https://github.com/pydata/pandas) - An extension of Numpy that simplifies data management

There are a number of other packages that are required for specific functionality. 

For communicating with VISA instruments, the PyVISA package is required. PySerial is used for basic serial communication.

[PyVISA](https://github.com/hgrecco/pyvisa) - VISA instrument communication library   
[PySerial](https://github.com/pyserial/pyserial) - Serial communication library   

The live-plotting and user-interfaces require either PyQt4 or PySide, in combination with PyQtGraph.

[PyQt4](https://www.riverbankcomputing.com/software/pyqt/download) - Cross-platform Qt library for graphical user interfaces    
[PySide](https://github.com/PySide/PySide) - Alternative to PyQt4, licensed appropriately for commercial use   
[PyQtGraph](https://github.com/pyqtgraph/pyqtgraph) - Efficient live-plotting library   

For listening in on the experimental procedure execution through TCP messaging, the PyZMQ and MsgPack-Numpy libraries are required. This is not necessary for general use.

[PyZMQ](https://github.com/zeromq/pyzmq) - Message communication library   
[MsgPack-Numpy](https://github.com/lebedov/msgpack-numpy) - Compresses messages and handles Numpy arrays   

### Install: ###

Get the latest release from GitHub or install via the Python `pip` installer:

```shell
pip install pymeasure
```
