.. _adding-instruments:

##################
Adding instruments
##################

You can make a significant contribution to PyMeasure by adding a new instrument to the :code:`pymeasure.instruments` package. Even adding an instrument with a few features can help get the ball rolling, since its likely that others are interested in the same instrument.

Before getting started, become familiar with the :doc:`contributing work-flow <../contribute>` for PyMeasure, which steps through the process of adding a new feature (like an instrument) to the development version of the source code. This section will describe how to lay out your instrument code.

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


.. toctree::
   :maxdepth: 2

   instrument
   properties
   channels
   advanced_communication
   tests
