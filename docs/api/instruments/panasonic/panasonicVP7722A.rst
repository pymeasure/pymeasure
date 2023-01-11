#################################
Panasonic VP-7722A Audio Analyzer
#################################
.. currentmodule:: pymeasure.instruments.panasonic.panasonicVP7722A

.. contents::

**********************************************
General Information
**********************************************

The VP-7722A Audio Analyzer is a measuring instrument with functions to
measure ten items including the frequency, level, distortion, S/N ratio,
and signal average and has a measuring signal source. An audio measuring
system featuring low noise, a high accuracy, and an excellent measuring
efficiency can be built by combining the signal source and various measuring
functions. One feature of this instrument is the measurement of distortion
factor. The true distortion below the noise level which cannot be measured by
conventional distortion meters can be measured using the digital signal
processing techniques. This instrument can also perform a harmonic
analysis for making it easy to measure extremely low distortion factors.

The GP-IB interface is used for remote setting and sending of measured
data. The GP-IP interface and memory control interface, which is proprietary
to this instrument, are equipped as standard interfaces to remote control
this instrument.

The GP-IB interface function allows oscillator frequency, output amplitude,
IMD test signal mixing ratio, measurement mode, measurement range, memory
function, etc. to be set by program codes.

It also allows to send the measured results and panel setups by selecting
a sending format by program codes. Eight formats are selectable for
various measurements such as frequency, input level and distortion.

.. note::
    The analyzer does not have a device trigger function. Alternatively, the
    analyzer has Pseudo-trigger function :meth:`PanasonicVP7722A.trigger_measurement`. 
    This function enables the controller to get the measured data at the time 
    when the controller sents a pseudo-trigger to the analyzer.

.. autoclass:: pymeasure.instruments.panasonic.PanasonicVP7722A
    :members:
    :show-inheritance: