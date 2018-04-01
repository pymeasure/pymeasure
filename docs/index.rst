.. PyMeasure documentation master file, created by
   sphinx-quickstart on Mon Apr  6 13:06:00 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

############################
PyMeasure scientific package
############################

.. image:: images/PyMeasure.png
    :alt: PyMeasure Scientific package

PyMeasure makes scientific measurements easy to set up and run. The package contains a repository of instrument classes and a system for running experiment procedures, which provides graphical interfaces for graphing live data and managing queues of experiments. Both parts of the package are independent, and when combined provide all the necessary requirements for advanced measurements with only limited coding.

Installing Python and PyMeasure are demonstrated in the :doc:`Quick Start guide <quick_start>`. From there, checkout the existing :doc:`instruments that are available for use <api/instruments/index>`.

PyMeasure is currently under active development, so please report any issues you experience on our `Issues page`_.

.. image:: https://ci.appveyor.com/api/projects/status/hcj2n2a7l97wfbb8/branch/master?svg=true
    :target: https://ci.appveyor.com/project/cjermain/pymeasure

.. image:: https://travis-ci.org/ralph-group/pymeasure.svg?branch=master
    :target: https://travis-ci.org/ralph-group/pymeasure

.. image:: https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat
    :target: http://pymeasure.readthedocs.org/en/latest/

.. _Issues page: https://github.com/ralph-group/pymeasure/issues


The main documentation for the site is organized into a couple sections:

* :ref:`learning-docs`
* :ref:`api-docs`
* :ref:`about-docs`

Information about development is also available:

* :ref:`dev-docs`


.. _learning-docs:

.. toctree::
   :maxdepth: 2
   :caption: Learning PyMeasure

   introduction
   quick_start
   tutorial/index


.. _api-docs:

.. toctree::
   :maxdepth: 1
   :caption: API References

   api/adapters
   api/experiment/index
   api/display/index
   api/instruments/index

.. _dev-docs:

.. toctree::
   :maxdepth: 2
   :caption: Getting involved

   dev/contribute
   dev/reporting_errors
   dev/adding_instruments
   dev/coding_standards

.. _about-docs:

.. toctree::
   :maxdepth: 2
   :caption: About PyMeasure

   about/authors
   about/license

