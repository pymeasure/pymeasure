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

.. |pypi_version| image:: https://img.shields.io/pypi/v/pymeasure
   :target: https://pypi.org/project/pymeasure/
   :alt: PyPI version

.. |python_versions| image:: https://img.shields.io/pypi/pyversions/pymeasure
   :alt: Supported Python versions

.. |ci| image:: https://github.com/pymeasure/pymeasure/actions/workflows/pymeasure_CI.yml/badge.svg
   :target: https://github.com/pymeasure/pymeasure/actions/workflows/pymeasure_CI.yml
   :alt: Continuous integration status

.. |docs| image:: https://app.readthedocs.org/projects/pymeasure/badge/?version=latest
   :target: https://pymeasure.readthedocs.io/en/latest/
   :alt: Documentation status

.. |coverage| image:: https://codecov.io/gh/pymeasure/pymeasure/graph/badge.svg
   :target: https://codecov.io/gh/pymeasure/pymeasure
   :alt: Code coverage

.. |conda_version| image:: https://anaconda.org/conda-forge/pymeasure/badges/version.svg
   :target: https://anaconda.org/conda-forge/pymeasure
   :alt: conda-forge version

.. |conda_downloads| image:: https://anaconda.org/conda-forge/pymeasure/badges/downloads.svg
   :target: https://anaconda.org/conda-forge/pymeasure
   :alt: conda-forge downloads

.. |doi| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.595633.svg
   :target: https://doi.org/10.5281/zenodo.595633
   :alt: Zenodo DOI

|pypi_version| |python_versions| |ci| |docs| |coverage| |conda_version| |conda_downloads| |doi|

.. _Issues page: https://github.com/pymeasure/pymeasure/issues


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
   :caption: API Reference

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
   dev/adding_instruments/index
   dev/coding_standards

.. _about-docs:

.. toctree::
   :maxdepth: 2
   :caption: About PyMeasure

   about/authors
   about/license
   about/changes
   about/related_projects
