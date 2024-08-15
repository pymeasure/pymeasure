################
Coding Standards
################

In order to maintain consistency across the different instruments in the PyMeasure repository, we enforce the following standards.

Python style guides
===================

The `PEP8 style guide`_ and `PEP257 docstring conventions`_ should be followed.

.. _PEP8 style guide: https://www.python.org/dev/peps/pep-0008/
.. _PEP257 docstring conventions: https://www.python.org/dev/peps/pep-0257/

Function and variable names should be lower case with underscores as needed to separate words. CamelCase should only be used for class names, unless working with Qt, where its use is common.

In addition, there is a configuration for the `flake8`_ linter present. Our codebase should not trigger any warnings.
Many editors/IDEs can run this tool in the background while you work, showing results inline. Alternatively, you can run ``flake8`` in the repository root to check for problems. In addition, our automation on Github also runs some checkers. As this results in a much slower feedback loop for you, it's not recommended to rely only on this.

.. _flake8: https://flake8.pycqa.org/en/latest/

It is allowed but not required to use the `black`_ code formatter. 
To avoid introducing unrelated changes when working on an existing file, it is recommended to use the `darker`_ tool instead of `black`.
This helps to keep the focus on the implementation instead of unrelated formatting, and thereby facilitates code reviews.
:code:`darker` is compatible with :code:`black`, but only formats regions that show as changed in Git.
If there are conflicts between :code:`black`/:code:`darker`'s output and flake8 (especially related to `E203`_), flake8 takes precedence. Use ``#noqa : E203`` to disable E203 warnings for a specific line if appropriate.

.. _black: https://black.readthedocs.io/en/stable/
.. _darker: https://github.com/akaihola/darker
.. _E203: https://www.flake8rules.com/rules/E203.html

There are no plans to support type hinting in PyMeasure code. This adds a lot of additional code to manage, without a clear advantage for this project. 
Type documentation should be placed in the docstring where not clear from the variable name.

Documentation
=============

PyMeasure documents code using reStructuredText and the `Sphinx documentation generator`_. All functions, classes, and methods should be documented in the code using a docstring, see section :ref:`docstrings`.

.. _Sphinx documentation generator: http://www.sphinx-doc.org/en/stable/


Usage of getter and setter functions
====================================

Getter and setter functions are discouraged, since properties provide a more fluid experience.
Given the extensive tools available for defining properties, detailed in the sections starting with :ref:`properties`, these types of properties are preferred.


.. _docstrings:

Docstrings
==========
Descriptive and specific docstrings for your properties and methods are important for your users to quickly glean important information about a property.
It is advisable to follow the `PEP257 <https://peps.python.org/pep-0257/>`_ docstring guidelines.
Most importantly:

* Use triple-quoted strings (:code:`"""`) to delimit docstrings.
* One short summary line in imperative voice, with a period at the end.
* Optionally, after a blank line, include more detailed information.
* For functions and methods, you can add documentation on their parameters using the `reStructuredText docstring format <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html#info-field-lists>`__.

Specific to properties, start them with "Control", "Get", "Measure", or "Set" to indicate the kind of property, as it is not visible after import, whether a property is gettable ("Get" or "Measure"), settable ("Set"), or both ("Control").
In addition, it is useful to add type and information about :ref:`validators` (if applicable) at the end of the summary line, see the docstrings shown in examples throughout the :ref:`adding-instruments` section.
For example a docstring could be :code:`"""Control the voltage in Volts (float strictly from -1 to 1)."""`.

The docstring is for information that is relevant for *using* a property/method.
Therefore, do *not* add information about internal/hidden details, like the format of commands exchanged with the device.
