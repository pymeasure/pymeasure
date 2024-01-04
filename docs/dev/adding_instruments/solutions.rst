.. _solutions:

Solutions for implementation challenges
=======================================

This is a list of less common challenges, their solutions, and example instruments.


General issues
**************

- Small numbers (<1e-5) are shown as 0 with :code:`%f`. If an instrument understands exponential notation, you can use :code:`%g`, which switches between floating point and exponential format, depending on the exponent.



Communication protocol issues
*****************************

- The instrument answers every message, even a setting command. You can set the setting's :code:`check_set_errors = True` parameter and redefine :func:`check_set_errors` to read an answer, see :class:`hcp.TC038D <pymeasure.instruments.hcp.TC038D>`
- Binary, frame-based communication, see :class:`hcp.TC038D <pymeasure.instruments.hcp.TC038D>`
- All replies have the same length, see :class:`aja.DCXS <pymeasure.instruments.aja.DCXS>`
- The device generates garbage messages at startup, cluttering the buffer, see :class:`aja.DCXS <pymeasure.instruments.aja.DCXS>`
- An instrument and its channel need to override `values`, but it has to use the correct `ask` method as well, see :class:`tcpowerconversion.CXN <pymeasure.instruments.tcpowerconversion.CXN>`



Channels
********

- Not all channels have the same features, see :class:`MKS937B <pymeasure.instruments.mksinst.mks937b.MKS937B>`
- Channel names in the communication (1, 2, 3) differ from front panel (A, B, C), see :class:`AdvantestR624X <pymeasure.instruments.advantest.advantestR624X.AdvantestR624X>`
- A family of instruments in which a property of the channels is different for different members of the family , see :class:`AnritsuMS464xB <pymeasure.instruments.anritsu.AnritsuMS464xB>`
- If you want to document the type of your instrument's channels (with a clickable link), check out the source of the :ref:`aimtti-landing-page` page.
