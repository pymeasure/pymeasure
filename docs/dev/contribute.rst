############
Contributing
############

Contributions to the instrument repository and the main code base are highly encouraged. This section outlines the basic work-flow for new contributors.

Using the development version
=============================

New features are added to the development version of PyMeasure, hosted on `GitHub`_. We use `Git version control`_ to track and manage changes to the source code. On Windows, we recommend using `GitHub Desktop`_. Make sure you have an appropriate version of Git (or GitHub Desktop) installed and that you have a GitHub account.

.. _GitHub: https://github.com/
.. _Git version control: https://git-scm.com/
.. _GitHub Desktop: https://git-scm.com/downloads

In order to add your feature, you need to first `fork`_ PyMeasure. This will create a copy of the repository under your GitHub account.

.. _fork: https://help.github.com/articles/fork-a-repo/

The instructions below assume that you have set up Anaconda, as described in the :doc:`Quick Start guide <../quick_start>` and describe the terminal commands necessary. If you are using GitHub Desktop, take a look through `their documentation`_ to understand the corresponding steps.

.. _their documentation: https://help.github.com/desktop/

Clone your fork of PyMeasure :code:`your-github-username/pymeasure`. In the following terminal commands replace your desired path and GitHub username.

.. code-block:: bash

    cd /path/for/code
    git clone https://github.com/your-github-username/pymeasure.git

If you had already installed PyMeasure using :code:`pip`, make sure to uninstall it before continuing.

.. code-block:: bash

    pip uninstall pymeasure

Install PyMeasure in the editable mode.

.. code-block:: bash

    cd /path/for/code/pymeasure
    pip install -e .

This will allow you to edit the files of PyMeasure and see the changes reflected. Make sure to reset your notebook kernel or Python console when doing so. Now you have your own copy of the development version of PyMeasure installed!

Working on a new feature
========================

We use branches in Git to allow multiple features to be worked on simultaneously, without causing conflicts. The master branch contains the stable development version. Instead of working on the master branch, you will create your own branch off the master and merge it back into the master when you are finished.

Create a new branch for your feature before editing the code. For example, if you want to add the new instrument "Extreme 5000" you will make a new branch "dev/extreme-5000".

.. code-block:: bash

    git branch dev/extreme-5000

You can also `make a new branch`_ on GitHub. If you do so, you will have to fetch these changes before the branch will show up on your local computer.

.. code-block:: bash

    git fetch

.. _make a new branch: https://help.github.com/articles/creating-and-deleting-branches-within-your-repository/

Once you have created the branch, change your current branch to match the new one.

.. code-block:: bash

    git checkout dev/extreme-5000

Now you are ready to write your new feature and make changes to the code. To ensure consistency, please follow the :doc:`coding standards for PyMeasure <coding_standards>`. Use :code:`git status` to check on the files that have been changed. As you go, commit your changes and push them to your fork.

.. code-block:: bash

    git add file-that-changed.py
    git commit -m "A short description about what changed"
    git push

Making a pull-request
=====================

While you are working, its helpful to start a pull-request (PR) on the :code:`master` branch of :code:`ralph-group/pymeasure`. This will allow you to discuss your feature with other contributors. We encourage you to start this pull-request after your first commit.

`Start a pull-request`_ on the `PyMeasure GitHub page`_.

.. _`Start a pull-request`: https://help.github.com/articles/using-pull-requests/
.. _PyMeasure GitHub page: https://github.com/ralph-group/pymeasure

Your pull-request will be merged by the PyMeasure maintainers once it meets the coding standards and passes unit tests. You will notice that your pull-request is automatically checked with the unit tests.

Unit testing
============

Unit tests are run each time a new commit is made to a branch. The purpose is to catch changes that break the current functionality, by testing each feature unit. PyMeasure relies on `py.test`_ to preform these tests, which are run on TravisCI and Appveyor for Linux/macOS and Windows respectively.

If your feature can be tested, writing tests are highly encouraged. This will ensure that your features keep working as new features are added.

.. _`py.test`: http://pytest.org/latest/

Now you are familiar with all the pieces of the PyMeasure development work-flow. We look forward to seeing your pull-request!