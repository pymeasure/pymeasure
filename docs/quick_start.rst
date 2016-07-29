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

Using the development version
=============================

If you are interested in using the development version to use the latest features or contribute to the code-base, then you will need `Git version control`_ installed. On Windows, we recommend `Github Desktop`_.

.. _Git version control: https://git-scm.com/
.. _GitHub Desktop: https://git-scm.com/downloads

Clone the :code:`ralph-group/pymeasure` master branch, which is the stable development branch. On macOS and Linux, this is performed by the following terminal commands, where you should choose a desired path.

.. code-block:: bash

    cd /path/for/code
    git clone https://github.com/ralph-group/pymeasure.git

If you had already installed PyMeasure using :code:`pip`, make sure to uninstall it before continuing.

.. code-block:: bash

    pip uninstall pymeasure

Install PyMeasure in the editable mode.

.. code-block:: none

    cd /path/for/code/pymeasure
    pip install -e .

This will allow you to edit the files of PyMeasure and see the changes reflected. Make sure to reset your notebook kernel or Python console when doing so.
