################
Coding Standards
################

In order to maintain consistency across the different instruments in the PyMeasure repository, we enforce the following standards.

Python style guides
===================

The `PEP8 style guide`_ and `PEP257 docstring conventions`_ should be followed.

.. _PEP8 style guide: https://www.python.org/dev/peps/pep-0008/
.. _PEP257 docstring conventions: https://www.python.org/dev/peps/pep-0257/

Function and variable names should be lower case with underscores as needed to seperate words. CamelCase should only be used for class names, unless working with Qt, where its use is common.

In addition, there is a configuration for the `flake8`_ linter present. Our codebase should not trigger any warnings.
Many editors/IDEs can run this tool in the background while you work, showing results inline. Alternatively, you can run ``flake8`` in the repository root to check for problems. In addition, our automation on Github also runs some checkers. As this results in a much slower feedback loop for you, it's not recommended to rely only on this.

.. _flake8: https://flake8.pycqa.org/en/latest/

There are no plans to support type hinting in PyMeasure code. This adds a lot of additional code to manage, without a clear advantage for this project. 
Type documentation should be placed in the docstring where not clear from the variable name.

Documentation
=============

PyMeasure documents code using reStructuredText and the `Sphinx documentation generator`_. All functions, classes, and methods should be documented in the code using a `docstring`_.

.. _Sphinx documentation generator: http://www.sphinx-doc.org/en/stable/
.. _docstring: https://www.sphinx-doc.org/en/master/usage/extensions/example_numpy.html?highlight=numpy+example


Usage of getter and setter functions
====================================

Getter and setter functions are discouraged, since properties provide a more fluid experience. Given the extensive tools avalible for defining properties, detailed in the :ref:`Advanced properties <advanced-properties>` section, these types of properties are prefered.
