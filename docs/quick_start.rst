###########
Quick start
###########

This section provides instructions for getting up and running quickly with PyMeasure.

.. _installing

Setting up Python
=================

The easiest way to install the necessary Python environment for PyMeasure is through the `Anaconda distribution`_, which includes 720 scientific packages. The advantage of using this approach over just relying on the :code:`pip` installer is that it Anaconda correctly installs the required Qt libraries. 

Download and install the appropriate Python 3.5 version of `Anaconda`_ for your operating system. 

.. _Anaconda distribution: https://www.continuum.io/why-anaconda
.. _Anaconda: https://www.continuum.io/downloads

Installing PyMeasure
====================

Now that you have Python installed, open up a "Jupyter Notebook". We will use this notebook to install the PyMeasure package with :code:`pip`, which you can alternatively do in the command-line. Run the following code in the notebook (here the "!" tells the notebook to run a terminal command instead of regular Python):

.. code-block:: none
    
    !pip install pymeasure

In another cell of the notebook, we can check the version number of PyMeasure by executing the following.

.. code-block:: python

    import pymeasure
    pymeasure.__version__

You should see the version of PyMeasure printed out. At this point you have PyMeasure installed, and you are ready to start using it! Are you ready to :doc:`connect to an instrument <./tutorial/connecting>`?