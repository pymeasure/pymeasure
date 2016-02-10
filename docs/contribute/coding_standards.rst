Coding Standards
================

In order to maintain consistency across the different instruments in the PyMeasure repository, we enforce the following standards.

Python style guides
###################

Python 3 is used in PyMeasure. The `PEP8 style guide`_ and `PEP257 docstring conventions`_ should be followed.

.. _PEP8 style guide: https://www.python.org/dev/peps/pep-0008/
.. _PEP257 docstring conventions: https://www.python.org/dev/peps/pep-0257/

Function and variable names should be lower case with underscores as needed to seperate words. Camel case should not be used, unless working with Qt, where it is common.

Standard naming
###############

Since many instruments have similar functions, a few naming conventions have been adopted to make the interface more consistent.

.. function names should be all lowercase with underbars if needed.

Usage of getter and setter
##########################
Many settings (such as range, enabled status, etc) are provided by the instrument with a pair of actions: one is to read the current setting value, the other is to assign a value to the setting. One can write two methods, get_setting() and set_setting() for instance, to handle these two actions; or altenatively use getter and setter decorators. In most cases, the two ways are equivalent. In order to incorporate different programming styles, and for the convenience of users, our convention is as follow:
- Write two functions get_setting() and set_setting(). The latter one should have only one non-keyword argument (but can have many keyword arguments).
- Define a property setting = property(get_setting, set_setting).

Using a buffer

.. code-block:: python

  set_buffer
  wait_for_buffer
  get_buffer
