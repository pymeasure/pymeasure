############
Contributing
############

Contributions to the instrument repository and the main code base are encouraged. Since the code is hosted on GitHub, contributions should be added by `forking the repository`_ and `submitting a pull request`_. Do not make your updates on the master branch. Instead `make a new branch`_ and work on that branch. To ensure consistency, follow the :doc:`coding standards for PyMeasure <coding_standards>`.

Unit testing is an important part of keeping the package running. When adding a feature that can be readily tested, include a unit test compatible with `py.test`_ so that our continuous integration services can ensure that your features are retained and do not conflict with existing behavior.

.. _`forking the repository`: https://help.github.com/articles/fork-a-repo/
.. _`submitting a pull request`: https://help.github.com/articles/using-pull-requests/
.. _`make a new branch`: https://help.github.com/articles/creating-and-deleting-branches-within-your-repository/
.. _`py.test`: http://pytest.org/latest/