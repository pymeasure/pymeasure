######################################
R&S FSL spectrum analyzer
######################################

Connecting to the instrument via network
----------------------------------------
Once connected to the network, the instrument's IP address can be found by
clicking the "Setup" button and navigating to "General Settings" -> "Network
Address".  

It can then be connected like this:

.. code:: python

    from pymeasure.instruments.rohdeschwarz import FSL
    fsl = FSL("TCPIP::192.168.1.123::INSTR")

Getting and setting parameters
------------------------------

Most parameters are implemented as properties, which means they can be read and
written (getting and setting) in a consistent and simple way. If numerical
values are provided, base units are used (s, Hz, dB, ...). 
Alternatively, the values can also be provided with a unit, e.g. ``"1.5 GHz"``
or ``"1.5GHz"``. Return values are always numerical.

.. code:: python

    # Getting the current center frequency
    fsl.freq_center

    9000000000.0

.. code:: python

    # Changing it to 10 MHz by providing the numerical value 
    fsl.freq_center = 10e6

.. code:: python

    # Verifying:
    fsl.freq_center

    10000000.0

.. code:: python

    # Changing it to 9 GHz by providing a string and verifying the result
    fsl.freq_center = '9GHz'
    fsl.freq_center

    9000000000.0

.. code:: python

    # Setting the span to maximum
    fsl.freq_span = '7 GHz'

Reading a trace
---------------

We will read the current trace

.. code:: python

    x, y = fsl.read_trace()

Markers
-------

Markers are implemented as their own class. You can create them like
this:

.. code:: python

    m1 = fsl.create_marker()

Set peak exursion:

.. code:: python

    m1.peak_excursion = 3

Set marker to a specific position:

.. code:: python

    m1.x = 10e9

Find the next peak to the left and get the level:

.. code:: python

    m1.to_next_peak('left')
    m1.y

    -34.9349060059

Delta markers
~~~~~~~~~~~~~

Delta markers can be created by setting the appropriate keyword.

.. code:: python

    d2 = fsl.create_marker(is_delta_marker=True)
    d2.name

    'DELT2'

Example program
---------------

Here is an example of a simple script for recording the peak of a signal.

.. code:: python

    m1 = fsl.create_marker() # create marker 1

    # Set standard settings, set to full span
    fsl.continuous_sweep = False
    fsl.freq_span = '18 GHz'
    fsl.res_bandwidth = "AUTO"
    fsl.video_bandwidth = "AUTO"
    fsl.sweep_time = "AUTO"

    # Perform a sweep on full span, set the marker to the peak and some to that marker
    fsl.single_sweep()
    m1.to_peak()
    m1.zoom('20 MHz')

    # take data from the zoomed-in region
    fsl.single_sweep()
    x, y = fsl.read_trace()

.. autoclass:: pymeasure.instruments.rohdeschwarz.fsl.FSL
    :members:
    :show-inheritance: