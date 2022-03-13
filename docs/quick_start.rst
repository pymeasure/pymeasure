###########
Quick start
###########

This section provides instructions for getting up and running quickly with PyMeasure.

Setting up Python
=================

The easiest way to install the necessary Python environment for PyMeasure is through the `Anaconda distribution`_, which includes 720 scientific packages. The advantage of using this approach over just relying on the :code:`pip` installer is that it Anaconda correctly installs the required Qt libraries. 

Download and install the appropriate Python version of `Anaconda`_ for your operating system.

.. _Anaconda distribution: https://www.anaconda.com/
.. _Anaconda: https://www.anaconda.com/products/individual

Installing PyMeasure
====================

Install with conda
------------------

If you have the `Anaconda distribution`_ you can use the conda package mangager to easily install PyMeasure and all required dependencies.

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
 
Depending on your operating system, using this method may require additional work to install the required dependencies, which include the Qt libaries.

    
Checking the version
--------------------

Now that you have Python and PyMeasure installed, open up a "Jupyter Notebook" to test which version you have installed. Execute the following code into a notebook cell.

.. code-block:: python

    import pymeasure
    pymeasure.__version__

You should see the version of PyMeasure printed out. At this point you have PyMeasure installed, and you are ready to start using it! Are you ready to :doc:`connect to an instrument <./tutorial/connecting>`?
