###########
Quick start
###########

This section provides instructions for getting up and running quickly with PyMeasure.

Setting up Python
=================

The easiest way to install the necessary Python environment for PyMeasure is through the `Anaconda distribution`_, which includes 720 scientific packages. The advantage of using this approach over just relying on the :code:`pip` installer is that Anaconda correctly installs the required Qt libraries. 

Download and install the appropriate Python version of `Anaconda`_ for your operating system.

.. _Anaconda distribution: https://www.anaconda.com/
.. _Anaconda: https://www.anaconda.com/products/individual

Installing PyMeasure
====================

Install with conda
------------------

If you have the `Anaconda distribution`_ you can use the conda package manager to easily install PyMeasure and all required dependencies.

Open a terminal and type the following commands (on Windows look for the `Anaconda Prompt` in the Start Menu):

.. code-block:: bash

    conda config --add channels conda-forge
    conda install pymeasure

This will install PyMeasure and all the required dependencies. 

Install with ``pip``
--------------------

PyMeasure can also be installed with :code:`pip`. 

.. code-block:: bash

    pip install pymeasure
 
Depending on your operating system, using this method may require additional work to install the required dependencies, which include the Qt libraries.

Installing VISA
---------------
Typically, communication with your instrument will happen using PyVISA, which is installed automatically.
However, this needs a VISA implementation installed to handle device communication.
If you do not already know what this means, install the pure-Python :code:`pyvisa-py` package (using the same installation you used above).
If you want to know more, consult `the PyVISA documentation <https://pyvisa.readthedocs.io/en/latest/introduction/configuring.html>`__. 


Checking the version
--------------------

Now that you have Python and PyMeasure installed, open your python environment (e.g. a REPL or Jupyter notebook) to test which version you have installed.
Execute the following Python code.

.. code-block:: python

    import pymeasure
    pymeasure.__version__

You should see the version of PyMeasure printed out. At this point you have PyMeasure installed, and you are ready to start using it! Are you ready to :doc:`connect to an instrument <./tutorial/connecting>`?

.. warning::
    The release of numpy version 2 caused some compatibility issues.
    PyMeasure is compatible with version 2 as of PyMeasure version 0.14.
    To use PyMeasure with numpy>=2, you also ensure the dependencies are compatible.
    This means installing pandas>=2.2.2 and pint>0.23 (at the time of writing, pint needs to be installed directly from the github repository, as no numpy-2 compatible version has been released).
