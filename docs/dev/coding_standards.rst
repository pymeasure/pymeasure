################
Coding Standards
################

In order to maintain consistency across the different instruments in the PyMeasure repository, we enforce the following standards.

Python style guides
===================

Only Python 3 is used in PyMeasure. This prevents the maintaininace overhead of supporting Python 2.7,  which will lose official support in the future.

The `PEP8 style guide`_ and `PEP257 docstring conventions`_ should be followed.

.. _PEP8 style guide: https://www.python.org/dev/peps/pep-0008/
.. _PEP257 docstring conventions: https://www.python.org/dev/peps/pep-0257/

Function and variable names should be lower case with underscores as needed to seperate words. CamelCase should only be used for class names, unless working with Qt, where its use is common.

Documentation
=============

PyMeasure documents code using reStructuredText and the `Sphinx documentation generator`_. All functions, classes, and methods should be documented in the code using a `docstring`_.

.. _Sphinx documentation generator: http://www.sphinx-doc.org/en/stable/
.. _docstring: http://www.sphinx-doc.org/en/stable/ext/example_numpy.html?highlight=docstring


Usage of getter and setter functions
====================================

Getter and setter functions are discouraged, since properties provide a more fluid experience. Given the extensive tools avalible for defining properties, detailed in the :ref:`Advanced properties <advanced-properties>` section, these types of properties are prefered.
