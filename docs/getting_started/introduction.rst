Introduction
============

The :code:`pymeasure` package uses an object oriented approach for communicating with instruments, which provides a more intuitive interface through the encapsulation of low level SCPI commands. That way you can focus on solving the measurement problems at hand, instead of re-inventing how to communicate with them. 

Instruments with VISA (GPIB, Serial, etc) are supported through the `PyVISA package`_ under the hood. `Prologix GPIB`_ adapters are also supported.

.. _PyVISA package: http://pyvisa.readthedocs.org/en/master/
.. _Prologix GPIB: http://prologix.biz/

Before using PyMeasure, you should be acquainted with `basic Python programming for the sciences`_ and understand the concept of objects.

.. _basic Python programming for the sciences: https://scipy-lectures.github.io/